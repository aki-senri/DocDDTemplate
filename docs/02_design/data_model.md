# データモデル

> status: active

---

## エンティティ一覧

### TaskItem（作業）

ユーザーが登録した作業リストの各エントリ。

| カラム | 型 | 制約 | 説明 |
|--------|-----|------|------|
| `Id` | INTEGER | PRIMARY KEY AUTOINCREMENT | 内部ID |
| `Title` | TEXT | NOT NULL, UNIQUE, MAX 100文字 | 作業名 |
| `CreatedAt` | TEXT | NOT NULL | 登録日時（ISO 8601 UTC） |
| `LastUsedAt` | TEXT | NULL | 最終使用日時（未使用時はNULL） |
| `UseCount` | INTEGER | NOT NULL DEFAULT 0 | 使用回数 |
| `IsDeleted` | INTEGER | NOT NULL DEFAULT 0 | 論理削除フラグ（0=有効, 1=削除済） |

**インデックス**
- `idx_task_title`: `Title`（検索・重複チェック用）
- `idx_task_last_used`: `LastUsedAt DESC`（最終使用順ソート用）

---

### TaskHistory（作業履歴）

実際に「現在の作業」として設定した記録。作業リストとは独立して管理。

| カラム | 型 | 制約 | 説明 |
|--------|-----|------|------|
| `Id` | INTEGER | PRIMARY KEY AUTOINCREMENT | 内部ID |
| `Title` | TEXT | NOT NULL | 作業名（スナップショット） |
| `StartedAt` | TEXT | NOT NULL | 作業開始日時（ISO 8601 UTC） |
| `EndedAt` | TEXT | NULL | 作業終了日時（NULL=進行中または未記録） |

---

### AppSettings（アプリ設定）

Key-Value 形式で設定値を保存。スキーマ変更なしに設定項目を追加できる。

| カラム | 型 | 制約 | 説明 |
|--------|-----|------|------|
| `Key` | TEXT | PRIMARY KEY | 設定キー |
| `Value` | TEXT | NOT NULL | 設定値（JSON文字列またはスカラー値） |
| `UpdatedAt` | TEXT | NOT NULL | 最終更新日時（ISO 8601 UTC） |

**設定キー一覧**

| Key | 型 | デフォルト | 説明 |
|-----|-----|-----------|------|
| `overlay.position.x` | int | 100 | オーバーレイX座標 |
| `overlay.position.y` | int | 100 | オーバーレイY座標 |
| `overlay.width` | int | 400 | オーバーレイ幅（px） |
| `overlay.opacity` | int | 80 | 背景透明度（%） |
| `overlay.fontsize` | int | 16 | フォントサイズ（pt） |
| `overlay.forecolor` | string | #FFFFFF | 文字色 |
| `overlay.backcolor` | string | #1A1A2E | 背景色 |
| `overlay.monitor` | int | 0 | 表示モニターインデックス |
| `app.startup` | bool | false | スタートアップ起動 |
| `app.tray` | bool | true | タスクトレイ常駐 |
| `monitor.enabled` | bool | false | アクティブウィンドウ監視 |
| `monitor.allowlist` | string[] | [] | 許可アプリ名リスト（JSON配列） |
| `monitor.alertcolor` | string | #FF4444 | アラートカラー |

---

## C# モデルクラス

```csharp
// Models/TaskItem.cs
public class TaskItem
{
    public int Id { get; set; }
    public string Title { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; }
    public DateTime? LastUsedAt { get; set; }
    public int UseCount { get; set; }
    public bool IsDeleted { get; set; }
}

// Models/TaskHistory.cs
public class TaskHistory
{
    public int Id { get; set; }
    public string Title { get; set; } = string.Empty;
    public DateTime StartedAt { get; set; }
    public DateTime? EndedAt { get; set; }
}

// Models/AppSettings.cs
public class AppSettings
{
    public OverlaySettings Overlay { get; set; } = new();
    public AppBehaviorSettings App { get; set; } = new();
    public MonitorSettings Monitor { get; set; } = new();
}

public class OverlaySettings
{
    public int X { get; set; } = 100;
    public int Y { get; set; } = 100;
    public int Width { get; set; } = 400;
    public int Opacity { get; set; } = 80;
    public int FontSize { get; set; } = 16;
    public string ForeColor { get; set; } = "#FFFFFF";
    public string BackColor { get; set; } = "#1A1A2E";
    public int Monitor { get; set; } = 0;
}

public class AppBehaviorSettings
{
    public bool Startup { get; set; } = false;
    public bool Tray { get; set; } = true;
}

public class MonitorSettings
{
    public bool Enabled { get; set; } = false;
    public List<string> AllowList { get; set; } = new();
    public string AlertColor { get; set; } = "#FF4444";
}
```

---

## DDL

```sql
CREATE TABLE IF NOT EXISTS task_items (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT    NOT NULL UNIQUE CHECK(length(title) <= 100),
    created_at  TEXT    NOT NULL,
    last_used_at TEXT,
    use_count   INTEGER NOT NULL DEFAULT 0,
    is_deleted  INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_task_title    ON task_items(title);
CREATE INDEX IF NOT EXISTS idx_task_last_used ON task_items(last_used_at DESC);

CREATE TABLE IF NOT EXISTS task_history (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    title      TEXT    NOT NULL,
    started_at TEXT    NOT NULL,
    ended_at   TEXT
);

CREATE TABLE IF NOT EXISTS app_settings (
    key        TEXT PRIMARY KEY,
    value      TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```
