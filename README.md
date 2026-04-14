# DocDD Template

**Document-Driven Development（ドキュメント駆動開発）** のスターターテンプレートです。  
Claude Code と組み合わせることで、AIエージェントがドキュメントを読みながら自律的に開発を進められる環境を構築します。

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
| Phase 2 | 要件定義・設計 | user_stories, api_spec.md, data_model.md |
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
/create-exec-plan   ← 実行計画を作成
/start-feature      ← 実装前の確認・ブランチ作成
（実装）
/pre-pr             ← PR前の総合チェック
/complete-exec-plan ← 計画を完了に移動
```

---

## スキル一覧

| スキル | 用途 |
|-------|------|
| `init-project` | プロジェクト初期化（Phase 0 → Phase 1） |
| `create-exec-plan` | 実行計画（exec-plan）の新規作成 |
| `start-feature` | 実装開始前の確認・ブランチ名決定 |
| `pre-pr` | PR前の総合チェック（invariants / doc-freshness / review_checklist / exec-plan更新） |
| `complete-exec-plan` | 実行計画を `active/` から `completed/` へ移動 |
| `check-invariants` | `invariants.md` の不変条件を実装コードに対して検証 |
| `check-doc-freshness` | 変更されたコードに対応するドキュメントの鮮度チェック |
| `update-context` | CONTEXT.md を現在の状態に更新 |
| `gc` | 定期ガベージコレクション（ドキュメント・アーキテクチャの健全性チェック） |

スキルの実行は Claude Code のチャットで `/スキル名` と入力します。

---

## ディレクトリ構成

```
プロジェクトルート/
├── .claude/
│   ├── settings.json          # フック設定（コード変更時の自動リマインド）
│   └── skills/                # 各スキルの定義
│       ├── init-project/
│       ├── create-exec-plan/
│       ├── start-feature/
│       ├── pre-pr/
│       ├── complete-exec-plan/
│       ├── check-invariants/
│       ├── check-doc-freshness/
│       ├── update-context/
│       └── gc/
├── docs/                      # ← init-project が生成（初期は存在しない）
│   ├── 00_project/            # overview.md, decisions.md, glossary.md
│   ├── 01_requirements/       # constraints.md, user_stories/
│   ├── 02_design/             # architecture.md, data_model.md, api_spec.md
│   ├── 03_implementation/     # invariants.md, patterns.md, dependencies.md
│   ├── 04_quality/            # test_strategy.md, review_checklist.md
│   ├── 05_operations/         # environments.md, monitoring.md
│   └── 06_ai_context/         # CONTEXT.md（ナビゲーションマップ）
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
| コードファイルを編集 | `check-doc-freshness` の実行を促す |

コードファイルの検出は言語非依存（`.md` `.json` `.yaml` 等のドキュメント・設定ファイル以外をコードとして扱います）。

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
