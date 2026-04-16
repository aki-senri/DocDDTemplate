namespace FileTagExplorer.Models;

/// <summary>タグの定義。不変オブジェクト。</summary>
public sealed record Tag(
    string Id,      // GUID 文字列
    string Name,    // 表示名（最大 50 文字）
    string Color    // CSS カラー文字列（例: "#FF5722"）
);
