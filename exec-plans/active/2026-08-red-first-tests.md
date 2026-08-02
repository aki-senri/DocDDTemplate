---
status: active
created: 2026-08-02
completed:
---

# red-first-tests

## Goal & Scope

受け入れテストを **実装より先に、AC 本文から起草して赤で置く**（red-first）ことを DocDD の規約にし、
「実装者が実装と同時にテストを書く＝自分の答案を自分で採点する」構造を解消する。
INV-T01（実装に合わせたテスト改変の禁止）を**時間軸**で強制する形に拡張し、赤の観測をもって
テストの期待値を凍結する。GitHub issue #22 (G-A) の解消。親トラッキングは #28 で、本プランはその Ph3
（#27 → #24 の次）にあたる。

## Acceptance Criteria

- [ ] AC-001: red-first の単一ソース `.claude/skills/run-tests/red-first.md` が存在し、
      ①手順（AC 本文からテストを起草 → 実行して赤を観測 → 記録して凍結 → 実装）②「妥当な赤」と
      「無効な赤」の判別基準 ③Decision Log への記録書式 ④凍結後にテストを変更してよい唯一の経路
      ⑤呼び出し地点ごとの措置表 ⑥適用外（documentation-only 等）の6項目すべてを定義した状態にする
- [ ] AC-002: `run-exec-plan` の内側ループが AC ごとに「テストを先に書いて赤を観測してから実装する」
      順序になった状態にする（Step 2 が 2a テスト起草＋赤観測 / 2b 実装に分かれ、AC 本文からテストを
      書けない場合は停止条件 (a) で HALT し、Decision Log に赤の観測が `AC-NNN done` より前に記録される）
- [ ] AC-003: `run-exec-plan` が `[E2E]` AC のテストを**ループ開始前**に赤で置いた状態でループを開始する
      （Step 0c）。あわせて「driver は E2E テストを書いてはならない」という現行記述が
      「実装前に AC 本文から転記する場合に限り書いてよい／転記できない場合は HALT (a)」に置き換わり、
      ループ中の「`[E2E]` AC にテストが無い＝ HALT」backstop が残っている
- [ ] AC-004: `run-tests` が red-first 検証（赤が期待される実行）を扱えた状態にする。すなわち
      「テストが失敗した」だけでなく「妥当な赤（期待結果に関する失敗）／無効な赤（コンパイル・
      セットアップ・存在しない API による失敗）」を判別して報告し、無効な赤を緑と同じく
      「先へ進んでよい」とは扱わない
- [ ] AC-005: `start-feature`（手動パス）の実装順ガイドが red-first を規定した状態にする
      （「安定層から実装する」順序の**前**に「その AC のテストを先に赤で置く」が来ることが本文で読める）
- [ ] AC-006: `pre-pr` と `complete-exec-plan` が red-first の証跡（各 AC について、赤の観測が
      `AC-NNN done` より前に Decision Log へ記録されていること）を確認し、欠落を報告する状態にする
      （証跡欠落は ⚠️ 報告であり PR / 完了をブロックしない。ブロックするのは既存の AC カバレッジ・
      E2E カバレッジのまま）
- [ ] AC-007: `init-project` が生成する不変条件表に **INV-T02**（テストの期待値は、それを満たす実装より
      先に AC から起草され、赤を観測してから凍結される）が含まれ、`SKILL.md` の共通不変条件・
      `setup-web.md` / `setup-windows.md` の各表・生成ファイル一覧の記述が INV-T02 を含む状態にする
- [ ] AC-008: `docode-review` の独立エージェントが「各テストが対応する AC を表現しているか（実装の写しに
      なっていないか）」を観点として持ち、判定に含めた状態にする
- [ ] AC-009: `CLAUDE.md` / `SKILL_FLOW.md` / `README.md` / `README.ja.md` / `ONBOARDING.md` /
      `ONBOARDING.ja.md` のいずれにも red-first 導入**前**のフロー記述が残っていない状態にする
      （＝内側ループを「実装 → テスト」と書いた図・表・手順、および INV-T01 だけを挙げてテストの
      時間軸に触れない箇所が1件も無い）
- [ ] AC-010: red-first を導入した4地点（`run-exec-plan` / `run-tests` / `start-feature` /
      `pre-pr`＋`complete-exec-plan`）の照合結果が Decision Log に記録され、(a) 同じ「妥当な赤」の
      定義が単一ソースにのみ存在すること (b) 措置だけが地点ごとに分かれること (c) 既存の停止条件
      (a)/(c) と矛盾しないこと を含む全項目が PASS である

