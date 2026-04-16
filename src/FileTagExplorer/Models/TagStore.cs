namespace FileTagExplorer.Models;

/// <summary>開いたフォルダ全体のタグデータ。.filetags JSON に永続化する。</summary>
public sealed class TagStore
{
    public int Version { get; init; } = 1;

    /// <summary>タグ定義リスト。Id でユニーク。</summary>
    public List<Tag> Tags { get; init; } = [];

    /// <summary>
    /// 相対パス → タグIDリストのマッピング。
    /// キー: ルートからの相対パス（'/' 区切り、例: "subdir/file.txt"）
    /// </summary>
    public Dictionary<string, List<string>> Files { get; init; } = [];
}
