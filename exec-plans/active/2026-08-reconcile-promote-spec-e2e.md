---
status: active
created: 2026-08-02
completed:
---

# reconcile-promote-spec-e2e

## Goal & Scope

`promote-spec` が生成する reconcile プランのテンプレートを、`create-exec-plan` の `[E2E]` AC 規約
（#27）と red-first（#22）に追従させる。#27 は「reconcile プランは `[E2E]` AC を持つ」を
`create-exec-plan` の表に書いたが、実際に reconcile プランを**生成する側**の `promote-spec` を
更新しなかったため、規約どおりに使うと必ず規約違反のプランが生まれる状態だった。

## Acceptance Criteria

- [x] AC-003: （再オープン: `exec-plans/completed/2026-08-goal-image-e2e.md`）`promote-spec` が
      生成する reconcile プランのテンプレートに `[E2E]` AC 行と「機能 AC が全て `- [x]` でも
      `[E2E]` が緑でなければ完了ではない」の注記があり、どの AC-ID を `[E2E]` に使うか
      （新 spec の `E2E-NNN` が指す既存 ID を使い、ID を捏造しない）が明記され、
      Completion criteria がその存在を確認する状態にする

> このプランは documentation-only（`git diff --name-only` が `.claude/skills/**` と
> `exec-plans/**` のみ）のため `[E2E]` AC を持たない。Decision Log の
> `E2E: n/a (documentation-only)` を参照。

## Task Breakdown

- [x] AC-003 — `.claude/skills/promote-spec/SKILL.md` の Step 7 テンプレート・補足・
      Completion criteria・報告書式

## Progress Log

### 2026-08-02
- Plan created
- AC-003 完了
- PR #31 作成（3プラン合同）。マージ後に `/complete-exec-plan` を実行する

## Decision Log

### 2026-08-02

- **E2E: n/a (documentation-only)**。変更対象はスキル定義と exec-plan のみで、機能を実装する
  ファイルを含まない。
- **AC-003 は `exec-plans/completed/2026-08-goal-image-e2e.md`（PR #29、`0e677b3`）の同 AC-ID を
  再オープンしたもの**。CLAUDE.md「現バージョン修正による stale の扱い」に従い、完了済みプランには
  追記せず本プラン側に記録する。
  - stale になった理由: AC-003 は「`create-exec-plan` に E2E-AC 規約を追加する」という形で書かれて
    おり、規約を**適用する側**（`promote-spec` の reconcile テンプレート）を含んでいなかった。
    結果、`create-exec-plan` の表は「reconcile プランは `[E2E]` AC が Required」と述べているのに、
    `promote-spec` が生成するプランには `[E2E]` AC が無く、`run-tests` / `pre-pr` /
    `check-doc-invariants` が ⚠️ を出す（＝規約どおり運用すると必ず警告が出る）状態だった。
  - ルーティングの判断: これは *次に作りたい物* ではなく *今ある規約の適用漏れ* であり、
    スコープを広げない是正のため `spec/<label>` ではなく `main` 側の不備修正として扱う。
- **AC-003 done.** `promote-spec` Step 7 の reconcile テンプレートに `[E2E]` AC 行と完了条件の注記を
  追加。あわせて次の2点を補足として明記した。
  1. **ID を捏造しない**。reconcile プランは既存 AC-ID の再オープンであり、`[E2E]` AC も新 spec の
     `E2E-NNN` が指す既存 ID（通常は再オープンした ID のいずれか）を使う。どの再オープン AC も
     通しフローを所有していない場合は、`/create-exec-plan` で人が決める。
     ID を新規に振ると DOC-INV-004（US の `ac_ids:` への追跡）が壊れる。
  2. **red-first の扱い**。spec が変わった AC は「preservation AC」の免除に該当しない。
     新しい AC 本文から期待値を書き直し、赤を観測してから実装する。テスト変更を promotion label と
     AC-ID に紐づけて記録することが、INV-T01 違反でないことの根拠になる。
- **ファイル名を `2026-08-reconcile-2.md` にした理由**。CLAUDE.md の命名規約は in-version の
  reconcile を `YYYY-MM-reconcile.md` と定めているが、同名のプランが同月内に既に完了・
  `exec-plans/completed/` へ移動済みで、同名で起票すると完了時に上書き衝突する。
  規約の意図（サイクルごとに閉じて新規を起こす）は満たしつつ連番で回避した。
  **同月内に2本目の in-version reconcile が必要になる場合の命名は規約に無い** ため、
  次のサイクルで CLAUDE.md 側に追記するか、連番を正式な規約にするかは人の判断に委ねる。
