# セットアップスキル 標準フォーマット定義

> このドキュメントは `skills/setup/{platform}.md` を書く際の**フォーマット仕様**です。
> スキルを手書きする場合も、`generate-setup-skill.md` を使って自動生成する場合も、
> 出力はこの仕様に従います。

---

## フォーマット種別

スキルファイルは**プロジェクト種別**と**機能セット**の組み合わせで内容が変わります。
エージェントは以下の種別を参照して、どのテンプレートを含めるかを決定します。

### プロジェクト種別（必ず1つ選択）

| 種別ID | 説明 | 含まれるテンプレートの特徴 |
|--------|------|--------------------------|
| `desktop-wpf` | WPF Windowsデスクトップアプリ | App.xaml / ウィンドウ / XAML / MVVM一式 |
| `desktop-winui` | WinUI 3 Windowsデスクトップアプリ | App.xaml / WinUI固有セットアップ |
| `api-aspnet` | ASP.NET Core Web API | Program.cs / Controller / Middleware一式 |
| `cli-dotnet` | .NETコンソールアプリ / CLIツール | Program.cs / HostBuilder / コマンドパーサー |
| `lib-dotnet` | .NETクラスライブラリ | ライブラリプロジェクト / パッケージング設定 |

### 機能セット（複数選択可・任意）

機能セットの選択により、「任意ファイル」セクションのテンプレートが追加されます。

| 機能セットID | 説明 | 追加されるテンプレート例 |
|-------------|------|----------------------|
| `feat-sqlite` | SQLiteによるローカルデータ永続化 | `DbConnectionFactory`, `DatabaseInitializer`, `*Repository` 基底 |
| `feat-settings` | アプリ設定の保存・読み込み | `SettingsRepository`, `SettingsService`, 設定モデル |
| `feat-tray` | タスクトレイ常駐（Windowsデスクトップのみ） | `TrayIconManager`, コンテキストメニュー定義 |
| `feat-singleinstance` | 多重起動防止（Named Mutex） | `SingleInstanceGuard` |
| `feat-logging` | Serilogによるファイルロギング | Serilog設定, `LoggingSetup` |
| `feat-ci` | GitHub Actions CI/CDパイプライン | `.github/workflows/ci.yml` |
| `feat-msix` | MSIXパッケージング設定 | パッケージマニフェスト, パブリッシュプロファイル |

---

## スキルファイルの構成

```
skills/setup/{platform-id}.md
│
├── [1] フロントマター       ─ スキルのメタ情報（機械読み取り用）
├── [2] 変数定義             ─ ユーザーが値を決める項目の一覧
├── [3] 生成ファイル一覧     ─ 何を作るかの全量リスト
│   ├── 必須ファイル         ─ 常に生成
│   └── 任意ファイル         ─ 機能セット選択時に生成
├── [4] テンプレート群       ─ 各ファイルの初期コード
├── [5] セットアップコマンド ─ 実行すべきコマンド（順番付き）
└── [6] 完了検証チェックリスト ─ 正常完了の確認基準
```

---

## 各セクションの定義

---

### [1] フロントマター

```yaml
---
skill-type: setup
project-type: desktop-wpf          # 種別ID（上記テーブルより）
features: [feat-sqlite, feat-tray] # 含まれる機能セットID（配列）
stack: C# / .NET 8 / WPF
version: 1.0.0
---
```

**役割**: エージェントがスキルの種類と機能セットを一目で把握するためのメタ情報。
ガベージコレクションエージェントがスキル一覧を管理する際にも使用する。

---

### [2] 変数定義

エージェントはスキル実行開始時にこの一覧をユーザーに提示し、値を確認してから次に進む。

```markdown
## 変数定義

> エージェントへの指示: 以下の変数をユーザーに確認し、全て揃ってから生成を開始してください。

| 変数 | 説明 | 形式 | 例 |
|------|------|------|----|
| `{{APP_NAME}}` | アプリ名。ソリューション名・プロジェクト名・実行ファイル名に使用される | PascalCase | `FocusKeeper` |
| `{{ROOT_NAMESPACE}}` | ルート名前空間。通常は APP_NAME と同じ | PascalCase | `FocusKeeper` |
| `{{REPO_ROOT}}` | ファイルを生成するリポジトリのルートパス | 絶対パス | `/home/user/FocusKeeper` |
```

**役割**: テンプレート内の `{{変数名}}` をユーザー指定の値に置き換えるための入力定義。
変数は必ず使われる場所が特定されており、未定義の `{{変数}}` はスキルに存在しない。

---

### [3] 生成ファイル一覧

