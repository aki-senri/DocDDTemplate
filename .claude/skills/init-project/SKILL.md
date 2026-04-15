---
name: init-project
description: Initialize a new project. Interviews the user to capture project overview, tech stack, development workflow rules, and platform type, then creates Phase 0 documents and executes the appropriate platform setup (Phase 1).
disable-model-invocation: true
---

# スキル: プロジェクト初期化

> **実行タイミング**: プロジェクト開始時に一度だけ実行する（Phase 0 → Phase 1）
>
> **目的**: チームメンバー（人間・AIエージェント双方）が「このプロジェクトをどう動かすか」を
> 一つのファイル（CONTEXT.md）から理解できる状態を作り、
> 続けてプラットフォーム固有の開発フロー定義（Phase 1）まで完了させる。
>
> **前提**: リポジトリが作成済みであること。

---

## このスキルが作るもの

### Phase 0（全プラットフォーム共通）

| ファイル | 役割 | 内容の決まり方 |
|---------|------|--------------|
| `docs/00_project/overview.md` | プロジェクトの目的・スコープ・技術スタック | Q1・Q2の回答から生成 |
| `docs/00_project/decisions.md` | 技術選定の意思決定ログ（ADR形式） | Q2の回答から生成 |
| `docs/06_ai_context/CONTEXT.md` | ナビゲーションマップ（開発ルール含む） | 全回答から生成 |

### Phase 1（Q4のプラットフォームに応じて実行）

| プラットフォーム | 参照 | 生成ドキュメント数 |
|----------------|------|-----------------|
| Windows（WPF / .NET 8） | [setup-windows.md](setup-windows.md) | 6ファイル + CONTEXT.md更新 |
| Web（React / ASP.NET Core） | [setup-web.md](setup-web.md) | 7ファイル + CONTEXT.md更新 |

内容はインタビューの回答をもとにエージェントが生成する（固定テンプレートではない）。
生成するドキュメントの一覧と必須/任意の判断基準は下記「ドキュメント構成」セクションを参照。

---

## インタビュー（Phase 0）

エージェントは以下を**1問ずつ順番に**確認する。

---

### Q1. プロジェクト概要

> 「このプロジェクトは何を作りますか？（目的・対象ユーザー・主な機能を3行以内で）」

→ `overview.md` の目的・背景・スコープ欄に使用
→ `CONTEXT.md` の冒頭3行（プロジェクト概要）に使用

---

### Q2. 技術スタック

> 「使用する技術スタックを教えてください。
> （例: プラットフォーム / 言語 / フレームワーク / DB / 配布方法）」

続けて確認する:

> 「それぞれの技術を選んだ主な理由を教えてください。
> 理由が不明な項目は『未決定』で構いません。」

→ `overview.md` の技術スタック表に使用
→ `decisions.md` に ADR として記録（選定理由が明確なもののみ）
→ `CONTEXT.md` の技術スタックセクションに使用

---

### Q3. 開発ルール

> 「このプロジェクトの開発ルールを確認します。
> 決まっていないものは『未定』で構いません。後から CONTEXT.md を更新できます。」

以下を順に確認する:

| # | 質問 | 回答例 |
|---|------|--------|
| Q3-1 | **ブランチ運用**: どのようにブランチを管理しますか？ | `main` + `feature/xxx` で運用 / `main` のみ（1人開発）|
| Q3-2 | **PRとレビュー**: コードをマージする前に何が必要ですか？ | PR必須・1名承認後マージ / セルフマージ可 / AIレビュー通過後に人間が確認 |
| Q3-3 | **テスト方針**: テストをどう扱いますか？ | ViewModel/Service層に80%以上 / 主要ロジックのみ / CI必須 |
| Q3-4 | **AI活用範囲**: AIエージェントにどこまで任せますか？ | 実装・テスト・PRまで自律 / 実装補助（最終判断は人間）/ ドキュメント生成のみ |

→ 4つの回答をまとめて `CONTEXT.md` の「開発ルール」セクションに記録する

---

### Q4. プラットフォーム

