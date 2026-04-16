namespace FileTagExplorer.Exceptions;

public sealed class FolderAccessDeniedException(string folderPath, Exception? inner = null)
    : Exception($"フォルダにアクセスできません: {folderPath}", inner)
{
    public string FolderPath { get; } = folderPath;
}
