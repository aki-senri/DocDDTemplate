---
status: active
created: 2026-08-02
completed:
---

# reconcile

## Goal & Scope

`create-exec-plan` が documentation-only プランに認めていた「`[E2E]` AC をウォークスルーで検証してよい」
免除を削除し、documentation-only プランは `E2E: n/a (documentation-only)` のみとする（`[E2E]` AC を置かない）。
この免除は `run-tests` / `pre-pr` / `complete-exec-plan` / `run-exec-plan` の4ゲートが認めておらず、
規約どおりに書いたプランが必ず後段でブロックされる自己矛盾になっていた。

## Acceptance Criteria

- [x] AC-003: （再オープン: `exec-plans/completed/2026-08-goal-image-e2e.md`）`create-exec-plan` から
      documentation-only のウォークスルー免除を削除し、「documentation-only プランは `[E2E]` AC を
      置かず `E2E: n/a (documentation-only)` を Decision Log に記録する」を規約として明記した状態にする。
      あわせて `ac-readiness.md` の R4 記述から「doc-only プランが `[E2E]` AC を持つ場合はそれにアンカーする」
      を削除する
- [x] AC-006: （再オープン: 同上）`doc-review` と `check-doc-invariants` が新しい規約と一致した状態にする。
      具体的には、documentation-only プランが `[E2E]` AC を持つ状態を `doc-review` が指摘対象とし、
      `check-doc-invariants` DOC-INV-006 が ⚠️ 警告として検出する（4ゲートが ❌ でブロックする状況を
      ドキュメント側が黙認しない。ただしドキュメントゲートをテストゲートより厳しくしないため警告に留める）

> このプランは documentation-only（`git diff --name-only` が `.claude/skills/**` と `*.md` のみ）のため
> `[E2E]` AC を持たない。Decision Log の `E2E: n/a (documentation-only)` を参照。

## Task Breakdown

- [x] AC-003 — `.claude/skills/create-exec-plan/SKILL.md`（免除段落の削除・When it is required 表・
      Completion criteria）と `.claude/skills/create-exec-plan/ac-readiness.md`（R4 の doc-only 記述）
- [x] AC-006 — `.claude/skills/doc-review/SKILL.md` §2b と
      `.claude/skills/check-doc-invariants/SKILL.md` DOC-INV-006（判定基準・重大度表・Step 7・報告書式）
- [x] 進行中プラン `2026-08-ac-readiness-gate.md` の `[E2E]` AC-007 を新規約に合わせる（同プランの
      Decision Log 側に記録）

## Progress Log

### 2026-08-02
- Plan created
- AC-003 完了
- AC-006 完了
- 進行中プラン `2026-08-ac-readiness-gate.md` の AC-007 を機能 AC に是正

- PR #30 作成（`2026-08-ac-readiness-gate.md` と合同）。マージ後に `/complete-exec-plan` を実行する
- PR #30 のレビュー対応（Copilot 3 件のうち 1 件が本プラン分）
## Decision Log

### 2026-08-02

- **E2E: n/a (documentation-only)**。本プランの変更対象は `.claude/skills/**` と `exec-plans/**`、
  すなわち機能を実装するファイルを1つも含まない。新しい規約に従い `[E2E]` AC を置かない
  （この判断自体が新規約の最初の適用例になる）。
- **AC-003 / AC-006 は `exec-plans/completed/2026-08-goal-image-e2e.md`（PR #29、`0e677b3` でマージ）の
  同 AC-ID を再オープンしたもの**。それらの実装は `main` 上の本不備修正によって stale になる。
  CLAUDE.md「現バージョン修正による stale の扱い」に従い、完了済みプランには追記せず本プラン側に記録する。
  - AC-003 が stale になる理由: 同 AC が追加した `create-exec-plan` の E2E-AC 規約に、
    ウォークスルー免除の段落が含まれていた。
  - AC-006 が stale になる理由: 同 AC が新設した DOC-INV-006 と `doc-review` §2b は、
    「documentation-only なら `[E2E]` AC が無くてよい」までは書いたが、
    「documentation-only なのに `[E2E]` AC がある」状態を未定義のまま残していた。
- **ルーティングの判断（CLAUDE.md「変更のルーティング」）**: これは *次に作りたい物* ではなく
  *今ある規約の誤り* であり、スコープを広げない是正のため `spec/<label>` ではなく `main` 側の
  不備修正として扱う。
- **AC readiness（Q3c）の判定**: AC-003 = READY（R1 単一の終状態「免除が削除され規約が明記された状態」/
  R2 given: doc-only プラン, when: E2E AC の要否を判断, then: `[E2E]` AC を置かず n/a を記録 /
  R3 対象ファイルと削除対象の段落が特定済み / R4 n/a（documentation-only）/ R5 手段の指定なし）。
  AC-006 = READY（同様。⚠️ 警告という重大度まで本文で確定させている）。

