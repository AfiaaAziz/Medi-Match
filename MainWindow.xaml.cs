using HospitalSchedulerUI;
using Newtonsoft.Json;
using System;
using System.Globalization;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media.Imaging;

namespace HospitalSchedulerUI
{
    public partial class MainWindow : Window
    {
        // Store doctor and patient UI elements
        private List<DoctorUI> doctorUIs = new List<DoctorUI>();
        private List<PatientUI> patientUIs = new List<PatientUI>();

        // Arrays for dropdowns
        private string[] specialties = { "Cardiology", "Neurology", "Orthopedics", "Pediatrics", "General", "Emergency" };
        private string[] diseases = { "Heart Attack", "Stroke", "Fracture", "Fever", "Migraine", "Broken Arm",
                                      "Appendicitis", "Pneumonia", "Diabetes", "Hypertension" };

        // UI helper classes
        public class DoctorUI
        {
            public StackPanel Panel { get; set; }
            public TextBox NameBox { get; set; }
            public ComboBox SpecialtyCombo { get; set; }
        }

        public class PatientUI
        {
            public StackPanel Panel { get; set; }
            public TextBox NameBox { get; set; }
            public ComboBox DiseaseCombo { get; set; }
            public TextBox AgeBox { get; set; }
            public TextBlock UrgencyText { get; set; }
        }

        public MainWindow()
        {
            InitializeComponent();
            UpdateDoctorFields();
            UpdatePatientFields();

            // Listen to changes
            TxtDoctors.TextChanged += (s, e) => UpdateDoctorFields();
            TxtPatients.TextChanged += (s, e) => UpdatePatientFields();
            TxtUrgency.TextChanged += (s, e) => UpdatePatientFields();

            // Show home by default
            ShowHome();

            // Load triage control into host so navigation shows same navbar
            try
            {
                var triage = new EmergencyTriage();
                var contentHost = this.FindName("TriageHost") as ContentControl;
                if (contentHost != null)
                {
                    contentHost.Content = triage;
                }
            }
            catch { }
        }

        // NAVIGATION HELPERS
        private void ShowHome()
        {
            HomePanel.Visibility = Visibility.Visible;
            SchedulerPanel.Visibility = Visibility.Collapsed;
            ScheduleGrid.Visibility = Visibility.Collapsed;
            GraphPanel.Visibility = Visibility.Collapsed;
            // hide embedded triage control when showing other pages
            try { var triagePanel = this.FindName("TriagePanel") as Border; if (triagePanel != null) triagePanel.Visibility = Visibility.Collapsed; } catch { }
        }



        // made public so other windows can navigate to scheduler view
        public void ShowScheduler()
        {
            HomePanel.Visibility = Visibility.Collapsed;
            SchedulerPanel.Visibility = Visibility.Visible;
            ScheduleGrid.Visibility = Visibility.Collapsed;
            GraphPanel.Visibility = Visibility.Collapsed;
            try { var triagePanel = this.FindName("TriagePanel") as Border; if (triagePanel != null) triagePanel.Visibility = Visibility.Collapsed; } catch { }
        }

        private void ShowSchedule()
        {
            HomePanel.Visibility = Visibility.Collapsed;
            SchedulerPanel.Visibility = Visibility.Collapsed;
            ScheduleGrid.Visibility = Visibility.Visible;
            GraphPanel.Visibility = Visibility.Collapsed;
            try { var triagePanel = this.FindName("TriagePanel") as Border; if (triagePanel != null) triagePanel.Visibility = Visibility.Collapsed; } catch { }
        }

        private void ShowGraph()
        {
            HomePanel.Visibility = Visibility.Collapsed;
            SchedulerPanel.Visibility = Visibility.Collapsed;
            ScheduleGrid.Visibility = Visibility.Collapsed;
            GraphPanel.Visibility = Visibility.Visible;
            try { var triagePanel = this.FindName("TriagePanel") as Border; if (triagePanel != null) triagePanel.Visibility = Visibility.Collapsed; } catch { }
        }

        private void NavHome_Click(object sender, RoutedEventArgs e)
        {
            ShowHome();
        }

