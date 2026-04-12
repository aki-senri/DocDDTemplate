# 環境構成

> status: active

---

## 環境一覧

デスクトップアプリのため、Web系のような staging/prod 分離はありません。  
開発・テスト・配布の3フェーズで管理します。

| 環境 | 用途 | DB | ログレベル |
|------|------|----|-----------|
| **Development** | 開発者ローカル環境 | `dev-focuskeeper.db`（`%LOCALAPPDATA%\FocusKeeper\Dev\`） | DEBUG |
| **Testing** | CI・自動テスト | インメモリSQLite | DEBUG |
| **Release** | エンドユーザー配布版 | `focuskeeper.db`（`%LOCALAPPDATA%\FocusKeeper\`） | INFO |

---

## 開発環境セットアップ

### 必要なツール

| ツール | バージョン | 用途 |
|--------|-----------|------|
| Visual Studio 2022 | 17.x以上 | メインIDE |
| .NET SDK | 8.x | ビルド・テスト |
| Git | 2.x | バージョン管理 |
| Windows App SDK | 1.5以上 | MSIX パッケージング（任意） |

### セットアップ手順

```bash
# リポジトリのクローン
git clone https://github.com/aki-senri/FocusKeeper.git
cd FocusKeeper

# 依存パッケージの復元
dotnet restore

# ビルド確認
dotnet build --configuration Debug

# テスト実行
dotnet test
```

---

## 環境変数・設定ファイル

### 開発環境固有設定

`src/FocusKeeper/appsettings.Development.json`（リポジトリに含めない・gitignore対象）:

```json
{
  "Database": {
    "Path": "%LOCALAPPDATA%\\FocusKeeper\\Dev\\dev-focuskeeper.db"
  },
  "Logging": {
    "MinimumLevel": "Debug"
  }
}
```

### リリース時のデフォルト設定

`src/FocusKeeper/appsettings.json`:

```json
{
  "Database": {
    "Path": "%LOCALAPPDATA%\\FocusKeeper\\focuskeeper.db"
  },
  "Logging": {
    "MinimumLevel": "Information",
    "FilePath": "%LOCALAPPDATA%\\FocusKeeper\\Logs\\focuskeeper-.log",
    "RetainedFileCount": 7
  }
}
```

---

## データファイルの場所

| ファイル | パス |
|---------|------|
| DBファイル（本番） | `%LOCALAPPDATA%\FocusKeeper\focuskeeper.db` |
| DBファイル（開発） | `%LOCALAPPDATA%\FocusKeeper\Dev\dev-focuskeeper.db` |
| ログファイル | `%LOCALAPPDATA%\FocusKeeper\Logs\focuskeeper-YYYYMMDD.log` |
| アプリ設定（MSIXの場合） | `%LOCALAPPDATA%\Packages\FocusKeeper_xxx\LocalCache\` |