> 「開発対象のプラットフォームを選択してください:
> 1. Windows デスクトップアプリ（WPF / .NET 8）
> 2. Web アプリ（React / ASP.NET Core / .NET 8）
> 3. その他（Phase 1 は別途手動でセットアップ）」

→ Phase 0 ドキュメントを生成したあと、回答に応じて Phase 1 セットアップへ続ける（下記参照）

---

## Phase 0 生成物の構成

### `CONTEXT.md` の構成（このスキルが生成する版）

以下の必須セクションで構成する。

```
## プロジェクト概要（3行）
← Q1の回答から生成

## 技術スタック
← Q2の回答から生成

## 開発ルール
  ブランチ運用          ← Q3-1
  PR・レビュー          ← Q3-2
  テスト方針            ← Q3-3
  AI活用範囲            ← Q3-4

## ドキュメント構成
← 下記「ドキュメント構成」セクションのパス一覧から生成

## 現在フェーズ・優先タスク
  フェーズ: Phase 1（ナレッジベース構築）開始
  次のアクション → exec-plans/active/ 参照

## 参照すべきドキュメント
  docs/00_project/overview.md
  docs/00_project/decisions.md
  docs/03_implementation/invariants.md（実装開始前に必読）
```

---

## Phase 1 セットアップ（Q4の回答に応じて実行）

Phase 0 のドキュメント生成が完了したら、続けて Phase 1 を実行する。

### Q4 = Windows（WPF / .NET 8）の場合

[setup-windows.md](setup-windows.md) の内容に従って Phase 1 ドキュメントを生成する。

### Q4 = Web（React / ASP.NET Core）の場合

[setup-web.md](setup-web.md) の内容に従って Phase 1 ドキュメントを生成する。

### Q4 = その他の場合

Phase 0 完了を報告し、Phase 1 は手動でセットアップするよう案内する。

---

## ドキュメント構成

プロジェクトで管理するドキュメントの全一覧。`必須` は常に作成し、`任意` は条件を満たす場合のみ作成する。

### 必須/任意の判断基準

| ファイル | 必須/任意 | 必要な条件 |
|---------|---------|----------|
| `docs/00_project/overview.md` | 必須 | 常に |
| `docs/00_project/glossary.md` | 任意 | 用語の誤解リスクがある場合 |
| `docs/00_project/decisions.md` | 必須 | 常に（技術選定ADRを記録） |
| `docs/01_requirements/functional/common.md` | 任意 | 複数プラットフォームが存在する場合 |
| `docs/01_requirements/functional/{platform}.md` | 必須 | 常に（プラットフォームごとに1ファイル） |
| `docs/01_requirements/non_functional/common.md` | 任意 | 複数プラットフォームが存在する場合 |
| `docs/01_requirements/non_functional/{platform}.md` | 必須 | 常に |
| `docs/01_requirements/user_stories/common.md` | 任意 | 複数プラットフォームが存在する場合 |
| `docs/01_requirements/user_stories/{platform}.md` | 必須 | 常に |
| `docs/01_requirements/constraints.md` | 必須 | 常に |
| `docs/02_design/architecture.md` | 必須 | 常に |
| `docs/02_design/data_model.md` | 任意 | DBや永続化ストレージを持つ場合 |
| `docs/02_design/api_spec.md` | 任意 | 外部公開APIを持つ場合 |
| `docs/02_design/ui_flows.md` | 任意 | UIを持つ場合 |
| `docs/03_implementation/coding_standards.md` | 必須 | 常に |
| `docs/03_implementation/directory_structure.md` | 必須 | 常に |
| `docs/03_implementation/patterns.md` | 必須 | 常に |
| `docs/03_implementation/dependencies.md` | 必須 | 常に |
| `docs/03_implementation/invariants.md` | 必須 | 常に |
| `docs/04_quality/test_strategy.md` | 必須 | 常に |
| `docs/04_quality/review_checklist.md` | 必須 | 常に |
| `docs/04_quality/security.md` | 任意 | 外部通信・認証・機密データを扱う場合 |
| `docs/04_quality/performance.md` | 任意 | パフォーマンス要件が明示されている場合 |
| `docs/05_operations/environments.md` | 任意 | dev/staging/prod の環境分離が必要な場合 |
| `docs/05_operations/deployment.md` | 必須 | 常に |
| `docs/05_operations/monitoring.md` | 必須 | 常に |
| `docs/06_ai_context/CONTEXT.md` | 必須 | 常に |

