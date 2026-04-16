---
id: exec-plan-001
title: プロジェクト初期セットアップ（M1: フォルダ参照 + ファイル一覧表示）
status: pending
created: 2026-04-16
branch: feature/001-initial-setup
milestone: M1
---

# exec-plan-001 — プロジェクト初期セットアップ

## 目標

.NET 9 WPF プロジェクトのソリューション構成を作成し、
フォルダを開いてファイル一覧を表示するところ（M1）まで実装する。

## スコープ

- ソリューション・プロジェクトファイルの作成
- MVVM 基本構造（MainViewModel / FileEntryViewModel）の実装
- `FileSystemService` の実装（GetFiles）
- `JsonTagRepository` の骨格実装（Read/Write）
- MainWindow UI の実装（フォルダ選択 + ファイル一覧表示）
- xUnit テストプロジェクトのセットアップ

## スコープ外（次のフェーズ以降）

- タグ付与・削除・フィルター（M2）
- 一括選択・移動（M3）
- タグ管理 UI（M4）

## 受け入れ条件

| ID     | 内容                                                                           | テスト |
|--------|--------------------------------------------------------------------------------|--------|
| AC-001 | 「フォルダを開く」ボタンでダイアログが開き、フォルダを選択できる                 | 手動   |
| AC-002 | ファイル一覧にファイル名・サイズ・更新日時が表示される                           | 手動   |
| AC-003 | `.filetags` ファイルが一覧に表示されない                                         | 自動   |
| AC-004 | 読み取り権限エラー時にエラーダイアログが表示される                               | 自動   |

## タスク一覧

### Phase A: プロジェクト構成

- [ ] A-1: ソリューションファイル作成（`FileTagExplorer.sln`）
- [ ] A-2: WPF プロジェクト作成（`src/FileTagExplorer/FileTagExplorer.csproj`）
  - TargetFramework: `net9.0-windows`
  - UseWPF: `true`
  - NuGet: `CommunityToolkit.Mvvm`、`Microsoft.Extensions.DependencyInjection`
- [ ] A-3: テストプロジェクト作成（`tests/FileTagExplorer.Tests/FileTagExplorer.Tests.csproj`）
  - NuGet: `xunit`、`FluentAssertions`、`Moq`
- [ ] A-4: DI セットアップ（`App.xaml.cs`）

### Phase B: モデル・インフラ実装

- [ ] B-1: `Models/FileEntry.cs`（record）
- [ ] B-2: `Models/Tag.cs`（record）
- [ ] B-3: `Models/TagStore.cs`（class）
- [ ] B-4: `Infrastructure/ITagRepository.cs`（interface）
- [ ] B-5: `Infrastructure/JsonTagRepository.cs`（Read/Write 実装）

### Phase C: サービス実装

- [ ] C-1: `Services/IFileSystemService.cs`
- [ ] C-2: `Services/FileSystemService.cs`（GetFiles + GetSubFolders）
  - `.filetags` を除外する
  - `UnauthorizedAccessException` を `FolderAccessDeniedException` に変換
- [ ] C-3: `Services/ITagStoreService.cs`
- [ ] C-4: `Services/TagStoreService.cs`（骨格のみ、タグ操作は M2 で実装）

### Phase D: ViewModel 実装

- [ ] D-1: `ViewModels/FileEntryViewModel.cs`
  - `ObservableProperty`: `IsSelected`, `AssignedTags`
- [ ] D-2: `ViewModels/MainViewModel.cs`
  - `ObservableProperty`: `Files`, `CurrentFolderPath`, `StatusMessage`
  - `RelayCommand`: `OpenFolderCommand`

### Phase E: View 実装

- [ ] E-1: `Views/MainWindow.xaml`
  - ツールバー（「フォルダを開く」ボタン、現在のフォルダパス表示）
  - DataGrid（ファイル名・サイズ・更新日時・タグ列）
  - ステータスバー（X 件表示中）
- [ ] E-2: フォルダ選択ダイアログ（`FolderBrowserDialog`）の組み込み

### Phase F: テスト実装

- [ ] F-1: `FileSystemServiceTests.cs`
  - `GetFiles_ExcludesFiletagsFile` [AC-003]
  - `GetFiles_ThrowsFolderAccessDenied_OnUnauthorizedAccess` [AC-004]
- [ ] F-2: `JsonTagRepositoryTests.cs`
  - `Read_ReturnsEmptyStore_WhenFileNotExists`
  - `Write_CreatesFileAtomically`（一時ファイル経由を確認）

## 完了条件

- [ ] `dotnet build` がエラーなしで通る
- [ ] `dotnet test` で全テストがグリーン（AC-003, AC-004）
- [ ] 手動確認: フォルダを開いてファイル一覧が正しく表示される（AC-001, AC-002）
- [ ] 手動確認: `.filetags` ファイルが一覧に現れない

## 参照ドキュメント

- `docs/02_design/architecture.md`
- `docs/02_design/data_model.md`
- `docs/03_implementation/invariants.md`（INV-003, INV-004 を優先確認）
- `docs/03_implementation/patterns.md`（PATTERN-001〜003）
