namespace FileTagExplorer.Models;

/// <summary>フォルダツリーの1ノード（移動先選択・ツリー表示用）。</summary>
public sealed record FolderNode(
    string Name,
    string RelativePath,    // ルートからの相対パス（"" = ルート自身）
    string FullPath,
    IReadOnlyList<FolderNode> Children
);
