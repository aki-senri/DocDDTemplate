# アーキテクチャ設計

> status: active

---

## システム全体構成

FocusKeeper は単一プロセスで動作するWindowsデスクトップアプリです。  
外部サーバー・クラウド依存はなく、すべてローカルで完結します。

```
┌─────────────────────────────────────────────────┐
│                   FocusKeeper.exe                │
│                                                  │
│  ┌──────────┐  ┌──────────────┐  ┌───────────┐  │
│  │ Overlay  │  │  Settings    │  │  Tray     │  │
│  │ Window   │  │  Window      │  │  Icon     │  │
│  └────┬─────┘  └──────┬───────┘  └─────┬─────┘  │
│       │               │                │         │
│  ─────────────── ViewModels ──────────────────   │
│  ┌────────────┐  ┌────────────┐  ┌──────────┐   │
│  │ OverlayVM  │  │ SettingsVM │  │  TaskVM  │   │
│  └─────┬──────┘  └─────┬──────┘  └────┬─────┘   │
│        │               │              │          │
│  ─────────────── Services ──────────────────     │
│  ┌─────────────┐  ┌──────────────┐               │
│  │ TaskService │  │SettingsService│               │
│  └──────┬──────┘  └──────┬───────┘               │
│         │                │                       │
│  ─────────── Repositories ──────────             │
│  ┌──────────────┐  ┌──────────────────┐          │
│  │ TaskRepository│  │SettingsRepository│          │
│  └──────┬───────┘  └──────┬───────────┘          │
│         │                 │                      │
│  ─────────────── SQLite DB ─────────────         │
│         focuskeeper.db                           │
└─────────────────────────────────────────────────┘

外部依存：
  Windows API（SetForegroundWindow, GetForegroundWindow）
  WinRT（タスクトレイ通知）
```

---

## レイヤー構成

### 依存方向の原則

```
View → ViewModel → Service → Repository → Model
```

逆方向の依存は禁止（invariants.mdで強制）。

### 各レイヤーの責務

| レイヤー | 責務 | 例 |
|----------|------|-----|
| **View** | UI描画・ユーザー入力受付。ロジックを持たない | `OverlayWindow.xaml`, `SettingsWindow.xaml` |
| **ViewModel** | ViewとServiceの橋渡し。UI状態管理・コマンド定義 | `OverlayViewModel`, `SettingsViewModel` |
| **Service** | ビジネスロジック。作業の切り替え・監視制御など | `TaskService`, `WindowMonitorService` |
| **Repository** | データアクセス抽象化。SQLiteとの入出力 | `TaskRepository`, `SettingsRepository` |
| **Model** | データ構造定義。ロジックなし | `TaskItem`, `AppSettings` |

---

## プロジェクト構成

```
FocusKeeper.sln
├── FocusKeeper/                  # メインプロジェクト（WPF）
│   ├── App.xaml
│   ├── App.xaml.cs
│   ├── Models/
│   ├── ViewModels/
│   ├── Views/
│   ├── Services/
│   ├── Repositories/
│   ├── Infrastructure/           # DI設定・ロギング等
│   └── Assets/                   # アイコン・リソース
└── FocusKeeper.Tests/            # テストプロジェクト（xUnit）
```

---

## 依存性注入（DI）

`Microsoft.Extensions.DependencyInjection` を使用します。  
`App.xaml.cs` でコンテナを構築し、ViewModel・Service・Repositoryを登録します。

```csharp
// 登録例
services.AddSingleton<ISettingsRepository, SettingsRepository>();
services.AddSingleton<ITaskRepository, TaskRepository>();
services.AddSingleton<ISettingsService, SettingsService>();
services.AddTransient<ITaskService, TaskService>();
services.AddTransient<OverlayViewModel>();
services.AddTransient<SettingsViewModel>();
```

---

## オーバーレイウィンドウ実装方針

- `WindowStyle = None`, `AllowsTransparency = True`, `Background = Transparent`
- `Topmost = True` で最前面固定
- `IsHitTestVisible = False` でクリックスルーを実現（ただし右クリックメニュー用に条件付きで変更）
- `ShowInTaskbar = False` でタスクバー非表示

---

## データ永続化

- DBファイル: `%LOCALAPPDATA%\FocusKeeper\focuskeeper.db`
- マイグレーション: 起動時に `EnsureCreated` + 手動DDL管理
- 設定: DBの `settings` テーブルに Key-Value 形式で保存

---

## Windows API 利用

| API | 用途 | 名前空間 |
|-----|------|----------|
| `GetForegroundWindow` | アクティブウィンドウ取得 | `user32.dll` |
| `GetWindowText` | ウィンドウタイトル取得 | `user32.dll` |
| `RegisterStartupApp` | スタートアップ登録（タスクスケジューラ or レジストリ） | WinRT / Registry |

---

## ロギング

- `Microsoft.Extensions.Logging` + `Serilog` を使用
- ログレベル: DEBUG（開発）/ INFO（本番）
- 出力先: `%LOCALAPPDATA%\FocusKeeper\Logs\focuskeeper-YYYYMMDD.log`
- 日次ローテーション、7日分保持
