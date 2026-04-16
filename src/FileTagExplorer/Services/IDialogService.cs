using FileTagExplorer.Models;

namespace FileTagExplorer.Services;

public interface IDialogService
{
    /// <summary>フォルダ選択ダイアログを表示する。キャンセルされた場合は null を返す。</summary>
    string? ShowFolderSelectDialog(string? initialPath = null);

    /// <summary>エラーダイアログを表示する。</summary>
    void ShowError(string message);

    /// <summary>確認ダイアログを表示する。OK なら true を返す。</summary>
    bool ShowConfirm(string message);

    /// <summary>フォルダツリーから移動先フォルダを選択するダイアログを表示する。</summary>
    FolderNode? ShowFolderTreeDialog(FolderNode rootNode);

    /// <summary>タグ作成/編集ダイアログを表示する。キャンセルなら null を返す。</summary>
    (string Name, string Color)? ShowTagEditorDialog(
        string? initialName = null, string? initialColor = null);
}
