# ディレクトリ構成

> status: active

---

## ソリューション構成

```
FocusKeeper.sln
├── src/
│   └── FocusKeeper/                  # メインアプリプロジェクト（WPF）
└── tests/
    └── FocusKeeper.Tests/            # テストプロジェクト（xUnit）
```

---

## メインプロジェクト（`src/FocusKeeper/`）

```
FocusKeeper/
├── App.xaml                          # アプリケーション定義・グローバルリソース
├── App.xaml.cs                       # DI構築・起動処理
│
├── Assets/                           # 静的リソース
│   ├── Icons/                        # アプリアイコン（.ico, .png）
│   └── Themes/                       # テーマ用 ResourceDictionary
│       ├── Colors.xaml
│       ├── Styles.xaml
│       └── Templates.xaml
│
├── Models/                           # データモデル（ロジックなし）
│   ├── TaskItem.cs
│   ├── TaskHistory.cs
│   └── AppSettings.cs                # 設定クラス群（OverlaySettings等含む）
│
├── ViewModels/                       # ViewModel（CommunityToolkit.Mvvm）
│   ├── OverlayViewModel.cs           # オーバーレイウィンドウのVM
│   ├── SettingsViewModel.cs          # 設定ウィンドウのVM
│   ├── TaskSelectViewModel.cs        # 作業入力ダイアログのVM
│   └── TaskListViewModel.cs          # 作業リスト管理のVM（設定ウィンドウ内）
│
├── Views/                            # WPF ウィンドウ・ダイアログ
│   ├── OverlayWindow.xaml            # オーバーレイウィンドウ
│   ├── OverlayWindow.xaml.cs
│   ├── SettingsWindow.xaml           # 設定ウィンドウ
│   ├── SettingsWindow.xaml.cs
│   ├── TaskSelectDialog.xaml         # 作業入力ダイアログ
│   └── TaskSelectDialog.xaml.cs
│
├── Services/                         # ビジネスロジック
│   ├── Interfaces/
│   │   ├── ITaskService.cs
│   │   ├── ISettingsService.cs
│   │   └── IWindowMonitorService.cs
│   ├── TaskService.cs                # 作業の切り替え・履歴記録
│   ├── SettingsService.cs            # 設定の読み書き・適用
│   └── WindowMonitorService.cs       # アクティブウィンドウ監視
│
├── Repositories/                     # データアクセス層
│   ├── Interfaces/
│   │   ├── ITaskRepository.cs
│   │   └── ISettingsRepository.cs
│   ├── TaskRepository.cs
│   └── SettingsRepository.cs
│
└── Infrastructure/                   # インフラ・横断的関心事
    ├── Database/
    │   ├── DatabaseInitializer.cs    # DBマイグレーション・初期化
    │   └── DbConnectionFactory.cs   # SQLite接続ファクトリ
    ├── Logging/
    │   └── LoggingSetup.cs           # Serilogセットアップ
    ├── StartupManager.cs             # スタートアップ登録管理
    └── SingleInstanceGuard.cs        # 多重起動防止（Named Mutex）
```

---

## テストプロジェクト（`tests/FocusKeeper.Tests/`）

```
FocusKeeper.Tests/
├── Services/
│   ├── TaskServiceTests.cs
│   ├── SettingsServiceTests.cs
│   └── WindowMonitorServiceTests.cs
├── ViewModels/
│   ├── OverlayViewModelTests.cs
│   ├── SettingsViewModelTests.cs
│   └── TaskSelectViewModelTests.cs
├── Repositories/
│   ├── TaskRepositoryTests.cs
│   └── SettingsRepositoryTests.cs
└── Helpers/
    └── TestDbFactory.cs              # テスト用インメモリDB
```

---

## 配置ルール

| ルール | 内容 |
|--------|------|
| レイヤー対応 | ファイルは必ず対応するレイヤーフォルダに配置する |
| インターフェース | `Services/Interfaces/`, `Repositories/Interfaces/` に配置 |
| XAML | `Views/` に配置。コードビハインドはXAMLと同フォルダ |
| テスト | 本体と対称的なフォルダ構成（`Services/` → `Services/`） |
| アイコン | `Assets/Icons/` に配置。`FocusKeeper.ico` がメインアイコン |
| DBファイル | 実行時は `%LOCALAPPDATA%\FocusKeeper\` に配置（リポジトリには含めない） |
