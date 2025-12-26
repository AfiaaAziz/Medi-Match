using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace HospitalSchedulerUI
{
    public partial class DiseasePrediction : UserControl
    {
        private List<CheckBox> symptomCheckboxes = new List<CheckBox>();
        private List<string> allSymptoms = new List<string>();

        public DiseasePrediction()
        {
            InitializeComponent();
            LoadSymptomsFromModel();
        }

        private void LoadSymptomsFromModel()
        {
            try
            {
                string projectRoot = GetProjectRoot();
                string symptomsFile = Path.Combine(projectRoot, "Backend", "PythonScripts", "symptom_columns.json");

                if (File.Exists(symptomsFile))
                {
                    string json = File.ReadAllText(symptomsFile);
                    allSymptoms = JsonConvert.DeserializeObject<List<string>>(json);
                    DisplaySymptoms(allSymptoms);
                }
                else
                {
                    ShowStatus("⚠️ Model not found. Please train the model first.", "#fff3cd", "#856404");
                }
            }
            catch (Exception ex)
            {
                ShowStatus($"❌ Error loading symptoms: {ex.Message}", "#f8d7da", "#721c24");
            }
        }

        private void DisplaySymptoms(List<string> symptomsToShow)
        {
            SymptomsPanel.Children.Clear();
            symptomCheckboxes.Clear();

            foreach (var symptom in symptomsToShow.OrderBy(s => s))
            {
                string displayName = FormatSymptomName(symptom);

                var checkbox = new CheckBox
                {
                    Content = displayName,
                    Tag = symptom,
                    Margin = new Thickness(8, 6, 8, 6),
                    FontSize = 13,
                    Padding = new Thickness(8, 5, 8, 5)
                };

                checkbox.Checked += Symptom_CheckedChanged;
                checkbox.Unchecked += Symptom_CheckedChanged;

                symptomCheckboxes.Add(checkbox);
                SymptomsPanel.Children.Add(checkbox);
            }
        }

        private string FormatSymptomName(string symptom)
        {
            return string.Join(" ", symptom.Split('_')
                .Select(word => char.ToUpper(word[0]) + word.Substring(1).ToLower()));
        }

        private void Symptom_CheckedChanged(object sender, RoutedEventArgs e)
        {
            UpdateSelectedCount();
        }

        private void UpdateSelectedCount()
        {
            int count = symptomCheckboxes.Count(cb => cb.IsChecked == true);
            txtSelectedCount.Text = $"{count} symptom{(count != 1 ? "s" : "")} selected";
        }

        private void btnClear_Click(object sender, RoutedEventArgs e)
        {
            foreach (var cb in symptomCheckboxes)
            {
                cb.IsChecked = false;
            }
            ResetResults();
        }

        private async void btnPredict_Click(object sender, RoutedEventArgs e)
        {
            var selectedSymptoms = symptomCheckboxes
                .Where(cb => cb.IsChecked == true)
                .Select(cb => cb.Tag.ToString())
                .ToList();

            if (selectedSymptoms.Count == 0)
            {
                ShowStatus("⚠️ Please select at least one symptom", "#fff3cd", "#856404");
                return;
            }

            btnPredict.IsEnabled = false;
            ShowStatus("🔄 AI is analyzing your symptoms...", "#d1ecf1", "#0c5460");

            try
            {
                var result = await PredictDisease(selectedSymptoms);

                if (result.ContainsKey("success") && (bool)result["success"])
                {
                    DisplayResults(result);
                    ShowStatus("✅ Analysis complete!", "#d4edda", "#155724");
                }
                else
                {
                    string error = result.ContainsKey("error") ? result["error"].ToString() : "Unknown error";
                    ShowStatus($"❌ {error}", "#f8d7da", "#721c24");
                }
            }
            catch (Exception ex)
            {
                ShowStatus($"❌ Prediction failed: {ex.Message}", "#f8d7da", "#721c24");
            }
            finally
            {
                btnPredict.IsEnabled = true;
            }
        }

        private void DisplayResults(Dictionary<string, object> result)
        {
            txtTopDisease.Text = result["top_disease"].ToString();

            double confidence = Convert.ToDouble(result["confidence"]);
            txtConfidence.Text = $"Confidence: {confidence:F1}%";

            txtSpecialist.Text = result["specialist"].ToString();
            txtDepartment.Text = result["department"].ToString();

            if (result.ContainsKey("other_predictions"))
            {
                var others = ((JArray)result["other_predictions"]).ToObject<List<Dictionary<string, object>>>();
                lstOtherDiseases.ItemsSource = others.Select(d =>
                    $"{d["disease"]} ({d["probability"]}%)").ToList();
            }
        }

        private void ResetResults()
        {
            txtTopDisease.Text = "Select symptoms to begin analysis";
            txtConfidence.Text = "Confidence: --%";
            txtSpecialist.Text = "--";
            txtDepartment.Text = "--";
            lstOtherDiseases.ItemsSource = null;
            ShowStatus("ℹ️ Select symptoms and click 'Analyze Disease'", "#d1ecf1", "#0c5460");
        }

        private void ShowStatus(string message, string bgColor, string textColor)
        {
            txtStatus.Text = message;
            statusBorder.Background = new SolidColorBrush((Color)ColorConverter.ConvertFromString(bgColor));
            txtStatus.Foreground = new SolidColorBrush((Color)ColorConverter.ConvertFromString(textColor));
        }

        private async System.Threading.Tasks.Task<Dictionary<string, object>> PredictDisease(List<string> symptoms)
        {
            string projectRoot = GetProjectRoot();
            string scriptPath = Path.Combine(projectRoot, "Backend", "PythonScripts", "disease_predictor.py");
            string inputFile = Path.Combine(projectRoot, "Backend", "PythonScripts", "disease_input.json");

            var inputData = new { symptoms = symptoms };
            File.WriteAllText(inputFile, JsonConvert.SerializeObject(inputData));

            var psi = new ProcessStartInfo
            {
                FileName = "python",
                Arguments = $"\"{scriptPath}\"",
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true
            };

            using (var process = Process.Start(psi))
            {
                string output = await process.StandardOutput.ReadToEndAsync();
                string error = await process.StandardError.ReadToEndAsync();

                process.WaitForExit();

                if (process.ExitCode != 0)
                    throw new Exception($"Python error: {error}");

                return JsonConvert.DeserializeObject<Dictionary<string, object>>(output);
            }
        }

        private string GetProjectRoot()
        {
            string exeDir = AppDomain.CurrentDomain.BaseDirectory;
            string projectRoot = exeDir;
            for (int i = 0; i < 3; i++)
            {
                var parent = Directory.GetParent(projectRoot);
                if (parent != null) projectRoot = parent.FullName;
            }
            return projectRoot;
        }
    }
}