# Confirmation sheet — what was built, laid out so a human can confirm it

> **Single source.** `pre-pr` (generating the sheet), `run-exec-plan` (Step 4b / 4c),
> `complete-exec-plan` (Step 2) and the human confirmation record in
> [`completion-boundary.md`](completion-boundary.md) all apply **this** file. Do not restate the
> sheet's layout, the demonstration rules or the method wording inline in a skill — reference this file.

## Why this exists

Completion waits for a human to confirm every AC of the plan
([`completion-boundary.md`](completion-boundary.md)「What `completed` means」). Nothing gave them the
material to do it. The run's report is a column of ✅ and a test count; the evidence — what the
approved documents asked for, what each test checks, the red that came before the green, the
re-anchor against the spec — is spread across the plan's Decision Log, the test files and the
sources. A confirmation made without that material is a confirmation of the ✅ column, which is the
agent's own claim.

So when every AC is done, the agent writes a **confirmation sheet**: the same frame as the expanded
view the plan was approved from (`../create-exec-plan/expanded-view.md`), with the evidence filled
in. At the freeze the view said *this is what will be built*; the sheet says *this is what was built,
and here is how you can tell*.

**The sheet is not a confirmation.** It is the material a human confirms with. Its existence, and
everything in it, are the agent's checks — the record of confirmation still comes only from the
human ([`completion-boundary.md`](completion-boundary.md)「Who writes it」).

---

## How the human confirms — the method

The unit is still **every AC of the plan**. The method differs by kind of AC:

| AC | How the human confirms it | Why |
|----|---------------------------|-----|
| `[E2E]` AC | **Sees the through-flow work**: runs it themselves (the sheet says how), or reads the demonstration record of a run at the sheet's commit | The through-flow is the one thing a list of green fragments cannot show. A human who has not seen it work has confirmed the fragments |
| Functional AC | **Reads the sheet**: the approved text, what the test checks, red before green, the re-anchor | A functional AC is a fragment the `[E2E]` flow is built from; its evidence is in documents and tests, which the sheet puts side by side |

A documentation-only plan has no `[E2E]` AC (`../create-exec-plan/SKILL.md`): every AC is confirmed
by reading the sheet, and the sheet has no demonstration and no "run it" item.

The agent asks for confirmation in this form. It does not refuse a confirmation over its method: what
the human says they did is what the record says (`<方法>`, below), and the record is theirs.

---

## Rules for the sheet

The expanded view's rules apply unchanged — **V1** quote, do not summarize; **V2** follow the
through-flow; **V4** show what was left out; **V5** what the human must do comes first; **V6** no
convention terms in the body (`../create-exec-plan/expanded-view.md`「Rules for the view」). V3 (the
example) is replaced by the evidence:

| # | Rule | Why |
|---|------|-----|
| C1 | **Evidence, per AC, from the record — not from memory.** The `red-first` and `done` entries of the Decision Log, the test file and test name, and the `spec 再アンカー:` line. Write what they say; an AC whose record is missing says so (`記録なし`) | The sheet must not contain a claim the files do not back |
| C2 | **The test in the AC's words.** Restate each test's given / when / then in product words next to the approved text it was transcribed from, so a mismatch between the two is visible | This is the comparison the human is in the best position to make: does the test check what was asked for? |
| C3 | **The demonstration is a real run, at the sheet's commit.** For each step of the scenario: the action and what was observed — captured output, a screenshot, a terminal transcript. A step that could not be shown says `実演できず（理由）`; never write what the step *should* show | A demonstration written from expectations is the ✅ column again, in prose |
| C4 | **What needs the human's eye goes first**: every `⚠️` of `pre-pr`, the suggestions of `docode-review`, every decision a human made during the run (`人の決定` and HALT entries), and every AC whose re-anchor is `n/a` | These are the places where the evidence is thinner or a choice was made; a human reading top-down meets them first |

---

## Where the sheet is written, and where a reviewer reads it

