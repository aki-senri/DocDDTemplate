---
name: create-exec-plan
description: |
  Creates a new execution plan in exec-plans/active/.
  Used when starting a substantial piece of work (feature implementation, documentation, refactoring, etc.) in Phase 2 (requirements/design) or later.
  Any plan that implements requirements or functionality — refactoring included — carries at least
  one [E2E] acceptance criterion alongside the functional ones, so a plan cannot be completed by
  turning fragments green without the through-flow working. Documentation-only plans record
  "E2E: n/a" instead. Every criterion is checked for testability (AC readiness) before the plan
  file is finalized, so ambiguity is caught while it is still cheap to rewrite.
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

1. Collect plan details via an interview
2. Check every criterion for **AC readiness** (testability) and rewrite the ones that fail
3. Generate `exec-plans/active/YYYY-MM-{name}.md` with at least one `[E2E]` acceptance criterion
   alongside the functional ones
4. Update the "Current Phase & Priority Tasks" section of `docs/07_ai_context/CONTEXT.md`

---

## Interview

The agent asks the following questions **one at a time, in order**.

| # | Question | Used for |
|---|----------|----------|
| Q1 | What is the name of this plan? (alphanumeric and hyphens, e.g. `user-auth`, `refactor-service-layer`) | Filename |
| Q2 | Please describe the goal and scope in 3 lines or fewer | `## Goal & Scope` |
| Q3 | List the acceptance criteria to consider this plan complete (numbered as `AC-001`, `AC-002`, ...) | `## Acceptance Criteria` |
| Q3b | Which end-to-end scenario must work when every criterion above is met? For a refactoring plan: which existing through-flow must still work unchanged? (see **E2E acceptance criteria** below) | `## Acceptance Criteria` (last entries) |
| Q3c | *(not asked — run by the agent)* Check every criterion from Q3 / Q3b against the five readiness checks and rewrite the failing ones with the user (see **AC readiness** below) | `## Acceptance Criteria`, `## Decision Log` |
| Q4 | Break down the tasks (in checklist format) | `## Task Breakdown` |

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
| NOT READY | **Rewrite the criterion with the user** — name the failing check (`R2`) and quote the phrase that fails it, propose a rewrite, confirm it. Do not finalize a plan containing a NOT READY criterion |

Rewriting an AC is a decision about *what to build*, so it is made with the user, not on their
behalf. If the user declines to rewrite, record their decision and the failing check in the
Decision Log — a later `run-exec-plan` will still halt on it (this is intended; see the call-site
table in `ac-readiness.md`).

---

## E2E acceptance criteria

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

**Where the content comes from.** If a spec exists, take the scenarios from its
`## E2E シナリオ` section — one E2E AC per `E2E-NNN`, and reference it so the trace survives:

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

<!-- documentation-only プランの場合は上の [E2E] AC と注記を置かず、代わりに
     Decision Log へ `E2E: n/a (documentation-only)` を記録する -->


## Task Breakdown
{Answer to Q4 in checklist format}

## Progress Log

### YYYY-MM-DD
- Plan created

## Decision Log

```

---

## Steps

1. Complete the Q1–Q4 interview (including Q3b — read the spec's `## E2E シナリオ` section first
   if a spec exists, so the E2E criteria can be derived rather than asked from scratch)
2. Run the readiness check (Q3c) over every criterion using [`ac-readiness.md`](ac-readiness.md);
   rewrite the NOT READY ones with the user and note any ⚠️ reasons for the Decision Log
3. Confirm today's date in `YYYY-MM-DD` format
4. Create the `exec-plans/active/` directory if it doesn't exist
5. Apply the interview answers to the template and create `exec-plans/active/YYYY-MM-{name}.md`
6. Update the "Current Phase & Priority Tasks" section of `docs/07_ai_context/CONTEXT.md`
   - Add a link to the newly created plan file in the priority tasks section

---

## Completion criteria

- [ ] `exec-plans/active/YYYY-MM-{name}.md` has been created
- [ ] The file contains `status: active`, `created: YYYY-MM-DD`, goal, acceptance criteria, and task breakdown
- [ ] For any plan implementing requirements or functionality (**refactoring included**):
      **at least one acceptance criterion is an E2E criterion** written as `- [ ] AC-NNN: [E2E] ...`,
      placed after the functional ACs, and traced to the spec's `E2E-NNN` (or to the US goal image
      when no spec exists). For a documentation-only plan: **no `[E2E]` AC is present**, and
      `E2E: n/a (documentation-only)` is recorded in the Decision Log instead
- [ ] The plan states that it is not complete while any `[E2E]` criterion is unchecked
- [ ] **Every criterion was checked against [`ac-readiness.md`](ac-readiness.md)**, and the plan
      contains no NOT READY criterion (any ⚠️ has its reason recorded in the Decision Log)
- [ ] The priority tasks in `docs/07_ai_context/CONTEXT.md` have been updated

Final report output by the agent:

```
=== Execution plan created ===

File     : exec-plans/active/YYYY-MM-{name}.md
機能 AC  : AC-001, AC-002, ...
E2E AC   : AC-NNN [E2E] ← E2E-001 (or "derived from US-XXX ゴール像")

=== AC readiness ===
AC-001  READY
AC-002  ⚠️  R4 — {reason, recorded in the Decision Log}
(NOT READY は残さない — 残る場合はプランを確定していない)

Note: 機能 AC がすべて完了しても、[E2E] の AC が緑になるまでこのプランは完了しない。

Next step: Use the start-feature skill to begin implementation
```
