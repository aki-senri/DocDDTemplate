using System.IO;
using FileTagExplorer.Exceptions;
using FileTagExplorer.Models;

namespace FileTagExplorer.Services;

public sealed class FileSystemService : IFileSystemService
{
    private const string FileTagsFileName = ".filetags";

    public async IAsyncEnumerable<FileEntry> GetFilesAsync(
        string folderPath,
        [System.Runtime.CompilerServices.EnumeratorCancellation] CancellationToken ct = default)
    {
        // バックグラウンドスレッドで再帰走査
        await Task.Yield();

        IEnumerable<string> files;
        try
        {
            files = Directory.EnumerateFiles(folderPath, "*", SearchOption.AllDirectories);
        }
        catch (UnauthorizedAccessException ex)
        {
            throw new FolderAccessDeniedException(folderPath, ex);
        }
        catch (DirectoryNotFoundException)
        {
            yield break;
        }

        foreach (var fullPath in files)
        {
            ct.ThrowIfCancellationRequested();

            // .filetags 自身は除外 (INV-003)
            if (string.Equals(Path.GetFileName(fullPath), FileTagsFileName,
                    StringComparison.OrdinalIgnoreCase))
                continue;

            FileInfo info;
            try
            {
                info = new FileInfo(fullPath);
            }
            catch
            {
                continue; // アクセスできないファイルはスキップ
            }

            var relativePath = ToRelativePath(folderPath, fullPath);
            yield return new FileEntry(
                Name: info.Name,
                RelativePath: relativePath,
                FullPath: fullPath,
                Size: info.Length,
                LastModified: info.LastWriteTimeUtc);
        }
    }

    public FolderNode GetFolderTree(string folderPath)
    {
        return BuildNode(folderPath, "");
    }

    private static FolderNode BuildNode(string fullPath, string relativePath)
    {
        var children = new List<FolderNode>();
        try
        {
            foreach (var subDir in Directory.EnumerateDirectories(fullPath))
            {
                var name = Path.GetFileName(subDir);
                var childRelative = relativePath.Length == 0
                    ? name
                    : $"{relativePath}/{name}";
                children.Add(BuildNode(subDir, childRelative));
            }
        }
        catch (UnauthorizedAccessException) { /* アクセスできないフォルダはスキップ */ }

        return new FolderNode(
            Name: relativePath.Length == 0 ? Path.GetFileName(fullPath) : Path.GetFileName(fullPath),
            RelativePath: relativePath,
            FullPath: fullPath,
            Children: children);
    }

    public void MoveFile(string sourcePath, string destinationFolder, bool overwrite = false)
    {
        var fileName = Path.GetFileName(sourcePath);
        var destPath = Path.Combine(destinationFolder, fileName);
        File.Move(sourcePath, destPath, overwrite);
    }

    /// <summary>絶対パスをルートからの相対パス（'/' 区切り）に変換する。</summary>
    public static string ToRelativePath(string rootPath, string fullPath)
    {
        var relative = Path.GetRelativePath(rootPath, fullPath);
        return relative.Replace('\\', '/');
    }
}
