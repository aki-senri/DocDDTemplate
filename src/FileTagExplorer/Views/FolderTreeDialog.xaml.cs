using FileTagExplorer.Models;
using FileTagExplorer.ViewModels;
using System.Windows;
using System.Windows.Controls;

namespace FileTagExplorer.Views;

public partial class FolderTreeDialog : Window
{
    public FolderNode? SelectedFolder { get; private set; }

    private FolderNodeViewModel? _selectedVm;

    public FolderTreeDialog(FolderNode rootNode)
    {
        InitializeComponent();
        // ルートノードを1要素のリストとして渡す
        DataContext = new[] { new FolderNodeViewModel(rootNode) };
    }

    private void FolderTree_SelectedItemChanged(object sender, RoutedPropertyChangedEventArgs<object> e)
    {
        _selectedVm = e.NewValue as FolderNodeViewModel;
    }

    private void OkButton_Click(object sender, RoutedEventArgs e)
    {
        if (_selectedVm is null)
        {
            MessageBox.Show("フォルダを選択してください。", "選択なし",
                MessageBoxButton.OK, MessageBoxImage.Warning);
            return;
        }
        SelectedFolder = _selectedVm.Model;
        DialogResult = true;
        Close();
    }

    private void CancelButton_Click(object sender, RoutedEventArgs e)
    {
        DialogResult = false;
        Close();
    }
}