> 本プランは documentation-only（変更対象は `.claude/skills/**` と `*.md` のみ）のため
> `[E2E]` AC を持たない。Decision Log の `E2E: n/a (documentation-only)` を参照。

## Task Breakdown

- [ ] AC-001 — `.claude/skills/run-tests/red-first.md` を新規作成
- [ ] AC-002 — `.claude/skills/run-exec-plan/SKILL.md` の Step 2 を 2a / 2b に分割
- [ ] AC-003 — 同 SKILL.md に Step 0c を追加し、E2E テスト起草の禁止規定を書き換え
- [ ] AC-004 — `.claude/skills/run-tests/SKILL.md` に red-first 検証モードを追加
- [ ] AC-005 — `.claude/skills/start-feature/SKILL.md` の実装順ガイドを改修
- [ ] AC-006 — `.claude/skills/pre-pr/SKILL.md` と `.claude/skills/complete-exec-plan/SKILL.md` に証跡確認を追加
- [ ] AC-007 — `.claude/skills/init-project/{SKILL.md,setup-web.md,setup-windows.md}` に INV-T02 を追加
- [ ] AC-008 — `.claude/skills/docode-review/SKILL.md` に観点を追加
- [ ] AC-009 — `CLAUDE.md` / `SKILL_FLOW.md` / `README*.md` / `ONBOARDING*.md` を追従
- [ ] AC-010 — 4地点の照合を実施し Decision Log に記録
- [ ] `/check-doc-invariants` を実行
- [ ] `/pre-pr` を実行（PR 作成自体は人間ゲート）

## Progress Log

### 2026-08-02
- Plan created

## Decision Log

### 2026-08-02

- **E2E: n/a (documentation-only)**。本プランの変更対象は `.claude/skills/**` と `*.md` のみで、
  機能を実装するファイルを含まない。`create-exec-plan` の規約に従い `[E2E]` AC を置かない。
- **スコープの根拠**。issue #22 の改善方向は3つ。①`run-exec-plan` の内側ループを red-first 化
  ②テスト起草を実装とは別ステップ（または軽量な別エージェント確認）にして実装前に固定
  ③INV-T01 の精神を時間軸で強制。3つとも本プランに入れた。①＝AC-002/003、②＝AC-001（別ステップの
  定義）＋AC-008（軽量な独立確認）、③＝AC-007（INV-T02）。
  ②を「別スキル」ではなく「単一ソース＋ステップ分割」で実現するのは #24 の `ac-readiness.md` と
  同じ構成にするため。スキルを増やすと呼び出し地点ごとの複製が増え、ドリフトの原因になる。
- **単一ソースの置き場所を `run-tests/` にした理由**。red-first は「テストは spec の実行可能表現」の
  時間軸版であり、その概念を所有しているのは `run-tests`（INV-T01 のゲートを持つ側）。
  `ac-readiness.md` が起票地点（`create-exec-plan`）に置かれているのと同じ理屈で、
  概念の持ち主のディレクトリに置き、他地点は参照する。
- **AC readiness（Q3c）の判定**: AC-001〜AC-010 すべて READY。R4 は documentation-only のため n/a。
  - R1: 各 AC は「〜した状態にする」という単一の終状態で書いた。AC-002 のように複数ファイルに
    触れるものも、観測可能な結果は1つ（ループの順序が red-first になっている）。
  - R2: given（現行の記述）/ when（該当スキルを読む・実行する）/ then（本文に何が書かれているか）が
    各 AC から特定できる。
  - R3: 判定語を「6項目すべてを定義」「`AC-NNN done` より前に記録」「1件も無い」など数えられる形にした。
  - R5: どのファイルを触るかは Task Breakdown に置き、AC 本文は結果のみとした（AC-001 と AC-007 は
    ファイルパス自体が成果物の同一性なので本文に残している）。
- **AC-006 を ⚠️ 報告に留めた理由**。red-first の証跡は Decision Log という**人が書くテキスト**に
  依存するため、欠落は「規約違反」と「記録漏れ」を機械的に区別できない。ブロックにすると
  記録漏れで PR が止まり、回避のために証跡を後から書く動機を生む（＝証跡の信頼性が下がる）。
  実効的なブロックは既存の AC カバレッジ／E2E カバレッジが担う。