### common / platform 分割基準

| 状況 | ルール |
|------|--------|
| プラットフォームが1つだけ | `common.md` は作成しない。すべて `{platform}.md` に記述する |
| プラットフォームが2つ以上 | 全プラットフォームに共通する要件を `common.md` に記述する |
| 「共通だが実装方法が異なる」要件 | `common.md` に要件を記述し、各 `{platform}.md` で実装制約を補記する |

### ドキュメントのフロントマター

各ドキュメントには以下のフロントマターを付与する。

```yaml
---
status: draft    # draft | active | deprecated
tracks:          # （任意）対応するコードのglobパターン
  - src/**/models/**
---
```

`docs/04_quality/test_strategy.md` には追加で以下のフィールドを設定する。

```yaml
---
status: active
test_command: dotnet test              # テスト実行コマンド（プラットフォームに応じて設定）
test_command_fe: npm test              # FE/BE 分離の場合（任意）
test_command_be: dotnet test           # FE/BE 分離の場合（任意）
coverage_threshold: 80                 # カバレッジ下限（任意）
---
```

### テスト保証規約

プロジェクト初期化時に以下の規約を `docs/04_quality/test_strategy.md` および `docs/03_implementation/invariants.md` に記録する。

**INV-T01（全プラットフォーム共通）:**

| # | 条件 | 違反時 |
|---|------|--------|
| INV-T01 | テストを実装の挙動に合わせて修正してはならない。テスト修正は必ず仕様（AC-ID）を根拠とすること | レビュー指摘 |

**AC-ID タグ付け規約:**

受け入れ条件（exec-plan の `## 受け入れ条件`）は `AC-001`, `AC-002`, ... と採番する。
テストコードにはその AC-ID を記載し、`run-tests` スキルがカバレッジを追跡できるようにする。

```csharp
// C# / xUnit
[Trait("AC", "AC-001")]
public void Login_WithInvalidPassword_Returns401() { ... }
```

```typescript
// TypeScript / Vitest
describe('AC-001: 無効なパスワードでのログイン', () => {
  it('401 を返す', () => { ... });
});
```

**`status:` 遷移ルール:**

| 遷移 | トリガー |
|------|---------|
| （新規）→ `draft` | ファイル作成時 |
| `draft` → `active` | PRマージ時。または作成から7日以内にレビューを受けた場合 |
| `active` → `deprecated` | 対応コード/機能が削除された場合。または後継ドキュメントが `active` になった場合 |
| `deprecated` → （削除） | `deprecated` から30日経過後に削除可 |

---

## 完了条件

### Phase 0

- [ ] `docs/00_project/overview.md` が作成されている
- [ ] `docs/00_project/decisions.md` が作成されている（ADRが1件以上ある）
- [ ] `docs/06_ai_context/CONTEXT.md` が作成されている
- [ ] `CONTEXT.md` に「開発ルール」セクションがあり、Q3の4項目が記載されている

### Phase 1（プラットフォームに応じた条件を満たすこと）

- Windows: [setup-windows.md](setup-windows.md) の完了条件を参照
- Web: [setup-web.md](setup-web.md) の完了条件を参照

完了後にエージェントが出力する報告:

```
=== Phase 0 → Phase 1 完了 ===

作成したファイル:
  docs/00_project/overview.md
  docs/00_project/decisions.md
  docs/06_ai_context/CONTEXT.md
  （+ Phase 1 で生成したファイル一覧）

次のフェーズ（Phase 2: 要件定義・設計）でやること:
  docs/00_project/glossary.md         用語定義
  docs/01_requirements/constraints.md 制約条件

exec-plans/active/ に Phase 2 の実行計画を作成することを推奨します。
```
