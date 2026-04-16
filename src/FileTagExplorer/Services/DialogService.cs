using FileTagExplorer.Models;
using FileTagExplorer.Views;
using Microsoft.Win32;
using System.Windows;

namespace FileTagExplorer.Services;

public sealed class DialogService : IDialogService
{
    public string? ShowFolderSelectDialog(string? initialPath = null)
    {
        var dialog = new OpenFolderDialog
        {
            Title = "フォルダを選択してください",
        };
        if (initialPath != null)
            dialog.InitialDirectory = initialPath;

        return dialog.ShowDialog() == true ? dialog.FolderName : null;
    }

    public void ShowError(string message)
    {
        MessageBox.Show(message, "エラー", MessageBoxButton.OK, MessageBoxImage.Error);
    }

    public bool ShowConfirm(string message)
    {
        return MessageBox.Show(message, "確認",
            MessageBoxButton.YesNo, MessageBoxImage.Question) == MessageBoxResult.Yes;
    }

    public FolderNode? ShowFolderTreeDialog(FolderNode rootNode)
    {
        var dialog = new FolderTreeDialog(rootNode)
        {
            Owner = Application.Current.MainWindow,
        };
        return dialog.ShowDialog() == true ? dialog.SelectedFolder : null;
    }

    public (string Name, string Color)? ShowTagEditorDialog(
        string? initialName = null, string? initialColor = null)
    {
        var dialog = new TagEditorDialog(initialName, initialColor)
        {
            Owner = Application.Current.MainWindow,
        };
        if (dialog.ShowDialog() == true)
            return (dialog.TagName, dialog.TagColor);
        return null;
    }
}
