# DocDD Template

**Document-Driven Development（ドキュメント駆動開発）** のスターターテンプレートです。  
Claude Code と組み合わせることで、AIエージェントがドキュメントを読みながら自律的に開発を進められる環境を構築します。

> English version: [README.md](README.md)

---

## DocDD とは

コードと常に同期した「生きたドキュメント」を中心に置き、AIエージェントが開発フロー全体を通じて正しい文脈で動けるようにする開発手法です。

```
ドキュメント = 定義（何を作るか）
スキル       = 操作（どうやって進めるか）
settings.json = トリガー（いつ自動実行するか）
```

- **CONTEXT.md**（≤50行）が常に「今どこにいるか」を示すナビゲーションマップとして機能します
- `tracks:` フィールドがドキュメントとコードの対応を定義し、乖離を自動検出します
- フェーズ0〜4の構造化されたワークフローで、要件定義から運用まで一貫して管理します

---

## 開発フェーズ

| フェーズ | 内容 | 主な成果物 |
|---------|------|-----------|
| Phase 0 | プロジェクト初期化 | CONTEXT.md, overview.md, decisions.md |
| Phase 1 | ナレッジベース構築 | invariants.md, patterns.md, architecture.md |
| Phase 2 | 要件定義・仕様・設計 | user_stories, app_spec.md, api_spec.md, data_model.md |
| Phase 3 | 実装 | コード + ドキュメントの同期維持 |
| Phase 4 | 品質・運用 | review_checklist.md, test_strategy.md |

---

## クイックスタート

### 1. テンプレートをコピーする

このリポジトリを新しいプロジェクトのリポジトリにコピーするか、テンプレートとして使用します。

```
.claude/                   ← そのまま残す（スキル・設定）
```

### 2. プロジェクトを初期化する

Claude Code で以下を実行します：

```
/init-project
```

インタビュー形式でプロジェクト概要・技術スタック・開発ルール・プラットフォームを収集し、Phase 0 → Phase 1 のドキュメントを自動生成します。

### 3. 機能実装を始める

```
/create-requirements ← User Story・AC 条件を定義（任意・推奨）
/create-spec         ← アプリ仕様を起草（任意・小さな変更ならスキップ）
/create-exec-plan    ← 実行計画を作成（AC-001~ を定義）
/start-feature       ← 実装前の確認・ブランチ作成
/run-exec-plan       ← AC を1つずつ自走実装（opt-in）
   （手動で進める場合: コードを書く → /check-doc-freshness → /check-invariants → /run-tests）
/pre-pr              ← PR前の総合チェック
/complete-exec-plan  ← 計画を完了に移動
```

> 最小ループに必須なのは `create-exec-plan` 以降のみ。`create-requirements` / `create-spec` は
> 「何を作るか」が曖昧なときやチームで共有するときに推奨。

---

## 人とAIの役割分担

DocDD は責任を分ける ── **「決定」は人、「実行」は AI**。

- **人が起動する**のは統治・判断のスキル（要件定義、AC 凍結、自走起動、レビュー、マージ）。
- **AI が内部で回す**のは検証・支援のスキル。人は直接呼ばず、上位スキルが自動で回す。