| Item | Rule |
|------|------|
| Place | `.claude/views/<plan file name without .md>.confirm.md` — the expanded view's place, under the same rules: **not committed** (`.gitignore`), outside every range a check reads. Captured images go in `.claude/views/<plan file name without .md>.confirm/` |
| Commit | The sheet names the commit it describes (`git rev-parse --short HEAD`), and says so when the working tree also had uncommitted implementation changes (`＋未コミットの変更`) |
| When it goes stale | When implementation changes after the sheet was generated. Regenerate it; a confirmation given on the stale sheet does not cover the change — the same rule as an approval given on an older commit ([`completion-boundary.md`](completion-boundary.md)「An approval covers the commit it was given on」) |
| On the PR path | A reviewer cannot read a file that is not committed, so the sheet goes **into the PR**: its body when the PR is opened by this flow (`run-exec-plan` Step 4c), or a comment, posted on the human's instruction, on a PR opened otherwise. It names its commit; when a new sheet replaces it, replace it in the PR too. Images under `.claude/views/` are not visible there: the PR carries the text of the demonstration (the captured output, the observed result per step) and says which images exist locally. A sheet too long for one body goes in comments, in order |
| In the conversation | The "確認してほしいこと" block and the path. Do not paste the whole sheet |

---

## Layout

```markdown
# {プラン名} — 確認シート

対象: `<commit>` 時点{＋未コミットの変更}。起点の文書: {US-XXX}, {spec ファイル}, {E2E-NNN}

## このプランが終わると（できたこと）
{US のゴール像の該当部分を引用}

## 確認してほしいこと
1. 通しの流れ（{E2E-NNN}）を動かして確かめる — 実行方法: `{コマンド}` ／ 実演記録は下の「通しの流れ」
2. 目を通してほしい点（{n} 件）
   - {pre-pr の ⚠️ ／ docode-review の提案 ／ 走行中の人の決定 ／ 再アンカーが n/a の AC}

## 通しの流れ（{E2E-NNN}）
{Mermaid flowchart — シナリオのステップ}

### ① {ステップ} ── {AC-NNN}
- [承認済み・{US-XXX § AC-NNN}] {US の bullet の原文}
- [承認済み・{spec §「節」}] {spec の該当節の原文}
- [1行] {プランの AC 行}
- [テスト] `{テストファイル}::{テスト名}` — {前提} のとき {操作} すると {結果} になることを確かめる
- [赤→緑] 実装前に赤（期待: {…}／実際: {…}）→ 実装後に緑（{n} 件）
- [仕様との照合] {spec §「節」} と照合し一致 ／ n/a（{理由}）
- [実演] {操作} → {観察した結果}（{出力・画面}）／ 実演できず（{理由}）

### どのステップにも現れない AC
...

## このプランに入れなかったもの
{展開ビューと同じ。走行中に取り下げた AC があればここに}

## 機械向けの記録（読まなくてよい）
{Decision Log の該当行、pre-pr・docode-review の結果}
```

---

## The method in the confirmation record

The record keeps its format ([`completion-boundary.md`](completion-boundary.md)「The human
confirmation record」). Its `<方法>` names the sheet's commit and how the `[E2E]` AC was seen, as
the human described it:

```markdown
- 人の確認: 全 AC（AC-001〜AC-005）— <確認者>, YYYY-MM-DD, 確認シート（a1b2c3d）で機能 AC、[E2E] AC-005 は実演記録を確認。根拠: 発言「<their words, verbatim>」
- 人の確認: 全 AC（AC-001〜AC-005）— <確認者>, YYYY-MM-DD, PR #12 のレビュー（確認シート a1b2c3d、[E2E] AC-005 は自分で実行）。根拠: PR #12 approve（…）
```

The `<方法>` is the human's account of what they did, transcribed — not inferred from which files
exist. When they confirmed without the sheet, or without seeing the flow, the record says what they
did say.

---

## Where this is applied

| Call site | When | Action |
|-----------|------|--------|
| `pre-pr` (⑧) | Every AC of the plan is `- [x]` and the plan is still in `active/` | Generate the sheet (also in the report-only mode `run-exec-plan` Step 4b uses: the sheet is written outside the code and the documents) and name its path |
| `run-exec-plan` (Step 4c) | Opening the draft PR | Put the sheet in the PR body |
| `complete-exec-plan` (Step 2) | No confirmation record is in hand | Hand the human the sheet — regenerated if it is stale or gone — when asking whether they have confirmed every AC |
| [`completion-boundary.md`](completion-boundary.md) | The human confirmation record | `<方法>` names the sheet's commit and how the `[E2E]` AC was seen |
