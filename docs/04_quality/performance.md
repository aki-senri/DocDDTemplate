# パフォーマンス基準・計測方法

> status: active

---

## パフォーマンス目標

| 指標 | 目標値 | 計測方法 |
|------|--------|----------|
| コールドスタート時間 | 3秒以内 | ストップウォッチ（手動） |
| 作業切り替え応答 | 200ms以内 | `Stopwatch`（コードレベル） |
| アイドル時CPU使用率 | 1%以下 | タスクマネージャー（手動） |
| 監視ON時CPU使用率 | 3%以下 | タスクマネージャー（手動） |
| 常時メモリ使用量 | 100MB以下 | タスクマネージャー（手動） |
| 72時間後メモリ | 起動時+10MB以内 | 自動計測スクリプト（将来対応） |
| DBクエリ（1000件） | 100ms以内 | xUnitベンチマークテスト |

---

## 重点注意箇所

### オーバーレイウィンドウの描画

- WPFの `DispatcherTimer` で描画更新を制御する場合、インターバルは最低100ms
- 不要な `PropertyChanged` 発火を避ける（バインディングが無駄に再描画しないよう）
- テキストが変わらない場合は `SetValue` を呼ばない

```csharp
// ✅ 変化があるときのみ通知
if (_currentTaskTitle != value)
{
    _currentTaskTitle = value;
    OnPropertyChanged(nameof(CurrentTaskTitle));
}
```

### アクティブウィンドウ監視

- `GetForegroundWindow` / `GetWindowText` を500msポーリング
- ポーリングはバックグラウンドスレッド（`Task.Run`）で実行し、UIスレッドをブロックしない
- 比較は文字列比較のみ（重い処理を入れない）

```csharp
// ✅ バックグラウンドポーリング
_monitorTimer = new PeriodicTimer(TimeSpan.FromMilliseconds(500));
_ = Task.Run(async () =>
{
    while (await _monitorTimer.WaitForNextTickAsync(_cts.Token))
    {
        var windowTitle = GetActiveWindowTitle();
        await CheckAndAlert(windowTitle);
    }
});
```

### SQLite クエリ

- 作業リスト取得は1クエリで完結させる（N+1クエリ禁止）
- インデックスを使用するクエリになっているか `EXPLAIN QUERY PLAN` で確認する

---

## 計測・ベンチマークテスト

```csharp
// FocusKeeper.Tests/Repositories/TaskRepositoryBenchmarkTests.cs
[Fact]
public async Task GetAllAsync_With1000Tasks_CompletesUnder100ms()
{
    // Arrange
    var factory = new TestDbFactory();
    await SeedTasksAsync(factory, 1000);
    var repo = new TaskRepository(factory, NullLogger<TaskRepository>.Instance);

    // Act
    var sw = Stopwatch.StartNew();
    var result = await repo.GetAllAsync();
    sw.Stop();

    // Assert
    Assert.True(sw.ElapsedMilliseconds < 100,
        $"クエリが100msを超えました: {sw.ElapsedMilliseconds}ms");
    Assert.Equal(1000, result.Count());
}
```

---

## パフォーマンス劣化の対応方針

1. 目標値を超えた計測値が確認された場合、Issue を起票する
2. プロファイリング（Visual Studio Profiler / dotnet-trace）で原因を特定する
3. ホットパスのみ最適化する（早すぎる最適化は禁止）
4. 最適化後、同じ手順で計測して改善を確認する
