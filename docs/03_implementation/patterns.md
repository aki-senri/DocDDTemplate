---
status: active
tracks:
  - src/FileTagExplorer/**/*.cs
---

# patterns.md — 実装パターン集

## PATTERN-001: MVVM バインディング（CommunityToolkit.Mvvm）

CommunityToolkit.Mvvm のソースジェネレーターを使用してボイラープレートを削減する。

```csharp
// ViewModel の基本形
[ObservableObject]  // ← INotifyPropertyChanged を自動生成
public partial class FileEntryViewModel
{
    [ObservableProperty]  // ← IsSelected プロパティ + SetProperty() を自動生成
    private bool _isSelected;

    [ObservableProperty]
    private ObservableCollection<TagViewModel> _assignedTags = [];

    // コマンドは RelayCommand 属性で定義
    [RelayCommand]
    private void RemoveTag(TagViewModel tag)
    {
        AssignedTags.Remove(tag);
        // ...
    }
}
```

**ルール:**
- ViewModel は `partial class` として定義する（ソースジェネレーター要件）
- バッキングフィールドは `_camelCase`（アンダースコア+小文字始まり）

---

## PATTERN-002: Repository パターン（TagStore の永続化）

`ITagRepository` インターフェースを通じてのみ `.filetags` にアクセスする。
テスト時はモックに差し替え可能にする。

```csharp
public interface ITagRepository
{
    TagStore Read(string folderPath);
    void Write(string folderPath, TagStore store);
}

public sealed class JsonTagRepository : ITagRepository
{
    private static readonly JsonSerializerOptions _options = new()
    {
        WriteIndented = true,
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
    };

    private static string GetFilePath(string folderPath) =>
        Path.Combine(folderPath, ".filetags");

    public TagStore Read(string folderPath)
    {
        var path = GetFilePath(folderPath);
        if (!File.Exists(path))
            return new TagStore();

        var json = File.ReadAllText(path);
        var store = JsonSerializer.Deserialize<TagStore>(json, _options)
            ?? throw new InvalidOperationException(".filetags のデシリアライズ失敗");

        if (store.Version != 1)
            throw new UnsupportedVersionException(store.Version);

        return store;
    }

    public void Write(string folderPath, TagStore store)
    {
        var targetPath = GetFilePath(folderPath);
        var tmpPath = Path.GetTempFileName();
        try
        {
            var json = JsonSerializer.Serialize(store, _options);
            File.WriteAllText(tmpPath, json);
            File.Move(tmpPath, targetPath, overwrite: true);  // アトミック置換
        }
        finally
        {
            if (File.Exists(tmpPath)) File.Delete(tmpPath);
        }
    }
}
```

---

## PATTERN-003: サービス層のエラーハンドリング

サービス層は `IOException` / `UnauthorizedAccessException` を catch し、
ドメイン例外として再スローする。ViewModel で UI フィードバックに変換する。

```csharp
// Services/FileSystemService.cs
public IReadOnlyList<FileEntry> GetFiles(string folderPath)
{
    try
    {
        return Directory.GetFiles(folderPath)
            .Where(f => Path.GetFileName(f) != ".filetags")
            .Select(f => new FileEntry(
                Name: Path.GetFileName(f),
                FullPath: f,
                Size: new FileInfo(f).Length,
                LastModified: File.GetLastWriteTimeUtc(f)))
            .ToList();
    }
    catch (UnauthorizedAccessException ex)
    {
        throw new FolderAccessDeniedException(folderPath, ex);
    }
    catch (DirectoryNotFoundException ex)
    {
        throw new FolderNotFoundException(folderPath, ex);
    }
}
```

```csharp
// ViewModels/MainViewModel.cs
[RelayCommand]
private async Task OpenFolderAsync(string? folderPath)
{
    try
    {
        var files = _fileSystemService.GetFiles(folderPath!);
        Files = new ObservableCollection<FileEntryViewModel>(
            files.Select(f => new FileEntryViewModel(f)));
    }
    catch (FolderAccessDeniedException ex)
    {
        await _dialogService.ShowErrorAsync(
            $"フォルダにアクセスできません:\n{ex.FolderPath}");
    }
}
```

---

## PATTERN-004: タグフィルター（OR 条件）

フィルターアクティブなタグがある場合のみ絞り込みを適用する。

```csharp
// MainViewModel.cs 内
private IEnumerable<FileEntryViewModel> ApplyFilter(
    IEnumerable<FileEntryViewModel> files)
{
    var activeFilterIds = Tags
        .Where(t => t.IsFilterActive)
        .Select(t => t.Id)
        .ToHashSet();

    if (activeFilterIds.Count == 0)
        return files;

    // OR 条件: いずれかのフィルタータグを持つファイルを返す
    return files.Where(f =>
        f.AssignedTags.Any(t => activeFilterIds.Contains(t.Id)));
}
```

---

## PATTERN-005: 一括移動後の .filetags クリーンアップ

ファイル移動後、`TagStore` の `files` セクションから移動したファイルのエントリを削除する。

```csharp
public void CleanUpMovedFiles(
    TagStore store,
    IEnumerable<string> movedFileNames)
{
    foreach (var name in movedFileNames)
    {
        store.Files.Remove(name);
    }
}
```

**注意:** 移動先フォルダへのタグ引き継ぎは行わない（ADR-001 参照）。

---

## PATTERN-006: xUnit テストの構造（AC-ID トレーサビリティ）

```csharp
public class TagStoreServiceTests
{
    [Fact]
    [Trait("AC", "AC-006")]  // ← 受け入れ条件 ID を必ず付与
    public void CreateTag_WithDuplicateName_ThrowsException()
    {
        // Arrange
        var store = new TagStore();
        var service = new TagStoreService(Mock.Of<ITagRepository>());
        service.AddTagToStore(store, new Tag("id1", "重要", "#FF0000"));

        // Act & Assert
        Assert.Throws<DuplicateTagNameException>(
            () => service.AddTagToStore(store, new Tag("id2", "重要", "#0000FF")));
    }
}
```
