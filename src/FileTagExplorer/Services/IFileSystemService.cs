using FileTagExplorer.Models;

namespace FileTagExplorer.Services;

public interface IFileSystemService
{
    /// <summary>folderPath 配下を再帰的に走査して全ファイルを非同期列挙する。</summary>
    IAsyncEnumerable<FileEntry> GetFilesAsync(string folderPath, CancellationToken ct = default);

    /// <summary>folderPath 配下のフォルダツリーを返す（ルートノード含む）。</summary>
    FolderNode GetFolderTree(string folderPath);

    /// <summary>指定ファイルを destinationFolder へ移動する。</summary>
    void MoveFile(string sourcePath, string destinationFolder, bool overwrite = false);
}