        private void NavScheduler_Click(object sender, RoutedEventArgs e)
        {
            ShowScheduler();
        }

        private void NavSchedule_Click(object sender, RoutedEventArgs e)
        {
            ShowSchedule();
        }

        private void NavEmergency_Click(object sender, RoutedEventArgs e)
        {
            // Show embedded triage user control inside main window
            try
            {
                var triagePanel = this.FindName("TriagePanel") as Border;
                if (triagePanel != null)
                {
                    HomePanel.Visibility = Visibility.Collapsed;
                    SchedulerPanel.Visibility = Visibility.Collapsed;
                    ScheduleGrid.Visibility = Visibility.Collapsed;
                    GraphPanel.Visibility = Visibility.Collapsed;

                    triagePanel.Visibility = Visibility.Visible;
                }
            }
            catch { }
        }

        private void NavGraph_Click(object sender, RoutedEventArgs e)
        {
            ShowGraph();
        }

        // ========== DOCTOR FIELDS ==========
        private void UpdateDoctorFields()
        {
            if (!int.TryParse(TxtDoctors.Text, out int doctorCount))
                doctorCount = 3;

            if (doctorCount <= 0)
                doctorCount = 3;

            DoctorPanel.Children.Clear();
            doctorUIs.Clear();

            for (int i = 1; i <= doctorCount; i++)
            {
                var doctorUI = new DoctorUI();

                // Create panel
                var stackPanel = new StackPanel
                {
                    Margin = new Thickness(10),
                    Width = 250,
                    VerticalAlignment = VerticalAlignment.Top
                };

                // Header
                var header = new TextBlock
                {
                    Text = $"Doctor {i}",
                    FontWeight = FontWeights.Bold,
                    Margin = new Thickness(0, 0, 0, 5)
                };

                // Name label
                var nameLabel = new TextBlock
                {
                    Text = "Name:",
                    Margin = new Thickness(0, 0, 0, 2)
                };

                // Name input
                var nameBox = new TextBox
                {
                    Text = string.Empty,
                    Margin = new Thickness(0, 0, 0, 5),
                    Padding = new Thickness(5)
                };

                // Specialty label
                var specialtyLabel = new TextBlock
                {
                    Text = "Specialty:",
                    Margin = new Thickness(0, 0, 0, 2)
                };

                // Specialty dropdown
                var specialtyCombo = new ComboBox
                {
                    ItemsSource = specialties,
                    //SelectedIndex = (i - 1) % specialties.Length,
                    Margin = new Thickness(0, 0, 0, 5),
                    Padding = new Thickness(5)
                };
                // Ensure no default selection
                specialtyCombo.SelectedIndex = -1;

                // Add to panel
                stackPanel.Children.Add(header);
                stackPanel.Children.Add(nameLabel);
                stackPanel.Children.Add(nameBox);
                stackPanel.Children.Add(specialtyLabel);
                stackPanel.Children.Add(specialtyCombo);

                // Add to UI collection
                doctorUI.Panel = stackPanel;
                doctorUI.NameBox = nameBox;
                doctorUI.SpecialtyCombo = specialtyCombo;
                doctorUIs.Add(doctorUI);

                // Add to UI
                DoctorPanel.Children.Add(stackPanel);
            }
        }

