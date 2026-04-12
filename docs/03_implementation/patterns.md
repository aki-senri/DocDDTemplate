# デザインパターン・実装慣習

> status: active

---

## 採用パターン一覧

| パターン | 用途 | 採用箇所 |
|----------|------|----------|
| MVVM | UI / ビジネスロジック分離 | View / ViewModel / Service 全体 |
| Repository | データアクセス抽象化 | `*Repository` クラス |
| Dependency Injection | 依存関係管理・テスタビリティ | App.xaml.cs のコンテナ構築 |
| Observer（INotifyPropertyChanged） | UI変更通知 | ViewModel（CommunityToolkit.Mvvm） |
| Command（ICommand） | UIアクションのバインディング | `[RelayCommand]` |
| Factory | DBコネクション生成 | `DbConnectionFactory` |
| Singleton | 設定・監視サービス（プロセス内唯一） | `ISettingsService`, `IWindowMonitorService` |

---

## MVVM パターンの実装

### ViewModel の基本形

```csharp
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

public partial class OverlayViewModel : ObservableObject
{
    private readonly ITaskService _taskService;
    private readonly ISettingsService _settingsService;

    public OverlayViewModel(ITaskService taskService, ISettingsService settingsService)
    {
        _taskService = taskService;
        _settingsService = settingsService;
    }

    [ObservableProperty]
    private string _currentTaskTitle = "作業未設定";

    [ObservableProperty]
    private bool _isAlertMode;

    [RelayCommand]
    private async Task ChangeTaskAsync()
    {
        // 作業変更ダイアログを開く
    }

    [RelayCommand]
    private async Task CompleteTaskAsync()
    {
        await _taskService.CompleteCurrentTaskAsync();
        CurrentTaskTitle = "作業未設定";
    }
}
```

### View からのバインディング

```xml
<!-- OverlayWindow.xaml -->
<Window.DataContext>
    <!-- DIコンテナから解決されるため、デザイン時専用 -->
    <d:DesignInstance Type="vm:OverlayViewModel" IsDesignTimeCreatable="False"/>
</Window.DataContext>

<TextBlock Text="{Binding CurrentTaskTitle}"
           FontSize="{Binding OverlaySettings.FontSize}"
           Foreground="{Binding ForeColorBrush}"/>

<Button Content="作業変更"
        Command="{Binding ChangeTaskCommand}"/>
```

---

## Repository パターンの実装

```csharp
// インターフェース定義（Services層はこれに依存）
public interface ITaskRepository
{
    Task<IEnumerable<TaskItem>> GetAllAsync(CancellationToken ct = default);
    Task<IEnumerable<TaskItem>> SearchAsync(string keyword, CancellationToken ct = default);
    Task<TaskItem> AddAsync(TaskItem item, CancellationToken ct = default);
    Task UpdateAsync(TaskItem item, CancellationToken ct = default);
    Task DeleteAsync(int id, CancellationToken ct = default);
}

// 実装（SQLite）
public class TaskRepository : ITaskRepository
{
    private readonly DbConnectionFactory _connectionFactory;
    private readonly ILogger<TaskRepository> _logger;

    public TaskRepository(DbConnectionFactory connectionFactory, ILogger<TaskRepository> logger)
    {
        _connectionFactory = connectionFactory;
        _logger = logger;
    }

    public async Task<IEnumerable<TaskItem>> GetAllAsync(CancellationToken ct = default)
    {
        await using var conn = _connectionFactory.Create();
        // SQLite クエリ実行
    }
}
```

---

## 設定の変更通知パターン

設定変更がオーバーレイに即座に反映されるよう、`ISettingsService` は変更イベントを発行します。

```csharp
public interface ISettingsService
{
    AppSettings Current { get; }
    event EventHandler<SettingsChangedEventArgs> SettingsChanged;
    Task SaveAsync(AppSettings settings);
}

// OverlayViewModel での購読
public OverlayViewModel(ISettingsService settingsService)
{
    settingsService.SettingsChanged += OnSettingsChanged;
}

private void OnSettingsChanged(object? sender, SettingsChangedEventArgs e)
{
    // オーバーレイのスタイルを更新
    OnPropertyChanged(nameof(ForeColorBrush));
    OnPropertyChanged(nameof(BackColorBrush));
}
```

---

## ウィンドウ管理パターン

ViewModel からウィンドウを直接操作せず、`WindowService` を経由します。

```csharp
public interface IWindowService
{
    void ShowSettingsWindow();
    bool? ShowTaskSelectDialog(out string? selectedTask);
    void ShowOverlay();
    void HideOverlay();
}
```

---

## 多重起動防止

```csharp
// Infrastructure/SingleInstanceGuard.cs
public class SingleInstanceGuard : IDisposable
{
    private readonly Mutex _mutex;

    public SingleInstanceGuard(string appName)
    {
        _mutex = new Mutex(true, $"Global\\{appName}", out var createdNew);
        IsFirstInstance = createdNew;
    }

    public bool IsFirstInstance { get; }

    public void Dispose() => _mutex.Dispose();
}

// App.xaml.cs
protected override void OnStartup(StartupEventArgs e)
{
    _guard = new SingleInstanceGuard("FocusKeeper");
    if (!_guard.IsFirstInstance)
    {
        MessageBox.Show("FocusKeeperは既に起動しています。");
        Shutdown();
        return;
    }
    base.OnStartup(e);
}
```

---

## テスト用パターン

```csharp
// Helpers/TestDbFactory.cs
// テスト用にインメモリSQLiteを使用
public class TestDbFactory : DbConnectionFactory
{
    public TestDbFactory() : base(":memory:") { }
}

// テスト例
public class TaskRepositoryTests
{
    [Fact]
    public async Task AddAsync_ShouldPersistTask()
    {
        var factory = new TestDbFactory();
        await new DatabaseInitializer(factory).InitializeAsync();
        var repo = new TaskRepository(factory, NullLogger<TaskRepository>.Instance);

        var item = new TaskItem { Title = "テスト作業" };
        await repo.AddAsync(item);

        var all = await repo.GetAllAsync();
        Assert.Single(all);
        Assert.Equal("テスト作業", all.First().Title);
    }
}
```
