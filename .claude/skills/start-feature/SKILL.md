---
name: start-feature
description: |
  機能実装を開始するときの準備スキル。
  exec-plans から作業を選択し、必要なドキュメントを確認してから実装に入る。
  「何を実装するか迷っている」「実装前に何を確認すべきか」というときに使う。
disable-model-invocation: true
---

# スキル: 機能実装の開始

> **実行タイミング**: `exec-plans/active/` から新しい作業を選んで実装を始めるとき
>
> **目的**: 実装前の確認漏れを防ぎ、エージェントが正しい前提で実装を開始できる状態を作る。
>
> **前提**:
> - `exec-plans/active/` に実行中の計画が存在すること
> - Phase 1（ナレッジベース構築）が完了していること（`docs/03_implementation/invariants.md` が存在すること）

---

## このスキルがすること

1. 実行計画を確認・選択する
2. 実装に必要なドキュメントを読み込む
3. ブランチ名を決定する
4. 作業開始を進捗ログに記録する

---

## 手順

### ステップ 1: 実行計画の確認

`exec-plans/active/` 内のファイルを一覧表示し、作業する計画をユーザーに確認する。

- 計画が1件のみの場合はそれを選択する
- 計画が複数の場合は選択を促す
- 計画がない場合は `create-exec-plan` スキルの実行を促して終了する

### ステップ 2: 必須ドキュメントの読み込み

以下のドキュメントを読み込み、実装前提を確認する。

| ドキュメント | 確認内容 |
|-------------|---------|
| `docs/06_ai_context/CONTEXT.md` | 現在フェーズ・開発ルール・技術スタック |
| `docs/03_implementation/invariants.md` | 守るべき不変条件（INV-XXX） |
| 選択した `exec-plans/active/*.md` | 受け入れ条件・タスク分解 |

プラットフォームに応じて以下も読み込む:

| 条件 | 追加で読むドキュメント |
|------|-------------------|
| 要件定義フェーズの場合 | `docs/01_requirements/user_stories/{platform}.md` |
| 設計が必要な場合 | `docs/02_design/architecture.md` |
| Web アプリの場合 | `docs/02_design/api_spec.md` |

### ステップ 3: ブランチ名の決定

CONTEXT.md の「ブランチ運用」ルールに従い、ブランチ名を提案する。

- 標準的なパターン: `feature/{exec-plan-name}`
- 例: `feature/user-auth`

### ステップ 4: 進捗ログの更新

選択した `exec-plans/active/*.md` に以下を追記する。

```markdown
### YYYY-MM-DD
- 実装開始。ブランチ: feature/{name}
```

---

## 実装順序のガイド

**実装順序の基本原則**: 依存される側（安定した層）から先に実装し、依存する側（不安定な層）を後に実装する。
具体的な順序は `docs/03_implementation/patterns.md` の定義に従う。

**一般的なパターン:**
```
データ構造（Model / Entity / Type）
  → データアクセス層（Repository / DAO）のインターフェース
  → ビジネスロジック層（Service / UseCase）のインターフェース
  → 各層の実装
  → UI / プレゼンテーション層
```

> **例（レイヤードアーキテクチャ + MVVM の場合）:**
> ```
> Model → Repository（Interface）→ Service（Interface）
>          ↓                         ↓
>         Repository（実装）     Service（実装）→ ViewModel → View
> ```
>
> **例（Web API + SPA の場合）:**
> ```
> BE: Entity → Repository（Interface）→ Service → Controller
> FE: 型定義 → API クライアント → ロジック層 → UI コンポーネント → ページ
> ```

実装順序の詳細と、このプロジェクト固有のパターンは `docs/03_implementation/patterns.md` を参照。

---

## 完了条件

- [ ] 実行計画を選択・確認した
- [ ] `CONTEXT.md`・`invariants.md`・選択した実行計画を読み込んだ
- [ ] ブランチ名を確定した
- [ ] 実行計画の進捗ログに「実装開始」を記録した

完了後にエージェントが出力する報告:

```
=== 実装開始の準備が完了しました ===

作業計画 : exec-plans/active/YYYY-MM-{name}.md
ブランチ  : feature/{name}
確認済み : CONTEXT.md / invariants.md / 実行計画

最初のタスク: {exec-planのタスク分解の先頭項目}
```
