# Expanded view — showing a drafted plan so a human can decide, not just accept

> **Single source.** `create-exec-plan` (drafting mode) applies **this** file, and
> `../complete-exec-plan/confirmation-sheet.md` reuses its frame and rules for the sheet a human
> confirms with. Do not restate the view's layout, its rules or its record format inline in a skill —
> reference this file.

## Why this exists

When the plan is drawn from approved documents, most of what `create-exec-plan` used to ask can be
derived: the name and scope from the US, the AC lines from the US AC sections and the `E2E-NNN`
scenarios, the `## Sources` table from what each line condenses, the task breakdown from the spec.
Asking those questions makes the human re-answer what they already approved.

Drafting them has its own failure, and this file exists to close it. Shown the plan file as it is,
a human reads one-line ACs, a `## Sources` table that points into other files, and lines such as
`AC-002 ⚠️ R4 — {reason}`. Fragments and summaries cannot be judged, so approval turns into
acceptance — and the plan freezes a target nobody actually looked at.

So the plan file stays as it is, written for the machine and the driver, and the human is shown a
separate **expanded view**: the drafted plan laid out against the approved text it came from, in the
order the product is used, with the decisions that are the human's pulled to the top.

---

## Rules for the view

| # | Rule | Why |
|---|------|-----|
| V1 | **Quote, do not summarize.** Under each AC, expand the US bullet and the spec section it condenses, verbatim. Mark what a human approved and what the agent wrote this time (the one-line condensation, the scope proposal, an `n/a` reason) so they look different | A summary is the agent's reading; the human must compare the line against the text they approved |
| V2 | **Follow the through-flow, not the AC numbers.** Use the steps of the `E2E-NNN` scenario as the skeleton and place each AC under the step it makes work (the R4 correspondence of `ac-readiness.md`). ACs that appear under no step go in a separate block | The human approved a flow of use, not a list of numbers; an AC under no step is the one most likely to be out of place |
| V3 | **One example per AC, built only from values the sources state.** If no example can be written without inventing a value, write no example — turn it into a question instead ("the passing condition is not written") | The example is for reading only. An invented value would be an expected result nobody set; a missing one is exactly the R2 NOT READY, shown in a form the human can answer |
| V4 | **Show what is left out**: US ACs not in this plan, the non-goals, and any bullet that may have been dropped when its AC was condensed to one line | Scope is decided as much by what is excluded as by what is included |
| V5 | **Put the decisions first.** Each question carries its options and what each option changes, so it can be answered from the question alone | A question that needs the rest of the view to answer is answered by accepting the recommendation |
| V6 | **No convention terms in the body.** R2, complement detection, re-anchor and the like are put in product words. The `## Sources` rows and other records go in a final "machine-facing" block the human need not read | The reader is deciding about the product, not auditing the convention |

**The example (V3) is never saved and never becomes a source.** Tests are drafted from the AC line
and its sources (`../run-tests/red-first.md`), exactly as before. An example that seems worth
keeping is a requirement: promote it into the US / spec with the human, or leave it.

---

## What becomes a question

The agent drafts; the human decides. A question is raised for every point where the draft would
otherwise contain a decision only a human may make:

| Source of the question | Example in product words |
|------------------------|--------------------------|
| **Scope** (`SKILL.md`「Plan size」) — a US AC whose inclusion is a real choice (the through-flow does not need it), or a split a size sign calls for (`../complete-exec-plan/completion-boundary.md`「Plan size」 S1–S6 — the question names the sign and its count) | 「タグの削除」をこのプランに入れますか？ |
| **NOT READY** (`ac-readiness.md`) — an AC that fails R1 / R2 / R5, or R3 / R4 with no reason recorded by a human | 同じタグを2回付けたときの結果が要件にも仕様にも書かれていません |
| **⚠️ reason** — R3 / R4 unmet; the reason is a claim about the spec, so it comes from the human (`ac-readiness.md`「Who may state the ⚠️ reason」) | 応答時間の基準が仕様にありません。今回は基準なしで進めますか？ |
| **`n/a（理由）` for a source that cannot be identified** — "there is nothing to read" is a claim about the spec (`ac-sources.md`). The `/create-spec`-skipped row is not one: it follows from the fact that no spec exists | この AC の振る舞いは仕様のどの節にも書かれていません |
| **A finding of the scenario comparison** — a requirements gap or a contradiction (`../create-spec/e2e-interaction.md`) | シナリオは「CSV で書き出す」と述べていますが、要件にはありません |

Anything not on this list is drafted and shown, not asked. The human may still correct any drafted
line while reading; a correction is a decision and is recorded as one (below).

**Approval is answering, not "OK".** While any question is open the plan is not finalized, whatever
else the human says. A question about an AC that another answer leaves out of the plan is closed by
that answer; it is not asked again. Only when the view has **no** questions does the agent ask for approval of the
flow as a whole.

---

## Where the view is written

| Item | Rule |
|------|------|
| Place | `.claude/views/<plan file name without .md>.view.md` |
| Kept in git | **No.** `.claude/views/` is in `.gitignore`. A committed copy of quoted text drifts from the original the moment the original changes |
| Why there | Outside every range a check reads: `check-doc-invariants` lints `.claude/skills/**`, `docs/**`, `exec-plans/**` and the root `*.md`; `spec-gate.py`, `run-tests` and the driver read AC lines from `exec-plans/active/`. Quoted `AC-NNN:` lines placed inside any of those would be read as criteria or linted as documents |
| Diagram | The through-flow is drawn as a Mermaid flowchart (CLAUDE.md「ドキュメント内の図・ダイアグラム規則」) |
| In the conversation | **Only the questions** (the "決めてほしいこと" block) and the path to the view. Do not paste the whole view into the conversation |