詳しい責任分担・人間視点のフロー・どのスキルがどれを呼ぶかは
[`ONBOARDING.ja.md` §6-0](ONBOARDING.ja.md#6-0-人が何をするか責任分担)
（English: [`ONBOARDING.md` §6-0](ONBOARDING.md#6-0-what-the-human-does-responsibility-split)）を参照。
スキル依存関係を含む全体フローは [`SKILL_FLOW.md`](SKILL_FLOW.md) にあります。

---

## スキル一覧

スキルの実行は Claude Code のチャットで `/スキル名` と入力します。

### 人が直接起動する（統治・判断）

| スキル | 用途 |
|-------|------|
| `init-project` | プロジェクト初期化（Phase 0 → Phase 1）。導入時に一度 |
| `create-requirements` | User Story・受け入れ条件・制約を定義（`docs/01_requirements/`） |
| `create-spec` | 承認済み要件からアプリ仕様（*何をするか*）を起草（`docs/02_spec/`、`status: draft`。人間承認が必要） |
| `create-exec-plan` | 受け入れ基準（AC-001~）を持つ実行計画を新規作成 |
| `start-feature` | 実装開始前の確認・ブランチ名決定（機能ごとに一度） |
| `run-exec-plan` | AC を1つずつ自走実装（実装→テスト→修正→次）。停止条件でのみ HALT（opt-in） |
| `pre-pr` | PR前の総合チェック（invariants / doc-freshness / doc-invariants / review_checklist / run-tests / exec-plan更新） |
| `complete-exec-plan` | 実行計画を `active/` から `completed/` へ移動 |
| `promote-spec` | 次バージョン仕様（`spec/<label>` ブランチ）を現ターゲットへ昇格（スプリント境界） |
| `gc` | 定期ガベージコレクション（ドキュメント・アーキテクチャの健全性チェック。週次） |

### AI が内部で回す（検証・支援）

| スキル | 用途 |
|-------|------|
| `run-tests` | テスト実行・仕様照合（テスト失敗時は仕様照合ゲートで対処方針を決定） |
| `check-invariants` | `invariants.md` の不変条件を実装コードに対して検証 |
| `check-doc-freshness` | 変更されたコードに対応するドキュメントの鮮度チェック |
| `check-doc-invariants` | ドキュメントの構造ルール（doc-INV）違反をチェック |
| `update-context` | CONTEXT.md を現在の状態に更新 |

### 任意の独立レビュー（必要に応じて人が起動・起草文脈を持たない）

| スキル | 用途 |
|-------|------|
| `doc-review` | 独立エージェントが要件・仕様ドキュメントをレビュー（AC の検証可能性・網羅性・参照方向） |
| `docode-review` | 独立エージェントが変更コードを AC と一般品質に対してレビュー |

> `run-tests` はモデル起動可（呼び出し側は Skill ツールで起動）。他の内部スキルは上位スキルが `SKILL.md` の手順をインライン実行する。CLAUDE.md「検証スキルの呼び出しポリシー」を参照。

---

## ディレクトリ構成

```
プロジェクトルート/
├── .claude/
│   ├── settings.json          # フック設定（コード変更時の自動リマインド）
│   └── skills/                # 各スキルの定義
│       ├── init-project/
│       ├── create-requirements/
│       ├── create-spec/
│       ├── create-exec-plan/
│       ├── start-feature/
│       ├── run-exec-plan/
│       ├── pre-pr/
│       ├── complete-exec-plan/
│       ├── promote-spec/
│       ├── run-tests/
│       ├── check-invariants/
│       ├── check-doc-freshness/
│       ├── check-doc-invariants/
│       ├── doc-review/
│       ├── docode-review/
│       ├── update-context/
│       └── gc/
├── docs/                      # ← init-project が生成（初期は存在しない）
│   ├── 00_project/            # overview.md, decisions.md, glossary.md
│   ├── 01_requirements/       # constraints.md, user_stories/
│   ├── 02_spec/               # app_spec.md（アプリが何をするか）
│   ├── 03_design/             # architecture.md, data_model.md, api_spec.md
│   ├── 04_implementation/     # invariants.md, patterns.md, dependencies.md
│   ├── 05_quality/            # test_strategy.md, review_checklist.md
│   ├── 06_operations/         # environments.md, monitoring.md
│   └── 07_ai_context/         # CONTEXT.md（ナビゲーションマップ）
└── exec-plans/                # ← create-exec-plan が生成（初期は存在しない）
    ├── active/                # 進行中の実行計画
    └── completed/             # 完了した実行計画
```

---

## ハーネス（自動化）

`.claude/settings.json` に PostToolUse フックが設定されています。

| トリガー | リマインド内容 |
|---------|--------------|
| `exec-plans/completed/` を編集 | `update-context` の実行を促す |
| `exec-plans/active/` を編集 | CONTEXT.md の更新確認を促す |
| テストファイルを編集（`*.Test.cs` / `*.test.ts` / `*.spec.ts` 等） | 変更が仕様（AC-ID）に基づいているか確認を促す |
| コードファイルを編集 | `check-doc-freshness` の実行と、テスト失敗時の `run-tests` による仕様照合を促す |

コードファイルの検出は言語非依存（`.md` `.json` `.yaml` 等のドキュメント・設定ファイル以外をコードとして扱います）。

---

## テスト保証（仕様照合ゲート）

DocDD では、テストを「仕様の実行可能な表現」として位置づけます。

### 仕様照合ゲート

テストが失敗したとき、すぐにテストを修正してはいけません。
`run-tests` スキルが以下の判断ゲートを提示します：

```
A) テストは仕様を正しく表現している
   → 実装にバグがある。実装を修正する。

B) 仕様が変更され、テストが古くなっている
   → 仕様（AC-ID）に基づいてテストを修正する。
   ⚠️ 実装の挙動に合わせてテストを修正することは禁止（INV-T01）
```

### AC-ID によるトレーサビリティ

受け入れ条件（exec-plan の `AC-001`, `AC-002`, ...）をテストコードに記載し、
仕様とテストの対応を追跡します。

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

`run-tests` スキルは、全 AC-ID にテストが対応しているかカバレッジを確認します。

### フロー内での実行タイミング

| タイミング | 目的 |
|-----------|------|
| `start-feature` 開始時 | ベースライン確認（グリーン状態で実装を始める） |
| 実装中（随時） | `/run-tests` で随時確認 |
| `pre-pr` | PR前の最終確認（失敗・未カバー AC があれば保留） |
| `complete-exec-plan` | 全 AC-ID テスト通過を完了の必須条件とする |

---

## ドキュメントとコードの同期

各ドキュメントのフロントマターに `tracks:` フィールドを設定することで、対応するコードファイルを定義します。

```yaml
---
status: active
tracks:
  - src/**/models/**
  - src/**/repositories/**
---
```

`check-doc-freshness` スキルがこのフィールドを読み取り、コード変更時に対応ドキュメントの更新漏れを検出します。

---

## 詳細仕様

各スキルの `SKILL.md` を参照してください。ドキュメント構成・必須/任意の判断基準・statusライフサイクル・exec-planテンプレートは `init-project/SKILL.md` に集約されています。

---

## ライセンス

[MIT](LICENSE)