        // ========== PATIENT FIELDS ==========
        private void UpdatePatientFields()
        {
            int patientCount;
            if (!int.TryParse(TxtPatients.Text, out patientCount))
                patientCount = 6;

            if (patientCount <= 0)
                patientCount = 6;

            // Get urgency values
            var urgencies = new List<int>();
            if (!string.IsNullOrEmpty(TxtUrgency.Text))
            {
                foreach (var s in TxtUrgency.Text.Split(','))
                {
                    if (int.TryParse(s.Trim(), out int u) && u >= 1 && u <= 10)
                        urgencies.Add(u);
                }
            }
            while (urgencies.Count < patientCount)
                urgencies.Add(5);
            urgencies = urgencies.Take(patientCount).ToList();

            PatientPanel.Children.Clear();
            patientUIs.Clear();

            for (int i = 1; i <= patientCount; i++)
            {
                var patientUI = new PatientUI();

                // Create panel
                var stackPanel = new StackPanel
                {
                    Margin = new Thickness(10),
                    Width = 250,
                    VerticalAlignment = VerticalAlignment.Top
                };

                // Header with urgency
                var header = new TextBlock
                {
                    Text = $"Patient {i} (Urgency: {urgencies[i - 1]})",
                    FontWeight = FontWeights.Bold,
                    Margin = new Thickness(0, 0, 0, 5)
                };

                // Name label
                var nameLabel = new TextBlock
                {
                    Text = "Name:",
                    Margin = new Thickness(0, 0, 0, 2)
                };

                // Name input
                var nameBox = new TextBox
                {
                    Text = string.Empty,
                    Margin = new Thickness(0, 0, 0, 5),
                    Padding = new Thickness(5)
                };

                // Disease label
                var diseaseLabel = new TextBlock
                {
                    Text = "Disease/Condition:",
                    Margin = new Thickness(0, 0, 0, 2)
                };

                // Disease dropdown
                var diseaseCombo = new ComboBox
                {
                    ItemsSource = diseases,
                    //SelectedIndex = (i - 1) % diseases.Length,
                    Margin = new Thickness(0, 0, 0, 5),
                    Padding = new Thickness(5)
                };
                diseaseCombo.SelectedIndex = -1;

                // Age label
                var ageLabel = new TextBlock
                {
                    Text = "Age:",
                    Margin = new Thickness(0, 0, 0, 2)
                };

                // Age input
                var ageBox = new TextBox
                {
                    Text = string.Empty,
                    //Text = $"{20 + (i * 5)}",
                    Margin = new Thickness(0, 0, 0, 5),
                    Padding = new Thickness(5)
                };

                // Urgency display
                var urgencyText = new TextBlock
                {
                    Text = $"Urgency Level: {urgencies[i - 1]}",
                    FontWeight = FontWeights.SemiBold,
                    Foreground = urgencies[i - 1] >= 8 ? System.Windows.Media.Brushes.Red :
                                urgencies[i - 1] >= 5 ? System.Windows.Media.Brushes.Orange :
                                System.Windows.Media.Brushes.Green
                };

                // Add to panel
                stackPanel.Children.Add(header);
                stackPanel.Children.Add(nameLabel);
                stackPanel.Children.Add(nameBox);
                stackPanel.Children.Add(diseaseLabel);
                stackPanel.Children.Add(diseaseCombo);
                stackPanel.Children.Add(ageLabel);
                stackPanel.Children.Add(ageBox);
                stackPanel.Children.Add(urgencyText);

                // Add to UI collection
                patientUI.Panel = stackPanel;
                patientUI.NameBox = nameBox;
                patientUI.DiseaseCombo = diseaseCombo;
                patientUI.AgeBox = ageBox;
                patientUI.UrgencyText = urgencyText;
                patientUIs.Add(patientUI);

                // Add to UI
                PatientPanel.Children.Add(stackPanel);
            }
        }

