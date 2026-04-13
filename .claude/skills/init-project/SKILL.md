---
name: init-project
description: Initialize a new project. Interviews the user to capture project overview, tech stack, and development workflow rules, then creates overview.md, decisions.md, and CONTEXT.md. Run once at project start (Phase 0).
disable-model-invocation: true
---

# スキル: プロジェクト初期化

> **実行タイミング**: プロジェクト開始時に一度だけ実行する（`document_architecture.md` Phase 0）
>
> **目的**: チームメンバー（人間・AIエージェント双方）が「このプロジェクトをどう動かすか」を
> 一つのファイル（CONTEXT.md）から理解できる状態を作る。
>
> **前提**: リポジトリが作成済みで、`document_architecture.md` が配置されていること。

---

## このスキルが作るもの

| ファイル | 役割 | 内容の決まり方 |
|---------|------|--------------|
| `docs/00_project/overview.md` | プロジェクトの目的・スコープ・技術スタック | Q1・Q2の回答から生成 |
| `docs/00_project/decisions.md` | 技術選定の意思決定ログ（ADR形式） | Q2の回答から生成 |
| `docs/06_ai_context/CONTEXT.md` | ナビゲーションマップ（開発ルール含む） | 全回答から生成 |

ファイルの構成は `document_architecture.md` の定義に従う。
内容はインタビューの回答をもとにエージェントが生成する（固定テンプレートではない）。

---

## インタビュー

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

## 生成物の構成

### `CONTEXT.md` の構成（このスキルが生成する版）

`document_architecture.md` が定義する必須セクションに「開発ルール」を加えた構成。

```
## プロジェクト概要（3行）
← Q1の回答から生成

## 技術スタック
← Q2の回答から生成

## 開発ルール          ← このスキルで追加されるセクション
  ブランチ運用          ← Q3-1
  PR・レビュー          ← Q3-2
  テスト方針            ← Q3-3
  AI活用範囲            ← Q3-4

## ドキュメント構成
← document_architecture.md の定義から生成（パス一覧）

## 現在フェーズ・優先タスク
  フェーズ: Phase 1（ナレッジベース構築）開始
  次のアクション → exec-plans/active/ 参照

## 参照すべきドキュメント
  docs/00_project/overview.md
  docs/00_project/decisions.md
  docs/03_implementation/invariants.md（実装開始前に必読）
```

---

## 完了条件

以下をすべて満たしたらスキル完了とし、ユーザーに報告する。

- [ ] `docs/00_project/overview.md` が作成されている
- [ ] `docs/00_project/decisions.md` が作成されている（ADRが1件以上ある）
- [ ] `docs/06_ai_context/CONTEXT.md` が作成されている
- [ ] `CONTEXT.md` に「開発ルール」セクションがあり、Q3の4項目が記載されている
- [ ] `CONTEXT.md` の現在フェーズが「Phase 1」になっている

完了後にエージェントが出力する報告:

```
=== Phase 0 完了 ===

作成したファイル:
  docs/00_project/overview.md
  docs/00_project/decisions.md
  docs/06_ai_context/CONTEXT.md

次のフェーズ（Phase 1: ナレッジベース構築）でやること:
  docs/00_project/glossary.md         用語定義
  docs/01_requirements/constraints.md 制約条件
  docs/03_implementation/invariants.md 不変条件（初版）

exec-plans/active/ に Phase 1 の実行計画を作成することを推奨します。
```