```markdown
## 生成ファイル一覧

### 必須ファイル

| # | 生成パス | 役割 | テンプレート |
|---|---------|------|------------|
| 1 | `{{APP_NAME}}.sln` | ソリューションファイル | [→ tpl-sln](#tpl-sln) |
| 2 | `Directory.Build.props` | NuGetバージョン一元管理 | [→ tpl-build-props](#tpl-build-props) |
| 3 | `.editorconfig` | コードスタイル統一 | [→ tpl-editorconfig](#tpl-editorconfig) |
| 4 | `src/{{APP_NAME}}/{{APP_NAME}}.csproj` | メインプロジェクト定義 | [→ tpl-csproj-main](#tpl-csproj-main) |
| 5 | `src/{{APP_NAME}}/App.xaml` | アプリケーション定義 | [→ tpl-app-xaml](#tpl-app-xaml) |
| 6 | `src/{{APP_NAME}}/App.xaml.cs` | DIコンテナ構築・起動処理 | [→ tpl-app-cs](#tpl-app-cs) |
| 7 | `tests/{{APP_NAME}}.Tests/{{APP_NAME}}.Tests.csproj` | テストプロジェクト定義 | [→ tpl-csproj-test](#tpl-csproj-test) |

### 任意ファイル（機能セットによる）

| # | 生成パス | 役割 | テンプレート | 生成条件 |
|---|---------|------|------------|---------|
| 8 | `src/{{APP_NAME}}/Infrastructure/DbConnectionFactory.cs` | SQLite接続管理 | [→ tpl-db-factory](#tpl-db-factory) | `feat-sqlite` |
| 9 | `src/{{APP_NAME}}/Infrastructure/DatabaseInitializer.cs` | DB初期化・マイグレーション | [→ tpl-db-init](#tpl-db-init) | `feat-sqlite` |
| 10 | `src/{{APP_NAME}}/Infrastructure/SingleInstanceGuard.cs` | 多重起動防止 | [→ tpl-single-instance](#tpl-single-instance) | `feat-singleinstance` |
| 11 | `.github/workflows/ci.yml` | CI設定 | [→ tpl-ci](#tpl-ci) | `feat-ci` |
```

**役割**: 生成するファイルの全量を事前に確認できる。
エージェントはこのリストを生成計画としてユーザーに提示し、承認を得てから実行する。

---

### [4] テンプレート群

各テンプレートは `<a id="tpl-xxx">` のアンカーIDを持ち、[3] の一覧から参照される。

````markdown
## テンプレート

---

### <a id="tpl-csproj-main"></a> `src/{{APP_NAME}}/{{APP_NAME}}.csproj`

> **役割**: .NET 8 WPFアプリのプロジェクト定義。パッケージバージョンは Directory.Build.props で一元管理。
> **機能セット依存**: `feat-sqlite` 選択時は Microsoft.Data.Sqlite の参照行を含む。

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>WinExe</OutputType>
    <TargetFramework>net8.0-windows</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <UseWPF>true</UseWPF>
    <RootNamespace>{{ROOT_NAMESPACE}}</RootNamespace>
    <AssemblyName>{{APP_NAME}}</AssemblyName>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="CommunityToolkit.Mvvm"
                      Version="$(CommunityToolkitMvvmVersion)" />
    <PackageReference Include="Microsoft.Extensions.DependencyInjection"
                      Version="$(MicrosoftExtensionsDIVersion)" />
    <!-- feat-sqlite -->
    <PackageReference Include="Microsoft.Data.Sqlite"
                      Version="$(MicrosoftDataSqliteVersion)" />
    <!-- feat-logging -->
    <PackageReference Include="Serilog.Sinks.File"
                      Version="$(SerilogSinksFileVersion)" />
  </ItemGroup>
</Project>
```

---

### <a id="tpl-app-cs"></a> `src/{{APP_NAME}}/App.xaml.cs`

> **役割**: DIコンテナ構築・多重起動チェック・アプリ起動エントリポイント。
> **機能セット依存**: `feat-singleinstance` 選択時は SingleInstanceGuard の呼び出しを含む。
> **注意**: ViewModels / Services / Repositories の追加はここに集約する（invariants.md 参照）。

```csharp
using Microsoft.Extensions.DependencyInjection;
using System.Windows;
using {{ROOT_NAMESPACE}}.ViewModels;

namespace {{ROOT_NAMESPACE}};

public partial class App : Application
{
    public static IServiceProvider Services { get; private set; } = null!;

    protected override void OnStartup(StartupEventArgs e)
    {
        var services = new ServiceCollection();
        ConfigureServices(services);
        Services = services.BuildServiceProvider();

        base.OnStartup(e);
        // TODO: 最初に表示するウィンドウを指定する
        // Services.GetRequiredService<MainWindow>().Show();
    }

    private static void ConfigureServices(IServiceCollection services)
    {
        // TODO: ViewModel / Service / Repository を登録する
        // services.AddTransient<MainViewModel>();
    }
}
```
````

**役割**: エージェントがコードブロックをそのままファイルに書き出す。
`{{変数}}` は書き出し前に置換済みであること。
`<!-- feat-xxx -->` コメントは、その機能セットを選択しない場合は行ごと削除する。

---

### [5] セットアップコマンド

```markdown
## セットアップコマンド

> エージェントへの指示: ファイル生成が完了したら以下を順番に実行し、エラーがないことを確認してください。

```powershell
# 1. 依存パッケージの復元
dotnet restore

# 2. ビルド確認（エラーがないこと）
dotnet build --configuration Debug

# 3. テスト実行（全パスすること）
dotnet test
```
```

---

### [6] 完了検証チェックリスト

```markdown
## 完了検証チェックリスト

> エージェントへの指示: 以下をすべて確認してから「スキル完了」とユーザーに報告してください。

- [ ] 生成ファイル一覧の全ファイルが存在する（パスを一覧表示して確認）
- [ ] `dotnet build` がエラーなしで完了する
- [ ] `dotnet test` が全テストパスで完了する（テストが0件でも可）
- [ ] アプリが起動する（起動してすぐ閉じてよい）
```

**役割**: エージェントがスキル完了を自己判断するための基準。
チェックを通過できない場合はその項目を修正してから完了とする。

---

## スキルファイルの命名規則

```
skills/setup/{project-type}[-{variant}].md

例:
  skills/setup/desktop-wpf.md          # WPF基本構成
  skills/setup/desktop-wpf-minimal.md  # WPF最小構成（テンプレートの絞り込み版）
  skills/setup/api-aspnet.md           # ASP.NET Core Web API
  skills/setup/cli-dotnet.md           # CLIツール
```
