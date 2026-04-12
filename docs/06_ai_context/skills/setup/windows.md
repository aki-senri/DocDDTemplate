# セットアップスキル：Windows（WPF / .NET 8）

> このスキルはFocusKeeperの開発環境をゼロからセットアップします。

---

## 前提条件

- Windows 10 22H2 以降 または Windows 11
- Git がインストール済み
- インターネット接続あり

---

## セットアップ手順

### Step 1: 必要ツールのインストール確認

```powershell
# .NET SDK の確認
dotnet --version  # 8.x が表示されること

# Visual Studio 2022 の確認（任意）
# コマンドラインビルドのみの場合はVS不要

# .NET SDKがない場合
# https://dotnet.microsoft.com/download/dotnet/8.0 からインストール
```

### Step 2: リポジトリのクローン

```bash
git clone https://github.com/aki-senri/FocusKeeper.git
cd FocusKeeper
```

### Step 3: 依存パッケージの復元

```bash
dotnet restore
```

### Step 4: ビルド確認

```bash
dotnet build --configuration Debug
# エラーがないことを確認
```

### Step 5: テスト実行

```bash
dotnet test
# すべてのテストがパスすることを確認
```

### Step 6: 開発用DB初期化

```bash
# 開発用DBは初回起動時に自動作成されます
# 手動で初期化する場合:
dotnet run --project src/FocusKeeper --configuration Debug
# アプリが起動し、%LOCALAPPDATA%\FocusKeeper\Dev\dev-focuskeeper.db が作成される
```

---

## 技術スタック詳細

| 項目 | 内容 |
|------|------|
| 言語 | C# 12 |
| ランタイム | .NET 8 |
| UIフレームワーク | WPF（Windows Presentation Foundation） |
| MVVMライブラリ | CommunityToolkit.Mvvm 8.x |
| DB | SQLite 3.x（Microsoft.Data.Sqlite） |
| DI | Microsoft.Extensions.DependencyInjection 8.x |
| ロギング | Serilog 3.x |
| テスト | xUnit 2.x + Moq 4.x |
| パッケージング | MSIX |

---

## コーディング規約の確認

```
参照: docs/03_implementation/coding_standards.md
主要ポイント:
- private フィールド: _camelCase
- 非同期メソッド: Async サフィックス
- ViewModel: ObservableObject 継承 + [ObservableProperty] / [RelayCommand]
- レイヤー依存: View → ViewModel → Service → Repository → Model
```

---

## 開発フロー

```
1. exec-plans/active/ から作業を確認
2. docs/01_requirements/user_stories/windows.md で要件確認
3. docs/03_implementation/invariants.md を確認（開発前に必読）
4. feature/xxx ブランチで開発
5. テスト作成・実行（docs/04_quality/test_strategy.md 参照）
6. docs/04_quality/review_checklist.md でセルフレビュー
7. PR作成 → レビュー → マージ
```

---

## よくある問題と対処

| 問題 | 対処 |
|------|------|
| `dotnet restore` が失敗する | NuGetフィードへのアクセス確認。プロキシ設定が必要な場合あり |
| WPFアプリがビルドできない | `<UseWPF>true</UseWPF>` が `.csproj` にあるか確認 |
| テストで `InvalidOperationException` | テスト用DBが残っている場合がある。`%TEMP%\test-*.db` を削除 |
| オーバーレイが表示されない | `Topmost = True` かつ `ShowInTaskbar = False` の設定を確認 |

---

## 成果物の確認

セットアップ完了後、以下が確認できること：

- [ ] `dotnet build` がエラーなく完了する
- [ ] `dotnet test` が全テストパスで完了する
- [ ] アプリを起動してオーバーレイが表示される
- [ ] 作業名を入力してオーバーレイに反映される
- [ ] 設定ウィンドウが開ける
