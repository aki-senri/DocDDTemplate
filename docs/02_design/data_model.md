---
status: active
tracks:
  - src/FileTagExplorer/Models/**
  - src/FileTagExplorer/Infrastructure/JsonTagRepository.cs
---

# data_model.md — データモデル

## ドメインモデル図

```
┌─────────────┐       ┌────────────┐
│   TagStore  │       │    Tag     │
├─────────────┤  1..* ├────────────┤
│ Version: int│◄──────│ Id: string │
│ Tags: List  │       │ Name: str  │
│ Files: Dict │       │ Color: str │
└─────────────┘       └────────────┘
      │
      │ ファイル名 → タグIDリスト
      ▼
┌─────────────────────────────┐
│  files: { "name": [tagIds] }│
└─────────────────────────────┘

┌──────────────────┐
│   FileEntry      │
├──────────────────┤
│ Name: string     │
│ FullPath: string │
│ Size: long       │
│ LastModified: DT │
└──────────────────┘
```

## C# モデルクラス定義

### Tag

```csharp
/// <summary>タグの定義。不変オブジェクト。</summary>
public sealed record Tag(
    string Id,        // GUID 文字列（例: "a1b2c3d4-..."）
    string Name,      // 表示名（最大50文字）
    string Color      // CSS カラー文字列（例: "#FF5722"）
);
```

### TagStore

```csharp
/// <summary>フォルダのタグデータ全体。</summary>
public sealed class TagStore
{
    public int Version { get; init; } = 1;

    /// <summary>タグ定義リスト。Id でユニーク。</summary>
    public List<Tag> Tags { get; init; } = [];

    /// <summary>
    /// ファイル名とタグIDリストのマッピング。
    /// キー: ファイル名（パスなし）
    /// 値: 付与されているタグIDの集合
    /// </summary>
    public Dictionary<string, List<string>> Files { get; init; } = [];
}
```

### FileEntry

```csharp
/// <summary>管理対象フォルダの直下ファイル情報。読み取り専用。</summary>
public sealed record FileEntry(
    string Name,            // ファイル名（パスなし）
    string FullPath,        // 絶対パス
    long Size,              // バイト単位
    DateTime LastModified   // UTC
);
```

## 永続化スキーマ（.filetags JSON）

### スキーマ定義

```json
{
  "version": 1,
  "tags": [
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "name": "重要",
      "color": "#FF5722"
    },
    {
      "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
      "name": "WIP",
      "color": "#2196F3"
    }
  ],
  "files": {
    "report.pdf": ["a1b2c3d4-e5f6-7890-abcd-ef1234567890"],
    "draft.docx": ["b2c3d4e5-f6a7-8901-bcde-f12345678901"],
    "final.pdf": [
      "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "b2c3d4e5-f6a7-8901-bcde-f12345678901"
    ]
  }
}
```

### フィールド仕様

| フィールド       | 型           | 必須 | 説明                                       |
|----------------|--------------|------|-------------------------------------------|
| `version`      | integer      | ✅   | スキーマバージョン。現在は `1` のみ有効。     |
| `tags`         | Tag[]        | ✅   | タグ定義の配列。空配列可。                   |
| `tags[].id`    | string(GUID) | ✅   | タグの一意識別子。GUID 形式。               |
| `tags[].name`  | string       | ✅   | タグの表示名。1〜50文字。                   |
| `tags[].color` | string       | ✅   | CSS カラー文字列（`#RRGGBB` 形式）。        |
| `files`        | object       | ✅   | ファイル名→タグIDリストのマッピング。空オブジェクト可。 |
| `files.*`      | string[]     | —    | ファイルに付与されたタグIDの配列。            |

### バージョン管理ポリシー

- 後方互換が破れる変更時はバージョンを `2` に上げる
- バージョン不明・未来バージョンの `.filetags` を開いた場合はエラーを表示してロードしない

## データ整合性ルール

1. `files` のキーに存在するファイルが実際には存在しない場合、次回保存時にエントリを削除する（ゴミ掃除）
2. `files[fileName]` に含まれるタグIDが `tags` に存在しない場合、そのIDは無視する（孤立参照の許容）
3. タグを削除した場合、`files` 内の全エントリから該当タグIDを除去する

## 注意事項

- `.filetags` ファイルは書き込みの際に一時ファイル→アトミック置換（`File.Move`）で保存し、
  書き込み中断によるファイル破損を防ぐ
- ファイル名は大文字小文字を区別する（Windows NTFS はデフォルト大文字小文字非区別だが、
  キーは記録されたまま保持する）
