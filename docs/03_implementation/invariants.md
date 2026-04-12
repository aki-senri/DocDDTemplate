# アーキテクチャ不変条件

> status: active

これらの条件はRoslynアナライザーとCI（GitHub Actions）により機械的に強制されます。  
違反した場合はビルドエラーとなります。エラーメッセージには修復手順が記載されます。

---

## INV-001: レイヤー依存方向

**条件**: 依存の方向は以下の一方向のみ許可する。逆方向参照は禁止。

```
View → ViewModel → Service → Repository → Model
```

**禁止例**:
- `Repository` が `Service` を参照する
- `ViewModel` が `Repository` を直接参照する
- `Model` が `Service` を参照する

**検出方法**: Roslyn アナライザー（`FocusKeeper.Analyzers`）でアセンブリ参照を静的解析  
**修復方法**: 逆方向参照をインターフェース経由に変更するか、依存の向きを逆転させる

---

## INV-002: ViewModel にビジネスロジックを書かない

**条件**: ViewModel は `Service` を呼び出すだけで、ビジネスロジックを直接実装しない。

**禁止例**:
```csharp
// ❌ ViewModel 内にDB操作のロジック
public async Task ChangeTaskAsync(string title)
{
    var conn = new SqliteConnection("..."); // 禁止
    await conn.ExecuteAsync("INSERT ...");
}
```

**許可例**:
```csharp
// ✅ Service に委譲
public async Task ChangeTaskAsync(string title)
{
    await _taskService.SetCurrentTaskAsync(title);
}
```

**検出方法**: ViewModel クラスが `Repository` 型を直接参照している場合にビルドエラー  
**修復方法**: ロジックを Service レイヤーに移動する

---

## INV-003: View（コードビハインド）にロジックを書かない

**条件**: `.xaml.cs` ファイルに含まれるコードは以下のみ許可する:
- コンストラクタ（DI経由の DataContext 設定）
- WPF 固有のイベントハンドラ（ドラッグ移動等、XAMLバインドで代替困難なもの）

**禁止例**:
```csharp
// ❌ コードビハインドにビジネスロジック
private async void SaveButton_Click(object sender, RoutedEventArgs e)
{
    var repo = new TaskRepository(); // 禁止
    await repo.SaveAsync(new TaskItem { Title = titleBox.Text });
}
```

**検出方法**: `.xaml.cs` 内の行数が 50行超でビルド警告  
**修復方法**: ViewModel の `Command` にロジックを移動する

---

## INV-004: ファイルサイズ上限

| 対象 | 上限 | 超えた場合 |
|------|------|-----------|
| `.cs` ファイル | 300行 | ビルド警告 → 分割を推奨 |
| `.xaml` ファイル | 200行 | ビルド警告 → UserControl への切り出し推奨 |
| `App.xaml.cs` | 100行 | ビルドエラー |

---

## INV-005: 非同期処理の制約

**条件**: `async void` は WPF イベントハンドラ以外で使用禁止。

**禁止例**:
```csharp
// ❌ Service 内の async void
public async void LoadDataAsync() { ... }
```

**許可例**:
```csharp
// ✅ async Task
public async Task LoadDataAsync(CancellationToken ct = default) { ... }

// ✅ WPF イベントハンドラのみ async void 許可
private async void SaveButton_Click(object sender, RoutedEventArgs e) { ... }
```

**検出方法**: Roslyn アナライザーで `async void` をスキャン（WPFイベントハンドラシグネチャを除く）  
**修復方法**: `async void` → `async Task` に変更。呼び出し元で `await` する

---

## INV-006: 命名規則の強制

| 対象 | ルール | 違反例 |
|------|--------|--------|
| `private` フィールド | `_camelCase` | `privateField`（禁止） |
| インターフェース | `I` プレフィックス | `TaskService`（インターフェース名として禁止） |
| 非同期メソッド | `Async` サフィックス | `Task GetData()` → `Task GetDataAsync()` |
| ViewModel クラス | `ViewModel` サフィックス | `OverlayVM`（禁止） |
| Repository クラス | `Repository` サフィックス | `TaskData`（禁止） |

**検出方法**: Roslyn アナライザー（StyleCopルール拡張）  
**修復方法**: エラーメッセージに記載された命名規則に合わせてリネーム

---

## INV-007: 外部ネットワーク通信の禁止

**条件**: アプリ本体からの外部HTTP通信・DNS解決を禁止する。

**禁止例**:
```csharp
// ❌ HttpClient による外部通信
var response = await _httpClient.GetAsync("https://example.com/api");
```

**検出方法**: `HttpClient` / `HttpClientFactory` の using をスキャンして警告  
**修復方法**: ネットワーク依存の機能はスコープ外として削除する

---

## INV-008: データバリデーションの境界強制

**条件**: 外部入力（ユーザー入力・DBから読み取ったデータ）は Service 層の入口でバリデーションする。ViewModel でバリデーションしない。

**禁止例**:
```csharp
// ❌ ViewModel でバリデーション
if (string.IsNullOrEmpty(title) || title.Length > 100)
    throw new ArgumentException("...");
```

**許可例**:
```csharp
// ✅ Service でバリデーション
public async Task SetCurrentTaskAsync(string title)
{
    if (string.IsNullOrWhiteSpace(title))
        throw new ArgumentException("作業名を入力してください", nameof(title));
    if (title.Length > 100)
        throw new ArgumentException("作業名は100文字以内で入力してください", nameof(title));
    // ...
}
```
