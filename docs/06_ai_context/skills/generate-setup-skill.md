# スキル: セットアップスキル生成

> このスキルを実行すると、指定したプロジェクト向けの
> セットアップスキルファイル（`skills/setup/{platform}.md`）を生成します。
> 生成されたファイルには実際のコードテンプレートが含まれ、
> そのまま次のプロジェクトのスキャフォールドに使用できます。

---

## ユーザーがすること・エージェントがすること

| フェーズ | ユーザー | エージェント |
|---------|---------|------------|
| Step 1 | 質問に答える | 質問を順番に提示する |
| Step 2 | 生成計画を確認し「OK」または修正を伝える | 回答をもとに生成計画を作成・提示する |
| Step 3 | 待つ | スキルファイルを生成する |
| Step 4 | 生成されたファイルをレビューし、必要なら修正を指示する | 検証チェックリストを実行し結果を報告する |

---

## Step 1: インタビュー

エージェントは以下の質問を**1問ずつ順番に**提示する。
全問回答が揃うまで Step 2 に進まない。

---

### Q1. プロジェクト種別（必須）

> 「どのような種類のアプリを作りますか？」

| 選択肢 | 説明 |
|--------|------|
| `1` desktop-wpf | WPF Windows デスクトップアプリ |
| `2` desktop-winui | WinUI 3 Windows デスクトップアプリ |
| `3` api-aspnet | ASP.NET Core Web API |
| `4` cli-dotnet | .NET コンソールアプリ / CLIツール |
| `5` lib-dotnet | .NET クラスライブラリ |

**→ 回答がこの後の全テンプレート選択を決定する。**

---

### Q2. 機能セット（任意・複数選択可）

> 「以下の機能のうち、最初から含めたいものを選んでください。（不要なら「なし」）」

| 選択肢 | 説明 | 対象プロジェクト種別 |
|--------|------|-------------------|
| `A` feat-sqlite | SQLiteによるローカルデータ永続化 | 全種別 |
| `B` feat-settings | アプリ設定の保存・読み込み | 全種別 |
| `C` feat-tray | タスクトレイ常駐 | desktop のみ |
| `D` feat-singleinstance | 多重起動防止 | desktop のみ |
| `E` feat-logging | Serilog ファイルロギング | 全種別 |
| `F` feat-ci | GitHub Actions CI パイプライン | 全種別 |
| `G` feat-msix | MSIX パッケージング設定 | desktop のみ |

**→ 選択した機能セットが「任意ファイル」テンプレートの追加を決定する。**

---

### Q3. 変数値（必須）

> 「以下の値を教えてください。」

| 変数 | 質問 | 形式 | 例 |
|------|------|------|----|
| `{{APP_NAME}}` | アプリ・ライブラリの名前は？（実行ファイル名・ソリューション名になります） | PascalCase | `FocusKeeper` |
| `{{ROOT_NAMESPACE}}` | ルート名前空間は？（通常はアプリ名と同じ） | PascalCase | `FocusKeeper` |
| `{{REPO_ROOT}}` | スキルファイルを保存するリポジトリのルートパスは？ | 絶対パス | `/home/user/FocusKeeper` |

---

## Step 2: 生成計画の提示と確認

エージェントは回答をもとに以下の形式で**生成計画**を提示し、ユーザーの承認を待つ。

---

### 提示フォーマット（エージェントが出力する内容）

