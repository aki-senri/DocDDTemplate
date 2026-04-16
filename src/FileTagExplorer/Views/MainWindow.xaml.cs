using FileTagExplorer.ViewModels;
using System.Windows;
using System.Windows.Controls;

namespace FileTagExplorer.Views;

public partial class MainWindow : Window
{
    public MainWindow(MainViewModel viewModel)
    {
        InitializeComponent();
        DataContext = viewModel;
    }

    /// <summary>タグチップの ✕ ボタンクリック → UnassignTagCommand を実行する。</summary>
    private void TagChipRemove_Click(object sender, RoutedEventArgs e)
    {
        if (sender is not Button btn) return;
        if (btn.Tag is not FileEntryViewModel fileVm) return;
        if (btn.DataContext is not TagViewModel tagVm) return;

        if (DataContext is MainViewModel vm)
            vm.UnassignTagCommand.Execute((fileVm, tagVm));
    }
}
