# テスト戦略

> status: active

---

## テスト方針

FocusKeeperはUIを持つデスクトップアプリのため、テストレイヤーを分けて効率的にカバレッジを確保します。

```
テストピラミッド

         ▲
        /E2E\        ← UIテスト（WinAppDriver）：最小限
       /──────\
      /  統合  \     ← Repositoryのインテグレーション：中程度
     /──────────\
    /  ユニット   \   ← ViewModel / Service：重点的にカバー
   ──────────────────
```

---

## テスト種別と対象

### ユニットテスト（`FocusKeeper.Tests`）

| 対象レイヤー | テスト対象 | 方針 |
|-------------|-----------|------|
| ViewModel | `OverlayViewModel`, `SettingsViewModel`, `TaskSelectViewModel` | Service をモック化。状態変更・コマンド動作を検証 |
| Service | `TaskService`, `SettingsService`, `WindowMonitorService` | Repository をモック化。ビジネスロジックのみ検証 |
| Repository | `TaskRepository`, `SettingsRepository` | インメモリSQLiteを使用。実際のCRUD操作を検証 |

### E2Eテスト（将来対応）

- WinAppDriver によるUIオートメーション
- v1.0では手動テストで代替し、v2.0以降に自動化

---

## カバレッジ目標

| レイヤー | カバレッジ目標 |
|----------|-------------|
| Service | 80%以上 |
| ViewModel | 80%以上 |
| Repository | 70%以上 |
| View（コードビハインド） | 計測対象外 |

---

## テストケース命名規則

```
{テスト対象メソッド}_{シナリオ}_{期待する結果}
```

**例**:
```csharp
SetCurrentTaskAsync_WithValidTitle_SetsCurrentTask()
SetCurrentTaskAsync_WithEmptyTitle_ThrowsArgumentException()
SetCurrentTaskAsync_WithTitleOver100Chars_ThrowsArgumentException()
GetAllAsync_WhenDatabaseIsEmpty_ReturnsEmptyCollection()
```

---

## テスト実装例

```csharp
public class TaskServiceTests
{
    private readonly Mock<ITaskRepository> _taskRepoMock;
    private readonly ITaskService _sut;

    public TaskServiceTests()
    {
        _taskRepoMock = new Mock<ITaskRepository>();
        _sut = new TaskService(_taskRepoMock.Object, NullLogger<TaskService>.Instance);
    }

    [Fact]
    public async Task SetCurrentTaskAsync_WithValidTitle_SetsCurrentTask()
    {
        // Arrange
        const string title = "メール対応";

        // Act
        await _sut.SetCurrentTaskAsync(title);

        // Assert
        Assert.Equal(title, _sut.CurrentTaskTitle);
        _taskRepoMock.Verify(r => r.UpdateLastUsedAsync(title, It.IsAny<DateTime>()), Times.Once);
    }

    [Theory]
    [InlineData("")]
    [InlineData("   ")]
    [InlineData(null)]
    public async Task SetCurrentTaskAsync_WithInvalidTitle_ThrowsArgumentException(string? title)
    {
        await Assert.ThrowsAsync<ArgumentException>(
            () => _sut.SetCurrentTaskAsync(title!));
    }
}
```

---

## ドキュメント鮮度チェック

### 検出ルール

- 実コードに存在するクラス名がドキュメントに存在するか（週次チェック）
- `docs/` 内のファイルの最終更新日が実コードの変更より30日以上古い場合に警告
- `status: draft` のファイルが14日以上経過で警告

### CI チェック

```yaml
# .github/workflows/doc-check.yml
- name: ドキュメント鮮度チェック
  run: |
    # docs/ の status: deprecated ファイルをリストアップ
    grep -r "status: deprecated" docs/ | xargs -I{} echo "deprecated: {}"
```

### ドキュメント status フィールド

| status | 意味 | 対応 |
|--------|------|------|
| `draft` | 執筆中・未確定 | 14日以内に `active` へ |
| `active` | 有効・最新 | 通常状態 |
| `deprecated` | 廃止済み | 参照ドキュメントを更新後に削除 |

---

## CI パイプライン

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  build-and-test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '8.0.x'
      - run: dotnet restore
      - run: dotnet build --no-restore --configuration Release
      - run: dotnet test --no-build --configuration Release --collect:"XPlat Code Coverage"
      - name: カバレッジチェック
        run: |
          # カバレッジが閾値（70%）未満の場合に失敗
          dotnet tool run reportgenerator -reports:**/coverage.cobertura.xml -targetdir:coverage -reporttypes:TextSummary
```
