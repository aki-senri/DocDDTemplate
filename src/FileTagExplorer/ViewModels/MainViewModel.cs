using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using FileTagExplorer.Models;
using FileTagExplorer.Services;
using System.Collections.ObjectModel;
using System.Windows;

namespace FileTagExplorer.ViewModels;

public sealed partial class MainViewModel : ObservableObject
{
    private readonly IFileSystemService _fsService;
    private readonly ITagStoreService _tagService;
    private readonly IDialogService _dialogService;

    private TagStore _tagStore = new();
    private string _rootFolderPath = "";
    private CancellationTokenSource? _loadCts;

    // --- 表示用コレクション ---
    private readonly List<FileEntryViewModel> _allFiles = [];

    [ObservableProperty]
    private ObservableCollection<FileEntryViewModel> _filteredFiles = [];

    [ObservableProperty]
    private ObservableCollection<TagViewModel> _tags = [];

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(HasFolder))]
    private string _currentFolderPath = "";

    [ObservableProperty]
    private bool _isLoading;

    [ObservableProperty]
    private string _statusMessage = "フォルダを開いてください";

    [ObservableProperty]
    [NotifyPropertyChangedFor(nameof(MoveDestinationLabel))]
    [NotifyCanExecuteChangedFor(nameof(MoveSelectedFilesCommand))]
    private FolderNode? _selectedMoveDestination;

    public bool HasFolder => CurrentFolderPath.Length > 0;
    public string MoveDestinationLabel =>
        SelectedMoveDestination is null ? "（未選択）"
        : SelectedMoveDestination.RelativePath.Length == 0 ? "（ルート）"
        : SelectedMoveDestination.RelativePath;

    public int SelectedCount => _allFiles.Count(f => f.IsSelected);

    public MainViewModel(
        IFileSystemService fsService,
        ITagStoreService tagService,
        IDialogService dialogService)
    {
        _fsService = fsService;
        _tagService = tagService;
        _dialogService = dialogService;
    }

    // ─── フォルダを開く ───────────────────────────────────────────
    [RelayCommand]
    private async Task OpenFolderAsync()
    {
        var path = _dialogService.ShowFolderSelectDialog(
            CurrentFolderPath.Length > 0 ? CurrentFolderPath : null);
        if (path is null) return;

        await LoadFolderAsync(path);
    }

    private async Task LoadFolderAsync(string path)
    {
        _loadCts?.Cancel();
        _loadCts = new CancellationTokenSource();
        var ct = _loadCts.Token;

        IsLoading = true;
        StatusMessage = "読み込み中...";
        _allFiles.Clear();
        FilteredFiles.Clear();
        Tags.Clear();
        SelectedMoveDestination = null;

        try
        {
            CurrentFolderPath = path;
            _tagStore = _tagService.Load(path);

            // タグ一覧を構築
            foreach (var tag in _tagStore.Tags)
                Tags.Add(new TagViewModel(tag));

            // ファイルを非同期で読み込み
            await foreach (var entry in _fsService.GetFilesAsync(path, ct))
            {
                var tagIds = _tagStore.Files.TryGetValue(entry.RelativePath, out var ids)
                    ? ids : [];
                var assignedTags = Tags.Where(t => tagIds.Contains(t.Id)).ToList();
                var vm = new FileEntryViewModel(entry, assignedTags);
                vm.PropertyChanged += (_, e) =>
                {
                    if (e.PropertyName == nameof(FileEntryViewModel.IsSelected))
                        OnPropertyChanged(nameof(SelectedCount));
                };

                _allFiles.Add(vm);
                Application.Current.Dispatcher.Invoke(() => FilteredFiles.Add(vm));
            }

            ApplyFilter();
            StatusMessage = $"{_allFiles.Count} 件のファイル";
        }
        catch (OperationCanceledException) { }
        catch (Exceptions.FolderAccessDeniedException ex)
        {
            _dialogService.ShowError($"フォルダにアクセスできません:\n{ex.FolderPath}");
            StatusMessage = "エラー: アクセス拒否";
        }
        finally
        {
            IsLoading = false;
        }
    }

    // ─── タグフィルター ────────────────────────────────────────────
    [RelayCommand]
    private void ToggleFilter(TagViewModel tag)
    {
        tag.IsFilterActive = !tag.IsFilterActive;
        ApplyFilter();
    }

    [RelayCommand]
    private void ClearFilter()
    {
        foreach (var t in Tags) t.IsFilterActive = false;
        ApplyFilter();
    }

    private void ApplyFilter()
    {
        var activeIds = Tags.Where(t => t.IsFilterActive).Select(t => t.Id).ToHashSet();

        Application.Current.Dispatcher.Invoke(() =>
        {
            FilteredFiles.Clear();
            foreach (var f in _allFiles)
            {
                if (activeIds.Count == 0 || f.AssignedTags.Any(t => activeIds.Contains(t.Id)))
                    FilteredFiles.Add(f);
            }
        });

        var active = Tags.Count(t => t.IsFilterActive);
        StatusMessage = active == 0
            ? $"{FilteredFiles.Count} 件表示中（全 {_allFiles.Count} 件）"
            : $"{FilteredFiles.Count} 件表示中（{active} タグでフィルター中）";
    }

    // ─── タグ管理 ──────────────────────────────────────────────────
    [RelayCommand]
    private void AddTag()
    {
        var result = _dialogService.ShowTagEditorDialog();
        if (result is null) return;

        var (name, color) = result.Value;
        try
        {
            var tag = _tagService.CreateTag(_tagStore, name, color);
            _tagService.Save(CurrentFolderPath, _tagStore);
            Tags.Add(new TagViewModel(tag));
        }
        catch (Exceptions.DuplicateTagNameException)
        {
            _dialogService.ShowError($"タグ名「{name}」は既に使用されています。");
        }
    }

    [RelayCommand]
    private void DeleteTag(TagViewModel tagVm)
    {
        if (!_dialogService.ShowConfirm($"タグ「{tagVm.Name}」を削除しますか？\n全ファイルからも除去されます。"))
            return;

        _tagService.DeleteTag(_tagStore, tagVm.Id);
        _tagService.Save(CurrentFolderPath, _tagStore);

        Tags.Remove(tagVm);

        // 表示中のファイルからもタグを除去
        foreach (var file in _allFiles)
            file.AssignedTags.Remove(tagVm);

        ApplyFilter();
    }

    // ─── ファイルへのタグ付与/削除 ────────────────────────────────
    [RelayCommand]
    private void AssignTag((FileEntryViewModel File, TagViewModel Tag) args)
    {
        var (fileVm, tagVm) = args;
        if (fileVm.HasTag(tagVm.Id)) return;

        _tagService.AddTag(_tagStore, fileVm.RelativePath, tagVm.Id);
        _tagService.Save(CurrentFolderPath, _tagStore);
        fileVm.AssignedTags.Add(tagVm);
    }

    [RelayCommand]
    private void UnassignTag((FileEntryViewModel File, TagViewModel Tag) args)
    {
        var (fileVm, tagVm) = args;
        _tagService.RemoveTag(_tagStore, fileVm.RelativePath, tagVm.Id);
        _tagService.Save(CurrentFolderPath, _tagStore);
        fileVm.AssignedTags.Remove(tagVm);
    }

    // ─── 一括選択 ─────────────────────────────────────────────────
    [RelayCommand]
    private void SelectAllVisible(bool select)
    {
        foreach (var f in FilteredFiles)
            f.IsSelected = select;
        OnPropertyChanged(nameof(SelectedCount));
    }

    [RelayCommand]
    private void SelectByTag(TagViewModel tag)
    {
        foreach (var f in FilteredFiles)
            f.IsSelected = f.HasTag(tag.Id);
        OnPropertyChanged(nameof(SelectedCount));
    }

    // ─── 移動先選択 ───────────────────────────────────────────────
    [RelayCommand(CanExecute = nameof(HasFolder))]
    private void SelectMoveDestination()
    {
        var tree = _fsService.GetFolderTree(CurrentFolderPath);
        var selected = _dialogService.ShowFolderTreeDialog(tree);
        if (selected is not null)
            SelectedMoveDestination = selected;
    }

    // ─── 一括移動 ─────────────────────────────────────────────────
    private bool CanMoveSelectedFiles() =>
        SelectedMoveDestination is not null && SelectedCount > 0;

    [RelayCommand(CanExecute = nameof(CanMoveSelectedFiles))]
    private void MoveSelectedFiles()
    {
        var dest = SelectedMoveDestination!;
        var selected = _allFiles.Where(f => f.IsSelected).ToList();

        // 移動先スコープ検証 (INV-005)
        if (!dest.FullPath.StartsWith(CurrentFolderPath, StringComparison.OrdinalIgnoreCase))
        {
            _dialogService.ShowError("移動先は開いたフォルダの配下のみ指定できます。");
            return;
        }

        int succeeded = 0, failed = 0;
        foreach (var fileVm in selected)
        {
            if (string.Equals(fileVm.FullPath,
                    Path.Combine(dest.FullPath, fileVm.Name),
                    StringComparison.OrdinalIgnoreCase))
                continue; // 同じフォルダはスキップ

            var destFilePath = Path.Combine(dest.FullPath, fileVm.Name);
            if (File.Exists(destFilePath))
            {
                if (!_dialogService.ShowConfirm(
                    $"移動先に「{fileVm.Name}」が既に存在します。上書きしますか？"))
                    continue;
            }

            try
            {
                _fsService.MoveFile(fileVm.FullPath, dest.FullPath, overwrite: true);

                // TagStore のキーを更新 (INV-007)
                var newRelative = dest.RelativePath.Length == 0
                    ? fileVm.Name
                    : $"{dest.RelativePath}/{fileVm.Name}";
                _tagService.UpdateFileKey(_tagStore, fileVm.RelativePath, newRelative);

                succeeded++;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Move failed: {ex.Message}");
                failed++;
            }
        }

        _tagService.Save(CurrentFolderPath, _tagStore);

        if (failed > 0)
            _dialogService.ShowError($"{succeeded} 件移動完了。{failed} 件は失敗しました。");

        // フォルダを再読み込み
        _ = LoadFolderAsync(CurrentFolderPath);
    }
}
