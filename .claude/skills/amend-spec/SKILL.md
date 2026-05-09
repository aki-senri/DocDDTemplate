---
name: amend-spec
description: |
  実装済みの仕様（User Story / exec-plan）を変更するためのスキル。
  変更内容を確認し、コードとの乖離を check-doc-freshness で検証した上で、
  Decision Log に変更理由を記録する。
disable-model-invocation: true
---

# Skill: Amend Spec

> **いつ実行するか**: 実装済みのコードに対応する仕様（US / exec-plan の AC）を変更するとき
>
> **目的**: 仕様変更の理由を追跡可能にし、コードとドキュメントの乖離を検出・解消する
>
> **実装前の仕様変更には使わない**: コードがまだない場合は US / exec-plan を直接編集して Decision Log に理由を記録するだけで十分

---

## What this skill does

1. 変更対象の US / exec-plan を特定するインタビューを行う
2. 変更内容と理由を確認する
3. 対象ドキュメントを編集する
4. `check-doc-freshness` を呼び出してコードとの乖離を確認する
5. exec-plan の Decision Log に変更理由を記録する
6. コードへの影響がある場合は新しい exec-plan の作成を提案する

---

## Pre-check

実行前に以下を確認する：

1. `exec-plans/active/` に active な exec-plan が存在するか確認する
2. `docs/01_requirements/user_stories/` に US ファイルが存在するか確認する
3. 変更対象ファイルの `tracks:` フィールドを読み取り、追跡対象のコードパスを把握する

---

## Interview

質問は **1つずつ、順番に** 行う。

| # | 質問 | 用途 |
|---|------|------|
| Q1 | 変更対象はどの文書ですか？（US-XXX / exec-plan ファイル名で指定） | 対象ファイルの特定 |
| Q2 | どの AC / 条件を変更しますか？（AC 番号や箇条書きの内容） | 変更箇所の特定 |
| Q3 | 変更後の内容を教えてください | 新しい仕様の内容 |
| Q4 | 変更理由を教えてください（Decision Log に記録します） | 追跡情報 |

---

## Steps

### Step 1: 対象ドキュメントの編集

Q1・Q2・Q3 の回答に基づき、対象の US または exec-plan ファイルを編集する。

- AC のチェックボックス状態（`[ ]` / `[x]`）は維持する
- 変更前の内容はコメントアウトせず削除する（Git 履歴が記録を保持する）

### Step 2: check-doc-freshness の実行

このスキルは実装済みコードに対応する仕様を変更する場面で使うため、常に実行する。

```
/check-doc-freshness
```

乖離が検出された場合：
- 乖離の内容をユーザーに報告する
- コード修正が必要かどうかをユーザーに確認する
- コード修正が必要な場合は `/create-exec-plan` で新しい実行計画を作成するよう提案する

### Step 3: Decision Log への記録

記録先は以下の優先順で選ぶ：

1. Q1 で指定したファイルが exec-plan の場合 → そのファイルの `## Decision Log` に記録
2. Q1 が US ファイルで、関連する active な exec-plan が存在する場合 → その exec-plan の `## Decision Log` に記録
3. Q1 が US ファイルで、関連する exec-plan が存在しない場合 → US ファイル末尾に `## Decision Log` セクションを追加して記録

以下の形式で追記する：

```markdown
### YYYY-MM-DD
- 仕様変更: {Q2 で指定した AC / 条件}
  - 変更理由: {Q4}
  - 変更前: {変更前の内容の要約}
  - 変更後: {Q3}
  - コードへの影響: {あり（新 exec-plan 要） / なし}
```

---

## Completion criteria

- [ ] 対象ドキュメント（US または exec-plan）が更新されている
- [ ] Decision Log に変更理由が記録されている
- [ ] `check-doc-freshness` を実行済みである

Final report output:

```
=== 仕様変更完了 ===

変更ファイル : {対象ファイルパス}
変更箇所     : {AC 番号 / 条件}
Decision Log : 記録済み
乖離チェック : 実行済み
コードへの影響: {あり（/create-exec-plan を推奨） / なし}
```
