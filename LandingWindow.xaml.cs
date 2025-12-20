using System;
using System.Windows;

namespace HospitalSchedulerUI
{
    public partial class LandingWindow : Window
    {
        public LandingWindow()
        {
            InitializeComponent();
        }

        private void BtnSchedule_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                var main = new MainWindow();

                // Ensure scheduler view is shown after the window has finished loading
                main.Loaded += (s, args) =>
                {
                    try
                    {
                       
                        main.Show();
                        this.Close();
                        //main.ShowScheduler();
                        main.Activate();
                    }
                    catch { }
                };

                main.Show();
                this.Close();
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Failed to open scheduler: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }
    }
}