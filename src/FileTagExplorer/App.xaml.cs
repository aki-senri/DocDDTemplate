using FileTagExplorer.Infrastructure;
using FileTagExplorer.Services;
using FileTagExplorer.ViewModels;
using FileTagExplorer.Views;
using Microsoft.Extensions.DependencyInjection;
using System.Windows;

namespace FileTagExplorer;

public partial class App : Application
{
    private ServiceProvider? _serviceProvider;

    protected override void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);

        var services = new ServiceCollection();
        ConfigureServices(services);
        _serviceProvider = services.BuildServiceProvider();

        var mainWindow = _serviceProvider.GetRequiredService<MainWindow>();
        mainWindow.Show();
    }

    private static void ConfigureServices(IServiceCollection services)
    {
        services.AddSingleton<ITagRepository, JsonTagRepository>();
        services.AddSingleton<ITagStoreService, TagStoreService>();
        services.AddSingleton<IFileSystemService, FileSystemService>();
        services.AddSingleton<IDialogService, DialogService>();
        services.AddTransient<MainViewModel>();
        services.AddTransient<MainWindow>();
    }

    protected override void OnExit(ExitEventArgs e)
    {
        _serviceProvider?.Dispose();
        base.OnExit(e);
    }
}
