# 外部ライブラリ・依存関係管理

> status: active

---

## 採用ライブラリ一覧

### メインプロジェクト（`src/FocusKeeper/`）

| パッケージ | バージョン | 用途 | ライセンス |
|-----------|-----------|------|-----------|
| `CommunityToolkit.Mvvm` | 8.x | MVVMパターン支援（ObservableObject, RelayCommand等） | MIT |
| `Microsoft.Data.Sqlite` | 8.x | SQLiteアクセス | MIT |
| `Microsoft.Extensions.DependencyInjection` | 8.x | DIコンテナ | MIT |
| `Microsoft.Extensions.Logging` | 8.x | ロギング抽象化 | MIT |
| `Serilog` | 3.x | ログ実装（ファイル出力） | Apache 2.0 |
| `Serilog.Extensions.Logging` | 8.x | Microsoft.Extensions.Logging ブリッジ | Apache 2.0 |
| `Serilog.Sinks.File` | 5.x | ファイル出力シンク | Apache 2.0 |

### テストプロジェクト（`tests/FocusKeeper.Tests/`）

| パッケージ | バージョン | 用途 | ライセンス |
|-----------|-----------|------|-----------|
| `xunit` | 2.x | テストフレームワーク | Apache 2.0 |
| `xunit.runner.visualstudio` | 2.x | VS テストランナー統合 | Apache 2.0 |
| `Moq` | 4.x | モックライブラリ | MIT |
| `Microsoft.NET.Test.Sdk` | 17.x | .NET テストSDK | MIT |
| `Microsoft.Extensions.Logging.Abstractions` | 8.x | NullLogger（テスト用） | MIT |

---

## バージョン管理方針

- `*.csproj` のパッケージバージョンは `Directory.Build.props` で一元管理する
- メジャーバージョンアップは必ず動作確認のうえ、ADR（decisions.md）に記録する
- パッチバージョンアップは自動（Dependabot等）で対応可

```xml
<!-- Directory.Build.props -->
<Project>
  <PropertyGroup>
    <CommunityToolkitMvvmVersion>8.3.2</CommunityToolkitMvvmVersion>
    <MicrosoftDataSqliteVersion>8.0.4</MicrosoftDataSqliteVersion>
    <SerilogVersion>3.1.1</SerilogVersion>
    <XunitVersion>2.9.0</XunitVersion>
    <MoqVersion>4.20.72</MoqVersion>
  </PropertyGroup>
</Project>
```

---

## ライセンス上の注意

- 採用ライブラリはすべて MIT または Apache 2.0 ライセンス
- GPL / LGPL ライブラリの採用は事前に確認が必要（配布条件に影響する可能性）
- ライブラリ追加時は THIRD-PARTY-NOTICES.txt に記載する

---

## 禁止ライブラリ

| パッケージ | 理由 |
|-----------|------|
| `Newtonsoft.Json` | `System.Text.Json`（標準）で対応可能 |
| `log4net` | Serilog に統一 |
| `EntityFramework Core`（v1.0） | SQLite直接操作で十分な複雑度。ORM追加は作業リスト1000件超時に検討 |

---

## セキュリティパッチ方針

- `dotnet list package --vulnerable` を CI で定期実行する
- 高・重大の脆弱性は即座に対応する
- 中程度の脆弱性は次のスプリントで対応する
