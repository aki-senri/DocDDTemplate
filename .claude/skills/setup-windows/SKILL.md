---
name: setup-windows
description: Define the development flow for a Windows WPF desktop app (.NET 8 / C# / CommunityToolkit.Mvvm). Interviews the user for project-specific details, then generates Phase 1 documents including architecture, coding standards, invariants, and directory structure.
disable-model-invocation: true
---

# セットアップスキル: Windows デスクトップアプリ（WPF / .NET 8 / C#）

> **実行タイミング**: `init-project.md` 実行後、Phase 1 開始時に実行する
>
> **目的**: このスキルを実行することで、Windows WPF アプリ開発に必要な
> 構成・設計・開発手順がドキュメントとして確定し、
> チームメンバーとAIエージェントが同じ前提で開発を進められる状態になる。

---

## 確定事項（このスキルが定める標準）

以下はプロジェクト固有の事情がない限り変更しない。
変更する場合は `docs/00_project/decisions.md` に理由を記録すること。

### 技術スタック

| 項目 | 採用技術 | 理由 |
|------|---------|------|
| 言語 | C# 12 | .NET 8 のデフォルト |
| ランタイム | .NET 8（Desktop Runtime） | LTS、2026年11月まで標準サポート |
| UI フレームワーク | WPF | オーバーレイ・最前面制御の実績が豊富。WinUI 3より成熟 |
| MVVM ライブラリ | CommunityToolkit.Mvvm 8.x | Microsoft公式、Source Generator でボイラープレートを最小化 |
| DI コンテナ | Microsoft.Extensions.DependencyInjection 8.x | .NET 標準、学習コスト低 |
| ローカル DB | Microsoft.Data.Sqlite 8.x | ローカル完結型アプリの標準。ORM不要な複雑度 |
| ロギング | Serilog 3.x + Serilog.Sinks.File | ファイルローテーション付きログ |
| テスト | xUnit 2.x + Moq 4.x | .NET 標準テストスタック |
| パッケージング | MSIX | Windows 10/11 標準。クリーンアンインストール保証 |
| CI | GitHub Actions（windows-latest） | MSBuild が使える環境 |

### アーキテクチャ

レイヤードアーキテクチャ + MVVM。**依存の方向は一方向のみ**。

```
View → ViewModel → Service → Repository → Model
```

| レイヤー | 責務 | 置き場所 |
|---------|------|---------|
| View | UI描画・入力受付のみ。ロジックなし | `Views/` |
| ViewModel | UI状態・コマンド定義。Service に委譲 | `ViewModels/` |
| Service | ビジネスロジック。Repository を通じてデータ操作 | `Services/` |
| Repository | DB アクセスの抽象化（インターフェース経由） | `Repositories/` |
| Model | データ構造定義のみ。ロジックなし | `Models/` |

### ディレクトリ構成

```
{APP_NAME}.sln
├── src/
│   └── {APP_NAME}/
│       ├── App.xaml / App.xaml.cs    # DI構築・起動処理
│       ├── Models/                   # データ構造
│       ├── ViewModels/               # MVVM ViewModel
│       ├── Views/                    # XAML ウィンドウ・ダイアログ
│       ├── Services/
│       │   └── Interfaces/           # サービスインターフェース
│       ├── Repositories/
│       │   └── Interfaces/           # リポジトリインターフェース
│       ├── Infrastructure/           # DI設定・DB初期化・ロギング
│       └── Assets/                   # アイコン・テーマ
└── tests/
    └── {APP_NAME}.Tests/             # xUnit テストプロジェクト
        ├── Services/
        ├── ViewModels/
        └── Repositories/
```

### 主要な不変条件

実装中は以下を守る。違反は Roslyn アナライザー + CI で自動検出する。

| # | 条件 | 違反時 |
|---|------|--------|
| INV-001 | View → ViewModel → Service → Repository → Model の依存方向のみ許可 | ビルドエラー |
| INV-002 | ViewModel はロジックを持たず Service に委譲する | ビルドエラー |
| INV-003 | `.xaml.cs` にビジネスロジックを書かない（50行超で警告） | 警告 |
| INV-004 | `.cs` 300行・`.xaml` 200行・`App.xaml.cs` 100行が上限 | 警告/エラー |
| INV-005 | `async void` は WPF イベントハンドラ以外禁止 | ビルドエラー |
| INV-006 | `private` フィールドは `_camelCase`、非同期メソッドは `Async` サフィックス | ビルド警告 |
| INV-007 | 外部ネットワーク通信禁止 | 警告 |
| INV-008 | 入力バリデーションは Service 層の入口で行う | レビュー指摘 |

### コーディング規約の要点

```csharp
// ViewModel: ObservableObject 継承 + Source Generator を使う
[ObservableProperty] private string _currentTask = string.Empty;
[RelayCommand] private async Task ChangeTaskAsync() { ... }

// 非同期: 常に CancellationToken を受け取る
public async Task<IEnumerable<TaskItem>> GetAllAsync(CancellationToken ct = default)

// private フィールド: _camelCase
private readonly ITaskService _taskService;
```

---

## インタビュー（プロジェクト固有）

エージェントは以下のみ確認する。技術スタックは確定事項のため聞かない。

| # | 質問 | 使用先 |
|---|------|--------|
| Q1 | アプリ名は？（PascalCase） | ソリューション名・名前空間・実行ファイル名 |
| Q2 | データを永続化しますか？（SQLite使用の有無） | `feat-sqlite` の有効化判断 |
| Q3 | インターネット接続が必要ですか？（通常は不要） | INV-007 の適用範囲確認 |
| Q4 | マルチウィンドウ構成ですか？（メインウィンドウ以外に何かある場合） | Views/ の初期構成確認 |

---

## 生成ドキュメント一覧

| ファイル | 内容 | Phase |
|---------|------|-------|
| `docs/02_design/architecture.md` | レイヤー図・DI構成・プロジェクト構成 | 1 |
| `docs/03_implementation/directory_structure.md` | ディレクトリ構成（Q1のアプリ名を反映） | 1 |
| `docs/03_implementation/coding_standards.md` | C# / WPF コーディング規約 | 1 |
| `docs/03_implementation/dependencies.md` | NuGetパッケージ一覧・バージョン管理方針 | 1 |
| `docs/03_implementation/invariants.md` | INV-001〜008（Roslyn 強制ルール） | 1 |
| `docs/03_implementation/patterns.md` | MVVM・Repository・DI の実装パターン | 1 |
| `CONTEXT.md` 追記 | 技術スタック・命名規則の大原則を更新 | 0→1 |

---

## 開発サイクル（このプロジェクトでの標準フロー）

```
1. exec-plans/active/ から作業を選ぶ
        ↓
2. docs/01_requirements/user_stories/windows.md で受け入れ条件を確認
        ↓
3. docs/03_implementation/invariants.md を確認（実装前に必読）
        ↓
4. feature/{issue-or-task-name} ブランチで実装
   └── View → ViewModel → Service → Repository の順に作成
        ↓
5. xUnit テストを追加（ViewModel・Service カバレッジ 80% 以上）
        ↓
6. docs/04_quality/review_checklist.md でセルフレビュー
        ↓
7. PR 作成 → レビュー → マージ
   └── CI（GitHub Actions）: dotnet build + dotnet test + Roslyn アナライザー
        ↓
8. exec-plans/active/ の進捗ログを更新
```

---

## 完了条件

- [ ] 上記「生成ドキュメント一覧」の全ファイルが作成されている
- [ ] `docs/06_ai_context/CONTEXT.md` の技術スタック・命名規則セクションが更新されている
- [ ] `CONTEXT.md` の現在フェーズが「Phase 2（要件定義・設計）」になっている