---

## Layout

```markdown
# {プラン名} — 読み合わせ

起点の文書: `<commit>` 時点（{US-XXX}, {spec ファイル}, {E2E-NNN}）

## このプランが終わると
{US のゴール像の該当部分を引用}

## 決めてほしいこと（{n} 件）
1. {問い}
   - {選択肢 A} → {選んだ場合に変わること}
   - {選択肢 B} → {選んだ場合に変わること}
   推奨: {A | B}（{理由}）

## 通しの流れ（{E2E-NNN}）
{Mermaid flowchart — シナリオのステップ}

### ① {ステップ} ── {AC-NNN}
- [承認済み・{US-XXX § AC-NNN}] {US の bullet の原文}
- [承認済み・{spec §「節」}] {spec の該当節の原文}
- [今回の1行] {プランの AC 行}
- [たとえば] {起点にある値だけを使った例} ／ 例なし — 決めてほしいこと {n}

### どのステップにも現れない AC
...

## このプランに入れないもの
- {US の AC で入れなかったもの}（{人の決定 | 提案}）
- 非ゴール: {US の非ゴールの引用}
- 1行にしたときに落ちた可能性のある bullet: {引用}

## 機械向けの記録（読まなくてよい）
{## Sources の行、readiness の判定、E2E の照合結果}
```

---

## The lifecycle — when the plan file exists

The plan file is written **only after the human has answered every question**. A drafted plan
lives in the view until then and never in `exec-plans/active/`, so no drafted-but-undecided AC line
can be read by `spec-gate.py`, `run-tests` or the driver, and the scenario freeze
(`../create-spec/e2e-interaction.md`「Finalized」) still happens at the moment the file is written.

| State | What exists | What a new session does |
|-------|-------------|-------------------------|
| Drafting / waiting for answers | The view (temporary, may be gone) | **Starts over**: drafts again from the approved documents and asks again. An answer given in an earlier session is not in any file, so it is not in hand — the human repeats it (same rule as `../complete-exec-plan/completion-boundary.md` for statements from an earlier session) |
| Answers applied, re-check pending | The view | Same as above |
| Finalized | The plan file, with the records below | Reads the plan file. The view is not needed; it can be regenerated from the records |

**After the answers, check again before writing the file.** Apply the answers, then re-run the
readiness check on every AC an answer added or changed (an AC brought into scope has not been
through it), the walkthrough judgement if the scope changed, and the scenario comparison on every
`E2E-NNN` a row newly names (`SKILL.md` Steps). A new question that this raises goes back to the human in a
regenerated view. Also check that the approved documents have not moved since the view was
generated (`git diff --quiet <commit> -- <source files>`); if they have, regenerate the view from the
new commit and present it again — the human answered about the text they were shown. An answer
whose quoted text changed is asked again; the other answers stand. The record names the commit of
the last view presented.

---

## Record format

In the plan's `## Decision Log`, written when the plan file is created:

```markdown
- 展開ビュー提示: 起点の文書は `<commit>` 時点（`US-003`, `docs/02_spec/app_spec.md`, `E2E-001`）。
  問い {n} 件 — 人の回答で確定（YYYY-MM-DD）。
- 人の決定（スコープ）: `US-003` AC-004「タグの削除」はこのプランに入れない（次のプランへ）。
- 人の決定（AC の書き直し）: AC-002 — {回答}。{合格条件が起点に無かった | 起点と1行が食い違った}。
- 人の決定（⚠️ の理由）: AC-005 R3 — {人が述べた理由}。
- 人の決定（起点 n/a）: AC-003 spec — {人が述べた理由}。
- 人の決定（1行の訂正）: AC-001 — 「{起草した1行}」→「{人の訂正}」。
```

with the scenario comparison recorded in its own format
(`../create-spec/e2e-interaction.md`「Record format」), and, when the view had no questions:

```markdown
- 展開ビュー提示: 起点の文書は `<commit>` 時点（…）。問い 0 件 — 通しの流れ全体を人が承認（YYYY-MM-DD）。
```

The `<commit>` is what lets the view be regenerated after the temporary file is gone:
`git show <commit>:<path>` gives the approved text the human read, and the plan file gives the rest.
Record only what the human said; the agent does not infer a decision from silence or from the
absence of objections.

---

## How this differs from the other checks

| Check | Question it answers |
|-------|---------------------|
| AC readiness (`ac-readiness.md`) | Can this criterion be measured? |
| AC sources (`ac-sources.md`) | Does the implementer receive the whole goal? |
| Scenario comparison (`../create-spec/e2e-interaction.md`) | Does the scenario say more than the requirements? |
| **Expanded view (this file)** | **Did the human see the drafted target in a form they could judge — and decide every point that was theirs?** |

The view adds no new check. It changes **who writes** the plan and **how the human is shown** the
decisions the existing checks raise; the checks, their criteria and their call sites stay where they
are.

---

## Where this is applied

| Call site | When | Action |
|-----------|------|--------|
| `create-exec-plan` (drafting mode) | Before the plan file is written | Draft, generate the view, put the questions to the human, apply the answers, re-check, then write the plan with the records above |
| `create-exec-plan` (interview mode) | — | Not applied: with no approved document to derive from, there is nothing to quote, and the questions are asked one at a time as before |
| `../complete-exec-plan/confirmation-sheet.md` | When every AC is done | Reuses the frame and rules V1, V2, V4–V6 for the sheet the human confirms with; V3 (the example) is replaced there by the evidence |