        // ========== VALIDATION METHODS ==========
        private bool ValidateInputs()
        {
            // Check if any doctor fields are empty
            List<string> doctorErrors = new List<string>();
            for (int i = 0; i < doctorUIs.Count; i++)
            {
                var doctor = doctorUIs[i];
                string name = doctor.NameBox.Text.Trim();
                string specialty = doctor.SpecialtyCombo.SelectedValue?.ToString();

                if (string.IsNullOrEmpty(name))
                    doctorErrors.Add($"Doctor {i + 1}: Name is required");

                if (string.IsNullOrEmpty(specialty))
                    doctorErrors.Add($"Doctor {i + 1}: Specialty must be selected");
            }

            // Check if any patient fields are empty
            List<string> patientErrors = new List<string>();
            for (int i = 0; i < patientUIs.Count; i++)
            {
                var patient = patientUIs[i];
                string name = patient.NameBox.Text.Trim();
                string disease = patient.DiseaseCombo.SelectedValue?.ToString();
                string ageText = patient.AgeBox.Text.Trim();

                if (string.IsNullOrEmpty(name))
                    patientErrors.Add($"Patient {i + 1}: Name is required");

                if (string.IsNullOrEmpty(disease))
                    patientErrors.Add($"Patient {i + 1}: Disease/Condition must be selected");

                if (string.IsNullOrEmpty(ageText))
                    patientErrors.Add($"Patient {i + 1}: Age is required");
                else if (!int.TryParse(ageText, out int age) || age <= 0 || age > 120)
                    patientErrors.Add($"Patient {i + 1}: Age must be a valid number between 1 and 120");
            }

            // Check urgency values
            List<string> urgencyErrors = new List<string>();
            if (!string.IsNullOrEmpty(TxtUrgency.Text))
            {
                var urgencyStrings = TxtUrgency.Text.Split(',');
                for (int i = 0; i < urgencyStrings.Length; i++)
                {
                    string urgencyStr = urgencyStrings[i].Trim();
                    if (!int.TryParse(urgencyStr, out int urgency) || urgency < 1 || urgency > 10)
                        urgencyErrors.Add($"Urgency value #{i + 1}: '{urgencyStr}' must be a number between 1-10");
                }
            }

            // Collect all errors
            List<string> allErrors = new List<string>();
            allErrors.AddRange(doctorErrors);
            allErrors.AddRange(patientErrors);
            allErrors.AddRange(urgencyErrors);

            // If no errors, return true
            if (allErrors.Count == 0)
                return true;

            // Show error message
            string errorMessage = "Please fix the following errors:\n\n";
            if (doctorErrors.Count > 0)
            {
                errorMessage += "Doctor Errors:\n";
                errorMessage += string.Join("\n", doctorErrors) + "\n\n";
            }
            if (patientErrors.Count > 0)
            {
                errorMessage += "Patient Errors:\n";
                errorMessage += string.Join("\n", patientErrors) + "\n\n";
            }
            if (urgencyErrors.Count > 0)
            {
                errorMessage += "Urgency Errors:\n";
                errorMessage += string.Join("\n", urgencyErrors);
            }

            MessageBox.Show(errorMessage, "Validation Error", MessageBoxButton.OK, MessageBoxImage.Warning);
            return false;
        }

