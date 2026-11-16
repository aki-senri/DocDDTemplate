---
name: create-exec-plan
description: |
  Creates a new execution plan in exec-plans/active/.
  Used when starting a substantial piece of work (feature implementation, documentation, refactoring, etc.) in Phase 2 (requirements/design) or later.
  Any plan that implements requirements or functionality — refactoring included — carries at least
  one [E2E] acceptance criterion alongside the functional ones, so a plan cannot be completed by
  turning fragments green without the through-flow working. Documentation-only plans record
  "E2E: n/a" instead. Each criterion also records where the detail it condenses lives (the US
  bullets and the spec section), so the implementer receives the whole goal rather than one line.
  Every criterion is checked for testability (AC readiness) before the plan
  file is finalized, so ambiguity is caught while it is still cheap to rewrite.
  When the plan is drawn from an approved US (and its spec and E2E scenarios), the agent drafts the
  plan instead of interviewing for it, and shows the human an expanded view — the draft against the
  approved text, in through-flow order — with only the decisions that are the human's put to them.
disable-model-invocation: true
---

# Skill: Create Execution Plan

> **When to run**: When starting a substantial piece of work (feature implementation, phase transition, documentation, etc.)
>
> **Purpose**: Record the goals, acceptance criteria, and task breakdown of the work in the repository,
> so that both agents and humans can track progress against the same plan.
>
> **Prerequisites**: The `exec-plans/active/` directory must exist (create it if it doesn't)

---

## What this skill does

1. Collect plan details — **drafted** from the approved documents when there are some, through an
   **interview** when there are none (see **Two modes** below)
2. For a plan that changes a process (a loop, a gate, a resumable run), require a
   **process walkthrough** AC rather than a description-consistency one
2b. Record each criterion's **sources** — the US bullets and spec section its one line condenses
2c. Check every criterion for **AC readiness** (testability) and rewrite the ones that fail
2d. Check that the plan is small enough for **one branch to implement and one human confirmation to
   cover** every criterion, and split it if not
3. Generate `exec-plans/active/YYYY-MM-{name}.md` with at least one `[E2E]` acceptance criterion
   alongside the functional ones, and a `## Sources` table covering every criterion
4. Update the "Current Phase & Priority Tasks" section of `docs/07_ai_context/CONTEXT.md`

---

## Two modes

Most of what this skill used to ask can be derived when the plan is drawn from approved documents,
and asking it anyway makes the human re-answer what they already approved. What cannot be derived
is a decision, and those stay with the human. The mode follows from what there is to derive from:

| Situation | Mode |
|-----------|------|
| The plan is drawn from a US that is approved (on `main`), or that is in the same bundle (`../create-spec/bundled-approval.md`) — with its spec and `E2E-NNN` scenarios, or with `/create-spec` skipped and the US goal image as the through-flow | **Drafting** — the agent drafts every row marked *drafted* below, and puts only the rows marked *the human decides* to the human, through the expanded view ([`expanded-view.md`](expanded-view.md)) |
| There is nothing approved to derive from — the plan's subject is the repository's own conventions (sources `n/a`), or the US is still a draft not on `main` | **Interview** — the questions are asked one at a time, in order, as below |

The documents are read as they are on `main`. A US, spec or scenario that the current branch has
edited but `main` does not have is not approved, and a draft is not derived from it: approve it first
(merge it), or use the interview — **except on the bundled path**, where the US, the spec and the
scenarios are approved together with this plan in one PR: then the documents in the bundle are read
from the definition branch, and the plan records the `一括承認:` line
([`../create-spec/bundled-approval.md`](../create-spec/bundled-approval.md)). Which US the plan is drawn from comes from the request
(`/create-exec-plan US-003`); when the request does not say, list the approved US `AC-NNN` sections
that no plan's `## Sources` (in `exec-plans/active/` or `exec-plans/completed/`) names yet, grouped by
US, and let the human pick — a US whose first plan left some of its ACs for later still has them
listed.

**Drafting changes who writes, not who decides.** The checks below — plan size, the walkthrough AC,
the sources, the scenario comparison, readiness — run exactly as in the interview; what changes is
that each decision they raise reaches the human as a question in the expanded view instead of in the
middle of a one-question-at-a-time interview. An agent that drafts a decision on the human's behalf
(a ⚠️ reason, an `n/a` reason, a rewritten AC, a resolution of a scenario finding) has left the
drafting mode's bounds, whatever the view looks like.

## Interview

In the interview mode, the agent asks the following questions **one at a time, in order**. In the
drafting mode, the last column says which rows the agent drafts and which become questions in the
expanded view.

| # | Question | Used for | Drafting mode |
|---|----------|----------|---------------|
| Q1 | What is the name of this plan? (alphanumeric and hyphens, e.g. `user-auth`, `refactor-service-layer`) | Filename | *drafted* from the US |
| Q2 | Please describe the goal and scope in 3 lines or fewer | `## Goal & Scope` | *drafted* from the US goal image and the proposed scope |
| Q3 | List the acceptance criteria to consider this plan complete (numbered as `AC-001`, `AC-002`, ...) | `## Acceptance Criteria` | *drafted* — one line per US `AC-NNN` section in scope, restating only what the section says |
| Q3b | Which end-to-end scenario must work when every criterion above is met? For a refactoring plan: which existing through-flow must still work unchanged? (see **E2E acceptance criteria** below) | `## Acceptance Criteria` (last entries) | *drafted* — one `[E2E]` AC per `E2E-NNN` in scope (the US goal image when the spec was skipped) |
| Q3f | Can **one branch implement every criterion above, and one confirmation by you cover them all**? If not, which criteria go to a separate plan? (see **Plan size** below) | `## Acceptance Criteria` (criteria moved out), `## Decision Log` (the split) | **the human decides** — the agent proposes the scope; every US AC whose inclusion is a real choice, and any split the size calls for, is a question |
| Q3e | Does this plan change a **process** — a loop, a resumable run, a stop condition, a gate, an exemption, or a rule other rules consume (including renaming a step or question number others point at)? If so, add the walkthrough AC (see **Process changes** below) | `## Acceptance Criteria` (verification AC) | *drafted* — judged by the scope table in [`process-walkthrough.md`](process-walkthrough.md) |
| Q3d | For each criterion: which US `AC-NNN` section and which spec section does it condense? (see **AC sources** below) | `## Sources` | *drafted* — the sections each line was condensed from are its sources. **The human decides** every `n/a（理由）` and every finding of the scenario comparison |
| Q3c | *(not asked — run by the agent)* Check **every criterion the plan will contain** — Q3, Q3b and the Q3e walkthrough AC — against the five readiness checks and rewrite the failing ones with the user (see **AC readiness** below) | `## Acceptance Criteria`, `## Decision Log` | run by the agent; **the human decides** every NOT READY rewrite and every ⚠️ reason |
| Q4 | Break down the tasks (in checklist format) | `## Task Breakdown` | *drafted* — how to build is not a decision about what to build |

> **Ask them in the order the rows appear**, not in alphabetical order of their labels: Q1 → Q2 →
> Q3 → Q3b → Q3f → Q3e → Q3d → Q3c → Q4. In the drafting mode the same order is the order of
> drafting, and the questions are put to the human together once the draft has been through Q3c.
> Q3f, Q3e and Q3d come **before** Q3c although they are lettered later. Q3f comes right after the criteria are listed, so the questions that follow — the
> walkthrough AC, the sources, readiness — run only on the criteria that stay in this plan. Readiness must run over the
> finished AC set: an AC added after the readiness gate has never been through it — which is the
> failure the gate exists to prevent. If any criterion is added or reworded after Q3c, re-run Q3c on
> it. Q3d comes before Q3c for a second reason: `R2` and `R4` are judged against the AC line
> **together with its sources**, so the readiness check cannot run correctly until Q3d has named
> which US section and which `E2E-NNN` each criterion condenses.

---

## Plan size

A plan is written to the size that **one branch can implement in full, and one human confirmation
can cover in full**. Completion is the human confirming every AC of the plan, recorded as a commit on
the implementation branch before the merge, and a plan is not merged in an intermediate state — so a
plan too large for one branch and one confirmation would have to be split later, mid-flight, when
splitting costs the most. The rule, the signs that a plan should be split and the one line not to
split across (an `[E2E]` AC's through-flow) live in
[`../complete-exec-plan/completion-boundary.md`](../complete-exec-plan/completion-boundary.md)
「Plan size」 — apply it at Q3f.

This is not a readiness check. Readiness (`ac-readiness.md`) asks whether each criterion can be
measured; Q3f asks whether the plan as a whole can be finished and confirmed at once. A plan can pass
one and fail the other.

| Answer | Action here |
|--------|-------------|
| Fits | Continue |
| Does not fit | Agree with the user which criteria move out, and run this skill again for them as a separate plan — implemented on a branch of its own, not alongside this one (`completion-boundary.md`「When part of a plan has to merge before the rest」). Record the split in this plan's `## Decision Log` (`- 分割: AC-… を <別プラン名> へ — <理由>`). Each plan that implements functionality keeps its own `[E2E]` AC |

Which criteria a plan delivers is the user's decision; propose a split, do not make it.

---

## AC sources

An exec-plan AC is one line by necessity (`spec-gate.py` parses `AC-(\d{3}):`), and
`create-requirements` states plainly that the verifiable bullets stay in the US file. The one-liner
is therefore a **pointer**, and a plan that does not say where it points hands the implementer a
condensed goal to interpret alone.

Q3d fills the `## Sources` table. Apply [`ac-sources.md`](ac-sources.md) — the single source shared
with `run-exec-plan`, `start-feature`, `pre-pr`, `docode-review` and `promote-spec`. Read that file
for the table format, the admissible sources, and the pitfall about colons after `AC-NNN`; do not
re-derive them here.

| Situation at authoring time | What to write in the row |
|-----------------------------|--------------------------|
| A US section and a spec section exist for the criterion | Both, each named down to the **section** |
| `/create-spec` was skipped (small change) | The US section, and `n/a（spec 未作成 — 起点は US の該当節）` |
| The plan's subject is the repository's own conventions, with no US and no spec | One row covering the range, `n/a（理由）` |
| The source genuinely cannot be identified | `n/a（理由）` — **with the user**. "There is no spec for this" is a claim about the spec, not a gap the agent may declare on its own |

In the drafting mode the rows are drafted — the sections each line was condensed from are its
sources, and the `/create-spec`-skipped row follows from the fact that no spec exists — but an
`n/a（理由）` for a source that cannot be identified is a claim about the spec and is put to the user
as a question, never written by the agent alone. The same holds for every finding of the scenario
comparison below.

Never leave a cell blank. A blank cannot be told apart from a forgotten row, and the table's value
is exactly that a later reader can distinguish "there is nothing to read" from "nobody looked".

Two more rules apply while filling the table, both because the plan is about to freeze:

- **Name sources only — never background material.** A research note, an ADR in
  `docs/00_project/decisions.md` or another plan's Decision Log may explain *why* an AC exists, and a
  design document how it is built, but a test may not be drafted from any of them
  (`ac-sources.md`「What counts as a source」). If the detail the AC
  needs lives only there, promote it into the US / spec with the user, or write `n/a（理由）`.
- **A row that names an `E2E-NNN` freezes that scenario for this plan.** Before finalizing, compare
  the scenario against the comparison set that
  [`../create-spec/e2e-interaction.md`](../create-spec/e2e-interaction.md) defines (wider than the
  row), resolve any detected requirements gap or contradiction with the user, and record the result
  in the Decision Log in that file's format. A comparison set that cannot be assembled (a US under
  the scenario's `由来ジャーニー` with no goal image, say) is not a pass: the plan is not finalized
  until it is whole (that file's「Where this is applied」). Freezing an unresolved gap would freeze
  a requirement nobody set.

---

## AC readiness

Before the plan file is written, every criterion is checked against the five testability checks in
[`ac-readiness.md`](ac-readiness.md) — the single source shared with `start-feature`,
`run-exec-plan` and `doc-review`. Read that file and apply it; do not re-derive the criteria here.

This is the point in the flow where a thin AC is cheapest to fix: the user is present, nothing has
been implemented, and the plan is not yet a frozen target. That is why the check lives here rather
than only in `run-exec-plan` — by the time the autonomous loop meets a NOT READY criterion, its only
option is to halt.

| Verdict | Action here |
|---------|-------------|
| READY | Write the criterion as answered |
| ⚠️ (R3 or R4 unmet for a stated reason) | Write it, and record the reason in `## Decision Log` |
| NOT READY | **Rewrite the criterion with the user** — name every failing check by its own ID (any of `R1` / `R2` / `R5`, and `R3` / `R4` when no reason can be given) and quote the phrase that fails each one, propose a rewrite, confirm it. Do not finalize a plan containing a NOT READY criterion |

Rewriting an AC is a decision about *what to build*, so it is made with the user, not on their
behalf. In the drafting mode a NOT READY criterion and an unmet R3 / R4 are put to the user as
questions in the expanded view, in product words ([`expanded-view.md`](expanded-view.md)「What
becomes a question」) — the agent drafts neither the rewrite nor the ⚠️ reason. If the user
declines to rewrite, record their decision and the failing check in the Decision Log — a later `run-exec-plan` will still halt on it (this is intended; see the call-site
table in `ac-readiness.md`).

---

## Process changes (plans that change how DocDD itself runs)

A plan whose deliverable is a **rule** rather than a feature — it changes a loop, a resumable run,
a stop condition, a gate, an exemption, or a single source other skills consume — needs a
verification AC of its own kind. Apply
[`process-walkthrough.md`](process-walkthrough.md) (the scope table there decides); do not
re-derive the laps here.

**Why a normal verification AC is not enough.** The reflex is to write "全地点の記述が一致することを
照合し、結果を Decision Log に記録する". That check compares text to text, and a process can be
described identically everywhere and still deadlock — a resumed run rejected by its own entry
check, a gate that fires at the moment the run succeeds. Those states are only visible by walking
the process one lap.

The same reflex has a second failure, which the AC must also cover: a change to a rule that other
gates consume leaves those gates *textually correct* — they still say "apply this rule", and they
do — while the material the rule now requires is not in hand when they run. Comparing descriptions
finds nothing, and neither does walking forward from the change, because those gates are not on the
path the change created. The AC must therefore require lap 7 by name.

| Plan changes… | Verification AC to write |
|---------------|--------------------------|
| A process in the scope of `process-walkthrough.md` | An AC requiring the walkthrough — naming the laps (happy / second iteration / resume / exemption / gate boundary / success moment / dependency backflow) and requiring the findings and their fixes in the Decision Log |
| A **single source, a record format, or a step's inputs** that other sites consume | The same AC. Lap 7 (dependency backflow) is the one that matters most here, and the one the plan is most likely to skip: the sites it visits are ones this plan never intended to edit |
| **Only a rename or renumbering** of a step, question or ID others point at | An AC requiring **lap 7 alone**, and saying why laps 1–6 do not apply (a rename carries no state transitions). Use the lap-7-only record variant in `process-walkthrough.md` — writing a 7-lap AC here produces a criterion that its own correct execution cannot satisfy |
| Only descriptions with no state transitions, and nothing points at what changed | The ordinary cross-site consistency AC is enough |

The walkthrough AC **replaces nothing**: readiness still applies to it (it is an ordinary AC and
must state a single observable outcome), and a plan that also implements functionality still carries
its `[E2E]` AC.

A plan that implements requirements or required functionality must carry **at least one E2E
acceptance criterion** in addition to its functional ones. Functional ACs are fragments: each can
be green while the thing as a whole is unusable. The E2E AC is the criterion that the fragments
add up.

### When it is required

| Plan implements… | E2E AC | The E2E AC says |
|------------------|:------:|-----------------|
| New / changed functionality from requirements | **Required** | the new through-flow works end to end |
| **Refactoring** of code that realizes functionality | **Required** | the *existing* through-flow still works unchanged |
| A reconcile plan re-opening AC-IDs (see CLAUDE.md) | **Required** | the through-flow covering the re-opened ACs holds |
| Nothing functional — documentation, doc restructuring | **Must not** carry one | — (record `E2E: n/a`) |

**Refactoring is not an exception.** It is the case that most needs the criterion: the whole claim
of a refactor is "behavior is preserved", and without an E2E AC the plan can be completed having
verified only that the fragments still compile. Write the E2E AC as a preservation statement —
"E2E-001 が変更後も同じ前提・同じ完了条件で成立する" — and hold it to the same passing-test bar.

**Documentation-only** means the plan changes no file that implements functionality — checkable
against `git diff --name-only`. It is not a judgment call about how "code-like" the work felt. For
such a plan, record `E2E: n/a (documentation-only)` in the plan's `## Decision Log` so a later
reader knows the criterion was considered and ruled out, not forgotten.

**A documentation-only plan does not define an `[E2E]` AC at all** — not even for a process
walkthrough that feels end-to-end. The reason is mechanical, not philosophical: `run-tests`,
`pre-pr`, `complete-exec-plan` and `run-exec-plan` all treat "`[E2E]` AC present, no passing test"
as a hold, and none of them accepts a walkthrough in place of a test. A plan that writes an `[E2E]`
AC it cannot cover with a test is a plan that cannot be completed. Verification work that is worth
tracking still belongs in the plan — as an ordinary functional AC whose result is observable
("…の照合結果が Decision Log に記録され、全項目が PASS である"), which the same gates handle without
a special case.

**Notation** — an E2E AC is an ordinary numbered AC whose description starts with the `[E2E]`
marker:

```markdown
- [ ] AC-005: [E2E] {the through-flow that must work end to end}
```

Keep the `AC-NNN:` numbering continuous with the functional ACs and place the E2E entries last.
Do **not** invent a separate ID series (`AC-E01:`) — `.claude/hooks/spec-gate.py` parses
`AC-(\d{3}):`, and a different series would be invisible to the spec gate. For the same reason,
**nothing may sit between the ID and its colon**: `- [ ] AC-003（再オープン: …）: …` does not match,
so put any annotation after the colon (`- [ ] AC-003: （再オープン: …）…`). This bites reconcile
plans in particular, where re-opened IDs invite a parenthetical. The `[E2E]` marker
goes *after* the colon so the gate keeps matching, and `run-tests` / `pre-pr` locate E2E ACs by
grepping for the marker.

**Where the content comes from.** If a spec exists, take the scenarios from `docs/01-02_e2e/`
(one file per `E2E-NNN`; a project not yet migrated has them as the spec's `## E2E シナリオ`
section) — one E2E AC per `E2E-NNN`, and reference it so the trace survives:

```markdown
- [ ] AC-005: [E2E] E2E-001 のとおり、{前提}から{完了条件}まで通しで実行できる
```

If the work is small enough that `/create-spec` was skipped, derive the E2E AC from the goal
image (`## ゴール像` の主要ユーザージャーニー) of the source US instead. For a refactoring plan,
take the E2E scenario the affected code already participates in. If none of these exist, ask the
user for the through-flow directly — **do not create a functional plan with fragment ACs only.**

**Effect on completion**: a plan is not complete while any E2E AC is unchecked, even if every
functional AC is `- [x]`. This is stated in the generated plan itself (see the template) so a
later session reading only the file knows it.

---

## Files to generate

| File path | Role |
|-----------|------|
| `exec-plans/active/YYYY-MM-{Q1}.md` | The execution plan itself (follows the template below) |
| `.claude/views/YYYY-MM-{Q1}.view.md` | Drafting mode only: the expanded view shown to the human. **Temporary, not committed** (`.gitignore`); the plan's Decision Log records the commit it was generated from ([`expanded-view.md`](expanded-view.md)) |

---

## Template for `exec-plans/active/YYYY-MM-{name}.md`

```markdown
---
status: active
created: YYYY-MM-DD
completed:
---

# {Q1: Plan name}

## Goal & Scope
{Answer to Q2}

## Acceptance Criteria
- [ ] AC-001: {Criterion 1}
- [ ] AC-002: {Criterion 2}
- [ ] AC-003: [E2E] {Answer to Q3b — the through-flow that must work end to end}

> このプランは、機能 AC がすべて `- [x]` でも `[E2E]` の AC が緑でなければ完了ではない。
> 完了は、人が全 AC を確認して実装ブランチに complete コミットを積んだとき。途中状態ではマージしない。

<!-- documentation-only プランの場合は上の [E2E] AC と注記を置かず、代わりに
     Decision Log へ `E2E: n/a (documentation-only)` を記録する -->

## Sources

| AC | US（検証可能な bullet） | spec（振る舞いの節） |
|----|------------------------|---------------------|
| AC-001 | `docs/01_requirements/user_stories/US-XXX_{name}.md` § AC-001 | `docs/02_spec/app_spec.md` §「{節名}」 |
| AC-002 | 同上 § AC-002 | 同上 §「{節名}」 |
| AC-003 [E2E] | 同上 § ゴール像／主要ユーザージャーニー | `docs/01-02_e2e/E2E-001_{slug}.md` § E2E-001 |

<!-- 全 AC に行を置く。起点が無い AC は空欄にせず `n/a（理由）` と書く。
     この表の中では AC-NNN の直後にコロンを置かない（spec-gate.py が AC として拾うため）。
     書式・許容される起点・食い違いの扱いは ac-sources.md を参照 -->

## Task Breakdown
{Answer to Q4 in checklist format}

## Progress Log

### YYYY-MM-DD
- Plan created

## Decision Log

```

---

## Steps

**Drafting mode** (see **Two modes**) runs the same steps with the agent writing the answers, and
three steps of its own around them:

- **D1** — Before Step 1: confirm the US is approved (on `main`) — or is in the same bundle, on this
  definition branch ([`../create-spec/bundled-approval.md`](../create-spec/bundled-approval.md)) — and note the commit the documents
  are read at. Draft Q1–Q4 from the US, the spec and the scenarios, in the order of Steps 1–3, over
  the scope the agent proposes. Steps 1–3 still run in full — the plan size check, the walkthrough
  judgement, the sources, the scenario comparison and readiness — and every decision they raise
  becomes a question instead of being asked on the spot or settled by the agent
- **D2** — After Step 3: write the expanded view to `.claude/views/` and put **only the questions** to
  the human, with the view's path ([`expanded-view.md`](expanded-view.md)). With no questions, ask
  for approval of the through-flow as a whole. Apply the answers, re-run the checks on whatever they
  added or changed, and check that the documents have not moved since the view was generated;
  a new question goes back to the human in a regenerated view. **Do not write the plan file while a
  question is open**
- **D3** — At Step 6: add the expanded view's records to `## Decision Log`
  ([`expanded-view.md`](expanded-view.md)「Record format」) alongside the records Steps 1–3 already
  produce (the split, the scenario comparison, ⚠️ reasons)

**Interview mode** runs the steps as written.

1. Complete the Q1–Q4 interview (including Q3b — read the scenarios in `docs/01-02_e2e/` first
   if a spec exists, so the E2E criteria can be derived rather than asked from scratch). At Q3f,
   check the plan size against
   [`../complete-exec-plan/completion-boundary.md`](../complete-exec-plan/completion-boundary.md)
   「Plan size」 and split with the user before going on
2. If the plan changes a process (Q3e — scope table in
   [`process-walkthrough.md`](process-walkthrough.md)), add the walkthrough AC **before** the
   readiness check, so it is checked with the rest
2b. Collect each criterion's sources (Q3d) per [`ac-sources.md`](ac-sources.md), so the readiness
   check that follows can answer `R4` against a named scenario rather than a guess. For every row
   that names an `E2E-NNN`, run complement detection with the user
   ([`../create-spec/e2e-interaction.md`](../create-spec/e2e-interaction.md)) — this is the last
   point before the scenario freezes
3. Run the readiness check (Q3c) over every criterion using [`ac-readiness.md`](ac-readiness.md);
   rewrite the NOT READY ones with the user and note any ⚠️ reasons for the Decision Log. If a
   rewrite changes a `## Sources` row so that it names a different `E2E-NNN`, run Step 2b's
   complement detection on that scenario before going on — the plan freezes it when finalized
4. Confirm today's date in `YYYY-MM-DD` format
5. Create the `exec-plans/active/` directory if it doesn't exist. Write the plan on a branch that is
   not implementing another plan — one implemented plan per branch
   ([`../complete-exec-plan/completion-boundary.md`](../complete-exec-plan/completion-boundary.md)
   「When part of a plan has to merge before the rest」)
6. Apply the interview answers to the template and create `exec-plans/active/YYYY-MM-{name}.md`
7. Update the "Current Phase & Priority Tasks" section of `docs/07_ai_context/CONTEXT.md`
   - Add a link to the newly created plan file in the priority tasks section

---

## Completion criteria

- [ ] `exec-plans/active/YYYY-MM-{name}.md` has been created
- [ ] The file contains `status: active`, `created: YYYY-MM-DD`, goal, acceptance criteria, and task breakdown
- [ ] For any plan implementing requirements or functionality (**refactoring included**):
      **at least one acceptance criterion is an E2E criterion** written as `- [ ] AC-NNN: [E2E] ...`,
      placed after the functional ACs, and traced to an `E2E-NNN` scenario (or to the US goal image
      when no spec exists). For a documentation-only plan: **no `[E2E]` AC is present**, and
      `E2E: n/a (documentation-only)` is recorded in the Decision Log instead
- [ ] The plan states that it is not complete while any `[E2E]` criterion is unchecked, and that it
      is completed by the human confirming every AC and is not merged in an intermediate state
- [ ] The plan size was checked at Q3f: one branch can implement every criterion and one human
      confirmation can cover them, or the plan was split with the user and the split recorded
- [ ] The plan has a `## Sources` table with **a row for every criterion**, each naming a section
      (not just a file) or an explicit `n/a（理由）` — no blank cells, and no colon directly after
      `AC-NNN` inside the table (see [`ac-sources.md`](ac-sources.md)), and no row naming background
      material
- [ ] Every `E2E-NNN` a row names — including one a Q3c rewrite introduced — was compared against
      the comparison set in [`../create-spec/e2e-interaction.md`](../create-spec/e2e-interaction.md), any
      detected gap or contradiction was resolved with the user, and the result is recorded in the
      Decision Log (see [`../create-spec/e2e-interaction.md`](../create-spec/e2e-interaction.md))
- [ ] **Every criterion was checked against [`ac-readiness.md`](ac-readiness.md)**, and the plan
      contains no NOT READY criterion (any ⚠️ has its reason recorded in the Decision Log)
- [ ] If the plan changes a process in the scope of
      [`process-walkthrough.md`](process-walkthrough.md): it carries an AC requiring that
      walkthrough, naming its laps — a description-consistency AC alone does not satisfy this
- [ ] In the drafting mode: the human was shown the expanded view and answered **every** question
      in it (or, with no questions, approved the through-flow as a whole) before the plan file was
      written; no ⚠️ reason, `n/a` reason, AC rewrite or scenario finding was settled by the agent;
      and the Decision Log records the commit the view was generated from and each decision
      ([`expanded-view.md`](expanded-view.md)「Record format」)
- [ ] The priority tasks in `docs/07_ai_context/CONTEXT.md` have been updated

Final report output by the agent:

```
=== Execution plan created ===

File     : exec-plans/active/YYYY-MM-{name}.md
Mode     : drafting（起点 `<commit>`、問い {n} 件に人が回答） | interview
機能 AC  : AC-001, AC-002, ...
E2E AC   : AC-NNN [E2E] ← E2E-001 (or "derived from US-XXX ゴール像")
Sources  : {n}/{n} AC に起点あり  |  n/a {n} 件（{理由}）

=== AC readiness ===
AC-001  READY
AC-002  ⚠️  R4 — {reason, recorded in the Decision Log}
(NOT READY は残さない — 残る場合はプランを確定していない)

Note: 機能 AC がすべて完了しても、[E2E] の AC が緑になるまでこのプランは完了しない。

Next step: Use the start-feature skill to begin implementation
```
