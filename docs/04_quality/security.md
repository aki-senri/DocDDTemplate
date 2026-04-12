# セキュリティ要件・チェック項目

> status: active

---

## セキュリティ原則

FocusKeeperはローカル完結型アプリです。ネットワーク通信がないため攻撃面は限定的ですが、  
ローカルデータの保護とWindows API利用の安全性を確保します。

---

## 脅威モデル

| 脅威 | リスク | 対策 |
|------|--------|------|
| 他ユーザーによるデータアクセス | 中 | `%LOCALAPPDATA%` への保存（ユーザー分離） |
| SQLインジェクション | 低（ローカルDBのみ） | パラメータバインディング必須 |
| DLL Hijacking | 中 | MSIXサンドボックス・コード署名 |
| 悪意あるアクティブウィンドウ情報の悪用 | 低 | ウィンドウタイトルのみ取得、外部送信なし |
| 権限昇格 | 低 | UAC不要設計、管理者権限で動作しない |

---

## セキュリティ要件

### SR-01: 最小権限の原則
- アプリは標準ユーザー権限（管理者権限なし）で動作する
- `app.manifest` にて `requestedExecutionLevel = asInvoker` を設定する

### SR-02: データ保存場所
- アプリデータは `%LOCALAPPDATA%\FocusKeeper\` のみに保存する
- システムディレクトリ・レジストリ（スタートアップ以外）への書き込みは禁止

### SR-03: 入力バリデーション
- ユーザーが入力したすべてのテキストは Service 層でバリデーションする
- SQLパラメータは必ずバインディング変数を使用し、文字列結合によるSQLを禁止する

```csharp
// ✅ 正しい
var cmd = conn.CreateCommand();
cmd.CommandText = "SELECT * FROM task_items WHERE title LIKE @keyword";
cmd.Parameters.AddWithValue("@keyword", $"%{keyword}%");

// ❌ 禁止（SQLインジェクション）
cmd.CommandText = $"SELECT * FROM task_items WHERE title LIKE '%{keyword}%'";
```

### SR-04: コード署名
- 配布用MSIXパッケージは有効なコード署名証明書で署名する
- テスト環境では自己署名証明書を使用し、本番配布では信頼された証明書を使用する

### SR-05: 外部通信の禁止
- `HttpClient` / `WebClient` / `Socket` を使用した外部通信は禁止
- `invariants.md` の INV-007 でCI強制する

### SR-06: ウィンドウ情報取得の範囲制限
- アクティブウィンドウ監視で取得するのは「ウィンドウタイトル」のみ
- ウィンドウのコンテンツ・キー入力・クリップボードは取得しない

---

## セキュリティレビューチェックリスト

- [ ] `GetForegroundWindow` / `GetWindowText` 以外の Windows API を使用していないか
- [ ] SQLパラメータバインディングが使用されているか（文字列結合SQL禁止）
- [ ] `%LOCALAPPDATA%` 以外へのファイル書き込みがないか
- [ ] `HttpClient` 等の外部通信クラスが使われていないか
- [ ] 取得したウィンドウ情報がログに出力されていないか（プライバシー）
- [ ] MSIXパッケージに不要なファイル（デバッグシンボル等）が含まれていないか