        // ========== MAIN SCHEDULING FUNCTION ==========
        private async void RunScheduler_Click(object sender, RoutedEventArgs e)
        {
            // Validate inputs first
            if (!ValidateInputs())
                return;

            Button btn = sender as Button;
            btn.IsEnabled = false;
            btn.Content = "AI RUNNING... PLEASE WAIT";

            try
            {
                // Clear previous data
                ScheduleGrid.ItemsSource = null;
                MetricsTable.ItemsSource = null;

                // 1. GET BASIC COUNTS
                int doctors = 3, patients = 6, beds = 4;
                int.TryParse(TxtDoctors.Text, out doctors);
                int.TryParse(TxtPatients.Text, out patients);
                int.TryParse(TxtBeds.Text, out beds);

                // 2. GET URGENCY VALUES
                var urgencies = new List<int>();
                if (!string.IsNullOrEmpty(TxtUrgency.Text))
                {
                    foreach (var s in TxtUrgency.Text.Split(','))
                    {
                        if (int.TryParse(s.Trim(), out int u) && u >= 1 && u <= 10)
                            urgencies.Add(u);
                    }
                }
                while (urgencies.Count < patients)
                    urgencies.Add(5);
                urgencies = urgencies.Take(patients).ToList();

                // 3. COLLECT DOCTOR DETAILS
                var doctorList = new List<object>();
                foreach (var doctorUI in doctorUIs)
                {
                    if (doctorUI != null && doctorUI.NameBox != null && doctorUI.SpecialtyCombo != null)
                    {
                        doctorList.Add(new
                        {
                            Name = doctorUI.NameBox.Text,
                            Specialty = doctorUI.SpecialtyCombo.SelectedValue?.ToString() ?? "General"
                        });
                    }
                }

                // 4. COLLECT PATIENT DETAILS
                var patientList = new List<object>();
                for (int i = 0; i < Math.Min(patientUIs.Count, patients); i++)
                {
                    var patientUI = patientUIs[i];
                    if (patientUI != null && patientUI.NameBox != null && patientUI.DiseaseCombo != null && patientUI.AgeBox != null)
                    {
                        int age;
                        if (!int.TryParse(patientUI.AgeBox.Text, out age))
                            age = 30;

                        patientList.Add(new
                        {
                            Name = patientUI.NameBox.Text,
                            Disease = patientUI.DiseaseCombo.SelectedValue?.ToString() ?? "Fever",
                            Age = age,
                            Urgency = urgencies[i]
                        });
                    }
                }

                // 5. CREATE INPUT JSON
                string exeDir = AppDomain.CurrentDomain.BaseDirectory;
                string projectRoot = exeDir;
                for (int i = 0; i < 3; i++)
                {
                    var parent = Directory.GetParent(projectRoot);
                    if (parent != null)
                        projectRoot = parent.FullName;
                }

                string inputFile = Path.Combine(projectRoot, "Backend", "PythonScripts", "input.json");
                string script = Path.Combine(projectRoot, "Backend", "PythonScripts", "scheduler.py");
                string resultsFolder = Path.Combine(projectRoot, "Results");

                Directory.CreateDirectory(Path.GetDirectoryName(inputFile));
                Directory.CreateDirectory(resultsFolder);

                // Enhanced input data
                var inputData = new
                {
                    Doctors = doctors,
                    Patients = patients,
                    Beds = beds,
                    Urgency = urgencies,
                    DoctorDetails = doctorList,
                    PatientDetails = patientList
                };

                // Add algorithm selection
                bool useGA = false;
                try
                {
                    useGA = (CmbAlgorithm.SelectedIndex == 1);
                }
                catch { }

                // Create a dictionary to include UseGA flag
                var inputDict = new Dictionary<string, object>(JsonConvert.DeserializeObject<Dictionary<string, object>>(JsonConvert.SerializeObject(inputData)));
                inputDict["UseGA"] = useGA;
                // Add GA hyperparameters if selected
                if (useGA)
                {
                    int pop = 80;
                    int gens = 120;
                    double mut = 0.06;
                    int? seed = null;
                    try { pop = int.Parse(TxtGAPopulation.Text); } catch { }
                    try { gens = int.Parse(TxtGAGenerations.Text); } catch { }
                    try
                    {
                        // normalize mutation input to 0..1, accept either '0.06' or '6' meaning 6%
                        var raw = TxtGAMutation.Text.Trim();
                        if (!string.IsNullOrEmpty(raw))
                        {
                            // try parse with invariant culture
                            double parsed = double.Parse(raw, CultureInfo.InvariantCulture);
                            if (parsed > 1.0)
                            {
                                // interpret >1 as percentage (e.g. 6 => 0.06)
                                mut = Math.Min(1.0, parsed / 100.0);
                            }
                            else if (parsed < 0.0)
                            {
                                // negative -> fallback
                                mut = 0.06;
                            }
                            else
                            {
                                mut = parsed;
                            }
                        }
                    }
                    catch { mut = 0.06; }
                    try { if (!string.IsNullOrEmpty(TxtGASeed.Text)) seed = int.Parse(TxtGASeed.Text); } catch { }

                    inputDict["GAPopulation"] = pop;
                    inputDict["GAGenerations"] = gens;
                    inputDict["GAMutation"] = mut;
                    if (seed.HasValue) inputDict["GASeed"] = seed.Value;
                }

                File.WriteAllText(inputFile, JsonConvert.SerializeObject(inputDict, Formatting.Indented));

                // 6. RUN PYTHON SCRIPT
                bool pythonSuccess = await RunPythonScriptAsync(script);

                if (!pythonSuccess)
                {
                    MessageBox.Show("Python script failed to run.", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
                    return;
                }

                // 7. LOAD RESULTS
                await LoadResultsAsync(resultsFolder);

                // Show schedule panel after loading
                ShowSchedule();

                MessageBox.Show($"AI Scheduling Complete!\n\nDoctors: {doctors}\nPatients: {patients}\nSpecialty-based matching applied.",
                              "Success", MessageBoxButton.OK, MessageBoxImage.Information);
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error: {ex.Message}", "Failed", MessageBoxButton.OK, MessageBoxImage.Error);
            }
            finally
            {
                btn.IsEnabled = true;
                btn.Content = "RUN AI SCHEDULER";
            }
        }

        private async Task<bool> RunPythonScriptAsync(string scriptPath)
        {
            return await Task.Run(() =>
            {
                try
                {
                    ProcessStartInfo psi = new ProcessStartInfo
                    {
                        FileName = "python",
                        Arguments = $"\"{scriptPath}\"",
                        UseShellExecute = false,
                        RedirectStandardOutput = true,
                        RedirectStandardError = true,
                        CreateNoWindow = true
                    };

                    using (Process process = new Process())
                    {
                        process.StartInfo = psi;
                        process.Start();

                        string output = process.StandardOutput.ReadToEnd();
                        string error = process.StandardError.ReadToEnd();

                        process.WaitForExit(60000);

                        return output.Contains("SUCCESS") || process.ExitCode == 0;
                    }
                }
                catch
                {
                    return false;
                }
            });
        }

        private async Task LoadResultsAsync(string resultsFolder)
        {
            await Task.Delay(500);

            // LOAD SCHEDULE DATA
            string jsonPath = Path.Combine(resultsFolder, "output.json");
            if (File.Exists(jsonPath))
            {
                try
                {
                    string jsonContent = File.ReadAllText(jsonPath);
                    var scheduleData = JsonConvert.DeserializeObject<List<Dictionary<string, object>>>(jsonContent)
                        .Select(x => new
                        {
                            Patient = x.ContainsKey("Patient") ? x["Patient"] : 0,
                            PatientName = x.ContainsKey("PatientName") ? x["PatientName"] : "",
                            Disease = x.ContainsKey("Disease") ? x["Disease"] : "",
                            Doctor = x.ContainsKey("Doctor") ? x["Doctor"] : 0,
                            DoctorName = x.ContainsKey("DoctorName") ? x["DoctorName"] : "",
                            Specialty = x.ContainsKey("Specialty") ? x["Specialty"] : "",
                            SpecialtyMatch = x.ContainsKey("SpecialtyMatch") ? x["SpecialtyMatch"] : "",
                            Urgency = x.ContainsKey("Urgency") ? Convert.ToDouble(x["Urgency"]) : 0.0,
                            FuzzyScore = x.ContainsKey("FuzzyScore") ? Math.Round(Convert.ToDouble(x["FuzzyScore"]), 3) : 0.0,
                            Bed = x.ContainsKey("Bed") ? x["Bed"] : 0
                        })
                        .OrderByDescending(item => item.Urgency) // descending: higher urgency first
                        .ToList();

                    ScheduleGrid.ItemsSource = scheduleData;
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Error loading schedule: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
                }
            }

            // LOAD CONVERGENCE GRAPH
            string imgPath = Path.Combine(resultsFolder, "convergence.png");
            if (File.Exists(imgPath))
            {
                try
                {
                    BitmapImage bitmap = new BitmapImage();
                    bitmap.BeginInit();
                    bitmap.CacheOption = BitmapCacheOption.OnLoad;
                    bitmap.UriSource = new Uri(imgPath);
                    bitmap.EndInit();
                    ConvergenceChart.Source = bitmap;
                }
                catch { }
            }

            // LOAD METRICS
            string metricsPath = Path.Combine(resultsFolder, "metrics.csv");
            if (File.Exists(metricsPath))
            {
                try
                {
                    var metricsData = new List<KeyValuePair<string, string>>();
                    var lines = File.ReadAllLines(metricsPath);

                    for (int i = 1; i < lines.Length; i++)
                    {
                        var line = lines[i];
                        if (!string.IsNullOrEmpty(line))
                        {
                            var parts = line.Split(',');
                            if (parts.Length >= 2)
                            {
                                metricsData.Add(new KeyValuePair<string, string>(
                                    parts[0].Trim(),
                                    parts[1].Trim()
                                ));
                            }
                        }
                    }

                    MetricsTable.ItemsSource = metricsData;
                }
                catch { }
            }
        }

        private void BtnReadMore_Click(object sender, RoutedEventArgs e)
        {
            var about = new AboutWindow();
            about.Owner = this;
            about.ShowDialog();
        }
    }
}