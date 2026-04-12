# 実行計画: FocusKeeper 初期実装

> ステータス: active  
> 作成日: 2026-04-12  
> 担当: 開発チーム

---

## 目標・スコープ（3行）

FocusKeeperのv1.0として、オーバーレイ表示・作業入力・設定ウィンドウの3機能をリリースする。  
アクティブウィンドウ監視はオプション機能として実装し、v1.0に含める。  
MSIX配布可能な状態までを今計画のスコープとする。

---

## 受け入れ条件

- [ ] オーバーレイウィンドウが常時最前面表示でき、クリックスルーが機能する
- [ ] 作業入力ダイアログから作業名を入力・選択してオーバーレイに反映できる
- [ ] 作業リストへの登録・編集・削除ができる
- [ ] 設定ウィンドウから表示設定・動作設定を変更できる
- [ ] 設定変更がオーバーレイにリアルタイムで反映される
- [ ] アプリ再起動後も作業リスト・設定・最後の作業が復元される
- [ ] タスクトレイ常駐ができる
- [ ] `dotnet test` がすべてパスする（Service / ViewModel のカバレッジ 80%以上）
- [ ] MSIXパッケージが正常にビルドできる

---

## タスク分解

### Phase A: プロジェクト基盤

- [ ] A-1: ソリューション・プロジェクト構成の作成（`src/FocusKeeper/`, `tests/FocusKeeper.Tests/`）
- [ ] A-2: `Directory.Build.props` でパッケージバージョン一元管理
- [ ] A-3: DI コンテナ設定（`App.xaml.cs`）
- [ ] A-4: SQLite 初期化・DDL実行（`DatabaseInitializer`）
- [ ] A-5: Serilog ロギングセットアップ
- [ ] A-6: 多重起動防止（`SingleInstanceGuard`）
- [ ] A-7: `.editorconfig` / `StyleCop` 設定

### Phase B: データ層

- [ ] B-1: モデルクラス定義（`TaskItem`, `TaskHistory`, `AppSettings`）
- [ ] B-2: `TaskRepository` 実装 + テスト
- [ ] B-3: `SettingsRepository` 実装 + テスト
- [ ] B-4: `DbConnectionFactory` 実装

### Phase C: ビジネスロジック層

- [ ] C-1: `TaskService` 実装 + テスト（作業切り替え・履歴記録）
- [ ] C-2: `SettingsService` 実装 + テスト（設定読み書き・変更イベント）
- [ ] C-3: `WindowMonitorService` 実装 + テスト（アクティブウィンドウ監視）
- [ ] C-4: `StartupManager` 実装（スタートアップ登録）

### Phase D: ViewModel 層

- [ ] D-1: `OverlayViewModel` 実装 + テスト
- [ ] D-2: `SettingsViewModel` 実装 + テスト
- [ ] D-3: `TaskSelectViewModel` 実装 + テスト
- [ ] D-4: `TaskListViewModel` 実装 + テスト

### Phase E: View 層（UI）

- [ ] E-1: テーマ・リソース定義（`Colors.xaml`, `Styles.xaml`）
- [ ] E-2: `OverlayWindow.xaml` 実装（最前面・クリックスルー・ドラッグ）
- [ ] E-3: `TaskSelectDialog.xaml` 実装（インクリメンタルサーチ）
- [ ] E-4: `SettingsWindow.xaml` 実装（タブ構成・リアルタイムプレビュー）
- [ ] E-5: タスクトレイアイコン・コンテキストメニュー実装

### Phase F: CI/CD

- [ ] F-1: GitHub Actions CI ワークフロー（build + test）
- [ ] F-2: GitHub Actions Release ワークフロー（MSIX ビルド + GitHub Release）
- [ ] F-3: Roslyn アナライザー設定（`invariants.md` の INV-001〜008）

---

## 進捗ログ

| 日付 | 内容 |
|------|------|
| 2026-04-12 | ドキュメント一式を作成（フェーズ2完了）。フェーズ3（実装）開始準備が整った |

---

## 判断ログ

| 日付 | 決定事項 | 理由 |
|------|---------|------|
| 2026-04-12 | UIフレームワークをWPFに決定 | ADR-001参照 |
| 2026-04-12 | MVVMライブラリをCommunityToolkit.Mvvmに決定 | ADR-002参照 |
| 2026-04-12 | DBをSQLiteに決定 | ADR-003参照 |
| 2026-04-12 | 配布形式をMSIXに決定 | ADR-004参照 |
| 2026-04-12 | アクティブウィンドウ監視をv1.0オプション機能として含める | 差別化機能として価値が高く、実装コストは限定的 |
