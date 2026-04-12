# 監視・ログ方針・ガベージコレクション運用

> status: active

---

## ロギング方針

### ログレベルと使い分け

| レベル | 用途 | 例 |
|--------|------|----|
| `DEBUG` | 開発時の詳細ログ（本番では出力しない） | DBクエリ内容、ウィンドウタイトル取得結果 |
| `INFO` | 通常動作の記録 | アプリ起動、作業切り替え、設定保存 |
| `WARN` | 問題にはならないが注意が必要な状況 | DB取得件数が上限に近い、設定値が範囲外 |
| `ERROR` | 回復可能なエラー | DB書き込み失敗、UI操作エラー |
| `FATAL` | アプリ停止を伴うエラー | DB初期化失敗、必須リソース読み込み失敗 |

### 必須ログ項目

```csharp
// アプリ起動
_logger.LogInformation("FocusKeeper 起動 v{Version}", AppVersion);

// 作業切り替え
_logger.LogInformation("作業を切り替えました: {Title}", newTitle);

// エラー
_logger.LogError(ex, "作業の保存に失敗しました: {Title}", title);
```

### ログに含めてはいけない情報

- ウィンドウのコンテンツ（セキュリティ上の理由）
- ユーザーが入力した作業名の詳細（プライバシー）
  - 起動・切り替えのタイムスタンプは記録するが、作業名はINFOレベルまで

---

## ログファイル管理

```
%LOCALAPPDATA%\FocusKeeper\Logs\
├── focuskeeper-20260101.log
├── focuskeeper-20260102.log
└── ...（7日分保持）
```

- 日次ローテーション（Serilog `rollingInterval: Day`）
- 7日を超えたファイルは自動削除
- 1ファイルの最大サイズ：10MB（上限に達した場合は日付内でシーケンス番号付与）

---

## ガベージコレクション運用

### 定期エージェントタスク（週次）

#### 1. ドキュメント整備エージェント

```
トリガー: 毎週月曜 / 大きな機能マージ後
目的: 実コードとドキュメントの乖離を検出し修正PRを作成

チェック内容:
- docs/02_design/architecture.md のクラス図と実コードの整合性
- docs/03_implementation/directory_structure.md と実際のファイル構成の差異
- docs/02_design/data_model.md のDDLと実際のDBスキーマの差異

生成成果物: docs更新PR（レビュー1分以内を目標）
```

#### 2. アーキテクチャドリフト検出エージェント

```
トリガー: CIパイプライン（PRマージ後）
目的: invariants.md の違反を検出してリファクタリングPRを作成

チェック内容（自動）:
- Roslynアナライザーによるレイヤー依存方向チェック
- ファイル行数チェック
- 命名規則チェック

対応:
- 警告: PR作成して担当者に通知
- エラー: ビルド失敗（マージブロック）
```

#### 3. CONTEXT.md 更新エージェント

```
トリガー: フェーズ移行 / exec-plans/active/ の変更
目的: CONTEXT.md を常に最新の状態に保つ

チェック内容:
- 現在フェーズが最新か
- 優先タスクリンクが有効か
- exec-plans/active/ の内容と一致しているか
```

---

## エラー監視

エンドユーザー向けアプリのため、クラッシュレポートの自動送信は行いません。

ユーザーがバグを報告する際のサポート情報として：

1. ログファイルの場所をアプリ内から参照できるようにする
2. 設定ウィンドウに「ログフォルダを開く」ボタンを設置する
3. GitHub Issues へのリンクをアプリ内に表示する

---

## ヘルスチェック（開発用）

CI環境でのアプリの動作確認：

```yaml
# .github/workflows/ci.yml
- name: スモークテスト
  run: |
    # アプリを起動して3秒後にプロセスが存在するか確認
    Start-Process "src/FocusKeeper/bin/Release/net8.0-windows/FocusKeeper.exe"
    Start-Sleep -Seconds 3
    $proc = Get-Process "FocusKeeper" -ErrorAction SilentlyContinue
    if ($null -eq $proc) { exit 1 }
    $proc | Stop-Process
```
