namespace FileTagExplorer.Models;

/// <summary>管理対象フォルダ配下のファイル情報。読み取り専用。</summary>
public sealed record FileEntry(
    string Name,            // ファイル名（パスなし）
    string RelativePath,    // ルートからの相対パス（'/' 区切り）
    string FullPath,        // 絶対パス
    long Size,              // バイト単位
    DateTime LastModified   // UTC
);
