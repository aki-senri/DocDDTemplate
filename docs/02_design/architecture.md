---
status: active
tracks:
  - src/FileTagExplorer/**/*.cs
---

# architecture.md — アーキテクチャ設計

## 全体構成

WPF アプリケーションとして MVVM パターンを採用する。
CommunityToolkit.Mvvm のソースジェネレーターを活用してボイラープレートを削減する。

```
┌────────────────────────────────────────────────────────┐
│                     Views (XAML)                       │
│  MainWindow.xaml / TagEditorDialog.xaml / ...          │
└────────────────────┬───────────────────────────────────┘
                     │ DataBinding / Commands
┌────────────────────▼───────────────────────────────────┐
│                   ViewModels                           │
│  MainViewModel / FileEntryViewModel / TagViewModel     │
└────────────────┬──────────────────┬────────────────────┘
                 │                  │
┌────────────────▼──┐  ┌────────────▼───────────────────┐
│     Services      │  │          Models                │
│  FileSystemService│  │  TagStore / FileEntry / Tag    │
│  TagStoreService  │  └────────────────────────────────┘
└────────────────┬──┘
                 │
┌────────────────▼───────────────────────────────────────┐
│                Infrastructure                         │
│  ITagRepository → JsonTagRepository (.filetags I/O)  │
└────────────────────────────────────────────────────────┘
```

## レイヤー定義

### Views（プレゼンテーション層）

- XAML + コードビハインド（最小限）
- ViewModel へのバインディングのみ担当
- ビジネスロジックを含まない

主要ファイル:
- `Views/MainWindow.xaml` — メインウィンドウ
- `Views/TagEditorDialog.xaml` — タグ作成・編集ダイアログ
- `Views/MoveConfirmDialog.xaml` — 移動確認ダイアログ

### ViewModels（アプリケーション層）

- `CommunityToolkit.Mvvm.ComponentModel.ObservableObject` を継承
- UI 状態の管理・コマンドの定義
- Service への委譲のみ行い、直接 I/O しない

主要クラス:
```
MainViewModel
├── ObservableCollection<FileEntryViewModel> Files
├── ObservableCollection<TagViewModel> Tags
├── ObservableCollection<TagViewModel> ActiveFilters
├── ICommand OpenFolderCommand
├── ICommand MoveSelectedFilesCommand
└── ICommand AddTagCommand

FileEntryViewModel
├── FileEntry Model（参照）
├── bool IsSelected
└── ObservableCollection<TagViewModel> AssignedTags

TagViewModel
├── Tag Model（参照）
└── bool IsFilterActive
```

### Services（ドメイン層）

ビジネスロジックを担当する。インターフェース経由で使用する。

```csharp
interface IFileSystemService
{
    IReadOnlyList<FileEntry> GetFiles(string folderPath);
    void MoveFiles(IEnumerable<string> filePaths, string destinationFolder);
    IReadOnlyList<string> GetSubFolders(string folderPath);
}

interface ITagStoreService
{
    TagStore Load(string folderPath);
    void Save(string folderPath, TagStore store);
    void AddTag(TagStore store, string fileName, string tagId);
    void RemoveTag(TagStore store, string fileName, string tagId);
}
```

### Models（ドメインモデル）

副作用のないデータ構造と値オブジェクト。詳細は `data_model.md` 参照。

### Infrastructure（インフラ層）

```csharp
interface ITagRepository
{
    TagStore Read(string folderPath);
    void Write(string folderPath, TagStore store);
}

class JsonTagRepository : ITagRepository { ... }
```

## 依存関係の方向

```
Views → ViewModels → Services → Models
                  → Infrastructure（ITagRepository）
```

循環依存は禁止。Infrastructure は Models に依存するが、ViewModels には依存しない。

## 依存性注入

`App.xaml.cs` で DI コンテナ（`Microsoft.Extensions.DependencyInjection`）を構成する。

```csharp
services.AddSingleton<ITagRepository, JsonTagRepository>();
services.AddSingleton<ITagStoreService, TagStoreService>();
services.AddSingleton<IFileSystemService, FileSystemService>();
services.AddTransient<MainViewModel>();
```

## プロジェクト構成

```
FileTagExplorer.sln
├── src/
│   └── FileTagExplorer/
│       ├── FileTagExplorer.csproj   (.NET 9 WPF)
│       ├── App.xaml / App.xaml.cs
│       ├── Models/
│       │   ├── FileEntry.cs
│       │   ├── Tag.cs
│       │   └── TagStore.cs
│       ├── ViewModels/
│       │   ├── MainViewModel.cs
│       │   ├── FileEntryViewModel.cs
│       │   └── TagViewModel.cs
│       ├── Views/
│       │   ├── MainWindow.xaml
│       │   ├── TagEditorDialog.xaml
│       │   └── MoveConfirmDialog.xaml
│       ├── Services/
│       │   ├── IFileSystemService.cs
│       │   ├── FileSystemService.cs
│       │   ├── ITagStoreService.cs
│       │   └── TagStoreService.cs
│       └── Infrastructure/
│           ├── ITagRepository.cs
│           └── JsonTagRepository.cs
└── tests/
    └── FileTagExplorer.Tests/
        ├── FileTagExplorer.Tests.csproj  (.NET 9 xUnit)
        ├── Services/
        │   ├── TagStoreServiceTests.cs
        │   └── FileSystemServiceTests.cs
        └── Infrastructure/
            └── JsonTagRepositoryTests.cs
```
