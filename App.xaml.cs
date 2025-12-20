using System.Windows;

namespace HospitalSchedulerUI
{
    public partial class App : Application
    {
        protected override void OnStartup(StartupEventArgs e)
        {
            base.OnStartup(e);
            var landing = new LandingWindow();
            landing.Show();
        }
    }
}