```
=== セットアップスキル生成計画 ===

出力ファイル: docs/06_ai_context/skills/setup/desktop-wpf.md

プロジェクト種別: desktop-wpf（WPF Windowsデスクトップアプリ）
機能セット: feat-sqlite, feat-singleinstance, feat-logging

--- 生成されるファイル一覧（テンプレート対象） ---

【必須 - 7ファイル】
  1. FocusKeeper.sln
  2. Directory.Build.props
  3. .editorconfig
  4. src/FocusKeeper/FocusKeeper.csproj
  5. src/FocusKeeper/App.xaml
  6. src/FocusKeeper/App.xaml.cs
  7. tests/FocusKeeper.Tests/FocusKeeper.Tests.csproj

【任意 - feat-sqlite】
  8. src/FocusKeeper/Infrastructure/DbConnectionFactory.cs
  9. src/FocusKeeper/Infrastructure/DatabaseInitializer.cs

【任意 - feat-singleinstance】
  10. src/FocusKeeper/Infrastructure/SingleInstanceGuard.cs

【任意 - feat-logging】
  11. src/FocusKeeper/Infrastructure/LoggingSetup.cs

以上 11 ファイルのテンプレートを含む
docs/06_ai_context/skills/setup/desktop-wpf.md を生成します。

この計画でよろしいですか？（OK / 修正点を伝えてください）
```

---

ユーザーが「OK」と答えた場合のみ Step 3 に進む。
修正を求められた場合は、該当箇所を変更して再提示する。

---

## Step 3: スキルファイルの生成

エージェントは `setup_skill_format.md` の仕様に従い、
以下の手順でスキルファイルを構築する。

### 3-1. フロントマターの生成

Step 1 の回答から以下を埋める。

```yaml
---
skill-type: setup
project-type: {Q1の回答}
features: [{Q2の回答リスト}]
stack: {プロジェクト種別に対応する技術スタック名}
version: 1.0.0
---
```

### 3-2. 変数定義セクションの生成

Q3 で収集した変数を、定義テーブルとして書き出す。

### 3-3. 生成ファイル一覧の生成

Step 2 で提示した計画をテーブル形式に変換する。
必須ファイルと、選択された機能セットに対応する任意ファイルのみを含める。

### 3-4. テンプレート群の生成

**エージェントの知識**と `setup_skill_format.md` のテンプレート構造定義を使い、
各ファイルの初期コードを生成する。

生成ルール:
- `{{変数名}}` はプレースホルダーのまま残す（置換は後のスキル実行時に行う）
- 機能セット固有のコードは `<!-- feat-xxx -->` コメントで明示する
- 各テンプレートには「役割」と「機能セット依存」の説明を添える

### 3-5. セットアップコマンドの生成

プロジェクト種別に対応するビルド・テストコマンドを記述する。

### 3-6. 完了検証チェックリストの生成

プロジェクト種別と機能セットに応じた検証項目を記述する。

---

## Step 4: 完了検証と報告

エージェントは生成したスキルファイルを確認し、以下をユーザーに報告する。

```
=== 生成完了 ===

生成ファイル: docs/06_ai_context/skills/setup/desktop-wpf.md
テンプレート数: 11ファイル分

【確認済み項目】
✓ フロントマターの項目がすべて設定されている
✓ 変数定義に {{APP_NAME}}, {{ROOT_NAMESPACE}}, {{REPO_ROOT}} がすべて含まれている
✓ 生成ファイル一覧の全エントリにテンプレートIDが対応している
✓ テンプレートIDと ## テンプレート セクションの見出しが一致している
✓ 完了検証チェックリストが含まれている

次のステップ:
生成された skills/setup/desktop-wpf.md を使って実際のプロジェクトをセットアップするには、
新しいリポジトリで「このスキルを実行してください」と伝えてください。
エージェントが変数値を確認し、テンプレートを展開してプロジェクトを作成します。
```

---

## このスキルが生成しないもの

以下はこのスキルの対象外です。混同しないよう注意してください。

| 対象外 | 理由 | 代わりに使うもの |
|--------|------|----------------|
| 実際のプロジェクトファイル生成 | このスキルは「スキルを作る」スキル | 生成された `skills/setup/*.md` を実行する |
| ドキュメント（docs/）の生成 | ドキュメントは別途作成する | `document_architecture.md` の定義に従う |
| CI/CDの実行設定 | インフラ設定は別管理 | `feat-ci` で CI 設定ファイルのテンプレートは含まれる |