- **AC-003 done.** `create-exec-plan` からウォークスルー免除の段落を削除し、代わりに
  「documentation-only プランは `[E2E]` AC を定義しない」と、その**機械的な理由**（4ゲートが
  「`[E2E]` AC あり・テスト無し」を保留として扱い、ドキュメント変更には渡せるテストが無い＝
  完了できないプランになる）を明記。追跡したい検証作業は通常の機能 AC（観測可能な結果）で書く
  という代替も併記した。`When it is required` 表の documentation-only 行を
  「Not required」→「**Must not** carry one」に変更、テンプレートに documentation-only 用の
  コメントを追加、Completion criteria も「`[E2E]` AC が無いこと」を明示。
  `ac-readiness.md` の R4 記述からは「doc-only プランが `[E2E]` AC を持つ場合はそれにアンカーする」を削除。
- **AC-006 done.** `doc-review` §2b に逆方向の指摘（documentation-only なのに `[E2E]` AC がある）を追加。
  `check-doc-invariants` DOC-INV-006 は判定を4通りの表（`[E2E]` AC の有無 × `E2E: n/a` 記録の有無）に
  整理し、矛盾する組み合わせを ⚠️ 警告として追加。重大度を violation にしなかったのは、
  同じ状況を4ゲートが既に ❌ でブロックしており、ドキュメントゲートをテストゲートより厳しくしない
  という #27 のレビュー指摘（PR #29）で確立した原則に従うため。
- **本プラン適用後の再照合（4項目）**: ①`create-exec-plan` にウォークスルー免除の記述が残っていない
  ②`ac-readiness.md` の doc-only 記述が新規約と一致 ③`doc-review` / `check-doc-invariants` が
  「doc-only なのに `[E2E]` AC」を検出する ④`run-tests` / `pre-pr` / `complete-exec-plan` /
  `run-exec-plan` は変更不要（元から `[E2E]` AC ありでテスト無しを保留としており、新規約と矛盾しない）。
  4項目とも PASS。

- **AC 行の記法を修正**。当初 `- [x] AC-003（再オープン: ...）: ...` と書いていたが、
  `.claude/hooks/spec-gate.py` は `AC-(\d{3}):` で解析するため、ID の直後にコロンが来ない書き方だと
  **AC がゲートから見えなくなる**（`check-doc-invariants` の Step 5 も `- \[[ x]\] AC-\d+:` で走査する）。
  `create-exec-plan` が「別 ID 系列を作るな」と警告しているのと同じ落とし穴を、括弧の位置で踏んでいた。
  `- [x] AC-003: （再オープン: ...）...` に修正。再オープンの注記を ID とコロンの間に置かないこと。
  同じ落とし穴を次に踏ませないため、`create-exec-plan` の Notation 段落（既に「別 ID 系列を作るな」と
  警告している箇所）に「ID とコロンの間に何も置かない。注記はコロンの後ろへ」を1文追記した。
  本プランのどの AC にも属さない変更だが、CLAUDE.md「現バージョンの不備修正は main に直接」に該当し、
  スコープを広げない1文であるため AC を追加せずここに記録する。
- **サマリ表3件も追従**。`CLAUDE.md` スキル一覧・`README.md` / `README.ja.md` のスキル表が
  「`create-exec-plan` は最低1本の `[E2E]` AC を定義する」と無条件に書いており、新規約
  （documentation-only は置かない）と食い違うため但し書きを追加。AC-003 の「規約として明記した状態」に
  含まれる追従とみなす。
- **再照合（最終）**: `grep -rn "walkthrough|ウォークスルー" --include=*.md`（exec-plans を除く）の結果は
  `create-exec-plan` の禁止文2行のみ。免除の記述はリポジトリ内に残っていない。
  `exec-plans/active/*.md` は2プランとも `[E2E]` AC なし・`E2E: n/a` 記録あり＝ DOC-INV-006 は ℹ️。
  両プランの AC 行は `AC-(\d{3}):` で解析可能（reconcile: 003/006、ac-readiness-gate: 001〜007）。
- **PR #30 レビュー対応（Copilot、本プラン分 1 件）**。`SKILL_FLOW.md` の PLAN ノードが
  「`create-exec-plan` は最低1本の `[E2E]` AC を定義する」と無条件に書いたままで、本プランで変更した
  規約（documentation-only は置かない）と食い違っていた。CLAUDE.md と README 2件は追従させたのに、
  フロー図のノードを見落としていた（サマリ表だけを探して図中のテキストを検索対象にしていなかった）。
  PLAN ノードに documentation-only の分岐を追記。
  なお §3-6 の G-F 行と §4 の但し書きは「`[E2E]` AC があるときのゲート挙動」を述べており、
  無条件の要求ではないため変更不要。
