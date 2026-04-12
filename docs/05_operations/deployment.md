# デプロイ・配布手順

> status: active

---

## 配布形式

| 形式 | 対象 | 備考 |
|------|------|------|
| **MSIX** | 一般ユーザー向け配布 | v1.0の主要配布形式 |
| **zip（自己解凍）** | 開発者・テスター向け | 署名なし、テスト用のみ |

---

## リリースフロー

```
1. main ブランチに PR マージ
         ↓
2. GitHub Actions CI が自動実行
   ├── dotnet build --configuration Release
   ├── dotnet test
   └── ビルド成功を確認
         ↓
3. リリースタグを作成
   git tag v1.0.0
   git push origin v1.0.0
         ↓
4. GitHub Actions Release ワークフローが自動実行
   ├── MSIXパッケージをビルド
   ├── コード署名
   └── GitHub Release に添付
         ↓
5. GitHub Release ページから配布
```

---

## バージョニング

セマンティックバージョニング（`MAJOR.MINOR.PATCH`）を採用します。

| 変更種別 | 例 |
|----------|-----|
| MAJOR | 破壊的変更、DBスキーマの互換性のない変更 |
| MINOR | 新機能追加（後方互換あり） |
| PATCH | バグ修正、セキュリティパッチ |

バージョンは `FocusKeeper/FocusKeeper.csproj` の `<Version>` で管理します。

---

## MSIXビルド手順

### 前提

- Visual Studio 2022 に「Windows アプリケーション パッケージ プロジェクト」がインストール済み
- コード署名証明書が `.pfx` 形式で用意されている

### ビルドコマンド

```bash
# MSIXパッケージのビルド
dotnet publish src/FocusKeeper/FocusKeeper.csproj \
  --configuration Release \
  --runtime win-x64 \
  --self-contained false \
  -p:PublishProfile=MSIX

# または GitHub Actions での自動ビルド（推奨）
```

### GitHub Actions Release ワークフロー

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build-msix:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '8.0.x'

      - name: ビルド
        run: dotnet build src/FocusKeeper/FocusKeeper.csproj --configuration Release

      - name: テスト
        run: dotnet test --configuration Release

      - name: MSIXパッケージ作成
        run: |
          # msbuild でMSIXを生成
          msbuild src/FocusKeeper/FocusKeeper.csproj `
            /p:Configuration=Release `
            /p:AppxBundlePlatforms="x64" `
            /p:AppxPackageDir="./artifacts/"

      - name: GitHub Release に添付
        uses: softprops/action-gh-release@v1
        with:
          files: ./artifacts/*.msix
```

---

## アップデート方針（v1.0）

- v1.0では手動アップデート（ユーザーが新しいMSIXをダウンロード・インストール）
- v2.0以降でMicrosoft Store経由の自動アップデートを検討

---

## アンインストール

MSIXパッケージは Windowsの「アプリと機能」から完全アンインストール可能です。  
ユーザーデータ（`%LOCALAPPDATA%\FocusKeeper\`）は残ります。

アンインストール時にデータも削除したい場合は、アンインストール前に「データを削除」ボタンをアプリから提供します（v2.0以降に検討）。
