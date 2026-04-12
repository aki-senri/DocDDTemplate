# コーディング規約

> status: active

C# / WPF / .NET 8 向けのコーディング規約です。StyleCop と EditorConfig で自動チェックします。

---

## 命名規則

| 対象 | 規則 | 例 |
|------|------|----|
| クラス・インターフェース | PascalCase | `TaskService`, `ITaskRepository` |
| メソッド | PascalCase | `GetTasksAsync`, `SaveSettings` |
| プロパティ | PascalCase | `CurrentTask`, `IsEnabled` |
| フィールド（private） | _camelCase（アンダースコアプレフィックス） | `_taskRepository`, `_logger` |
| ローカル変数・引数 | camelCase | `taskItem`, `cancellationToken` |
| 定数 | PascalCase | `MaxTaskLength`, `DefaultOpacity` |
| インターフェース | 先頭 `I` + PascalCase | `ITaskService` |
| 非同期メソッド | 末尾 `Async` | `LoadTasksAsync` |
| XAML `x:Name` | camelCase | `taskTitleTextBox` |
| リソースキー（XAML） | PascalCase | `PrimaryBrush`, `OverlayStyle` |

---

## ファイル・クラス構成

- 1ファイル1クラス（ネストクラス除く）
- ファイル名はクラス名と一致させる
- ファイルの最大行数：300行（超える場合は分割を検討）
- 部分クラス（partial）は XAML コードビハインドのみ許可

---

## 非同期処理

```csharp
// ✅ 正しい
public async Task<IEnumerable<TaskItem>> GetTasksAsync(CancellationToken ct = default)
{
    return await _repository.GetAllAsync(ct);
}

// ❌ 禁止：.Result / .Wait() はデッドロックの原因
var result = GetTasksAsync().Result;
```

- `async void` は WPF イベントハンドラ (`Button_Click` 等) のみ許可。それ以外は `async Task`
- `CancellationToken` を受け取れるAPIはすべて受け取る

---

## MVVM 規則

- View（XAML コードビハインド）にビジネスロジックを書かない
- ViewModel から直接 View を参照しない
- ViewModel は `ObservableObject` を継承し、CommunityToolkit.Mvvm の `[ObservableProperty]` / `[RelayCommand]` を使用する

```csharp
// ✅ CommunityToolkit.Mvvm の使用例
[ObservableProperty]
private string _currentTaskTitle = string.Empty;

[RelayCommand]
private async Task ChangeTaskAsync()
{
    // ...
}
```

---

## エラー処理

- UI起点の操作でエラーが発生した場合はユーザーに通知する（サイレントに失敗しない）
- `catch (Exception)` で握り潰さない。ログ記録後にユーザーへフィードバック
- DB操作は `try/catch` でラップし、エラー時は元の状態が保たれることを保証する

```csharp
// ✅ 正しい
try
{
    await _repository.SaveAsync(item);
}
catch (Exception ex)
{
    _logger.LogError(ex, "作業の保存に失敗しました: {Title}", item.Title);
    // ViewModel経由でユーザーに通知
}
```

---

## 依存性注入

- コンストラクタインジェクションを使用する（プロパティインジェクション禁止）
- `new` によるサービスのインスタンス化を避ける（テスト不能になるため）
- ViewModel はコンテナから解決する

---

## XAML 規則

- コードビハインドにはイベントハンドラの最小限のコードのみ書く
- バインディングは `x:Bind`（型安全）より `Binding` を優先（WPF標準）
- リソースは `App.xaml` または専用 `ResourceDictionary` ファイルで管理
- マジックナンバー（色コード・サイズ等）は直接XAML内に書かず、リソースを参照する

---

## EditorConfig 設定（`.editorconfig` 抜粋）

```ini
root = true

[*.cs]
indent_style = space
indent_size = 4
end_of_line = crlf
charset = utf-8-bom
trim_trailing_whitespace = true
insert_final_newline = true

# using ディレクティブはファイルの外側に
csharp_using_directive_placement = outside_namespace

# var の使用：型が明らかな場合のみ許可
csharp_style_var_when_type_is_apparent = true:suggestion
csharp_style_var_elsewhere = false:suggestion
```
