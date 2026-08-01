---
name: create-exec-plan
description: |
  Creates a new execution plan in exec-plans/active/.
  Used when starting a substantial piece of work (feature implementation, documentation, refactoring, etc.) in Phase 2 (requirements/design) or later.
  Every plan carries at least one [E2E] acceptance criterion alongside the functional ones, so a
  plan cannot be completed by turning fragments green without the through-flow working.
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
2. Generate `exec-plans/active/YYYY-MM-{name}.md` with at least one `[E2E]` acceptance criterion
   alongside the functional ones
3. Update the "Current Phase & Priority Tasks" section of `docs/07_ai_context/CONTEXT.md`

---

## Interview

The agent asks the following questions **one at a time, in order**.

| # | Question | Used for |
|---|----------|----------|
| Q1 | What is the name of this plan? (alphanumeric and hyphens, e.g. `user-auth`, `refactor-service-layer`) | Filename |
| Q2 | Please describe the goal and scope in 3 lines or fewer | `## Goal & Scope` |
| Q3 | List the acceptance criteria to consider this plan complete (numbered as `AC-001`, `AC-002`, ...) | `## Acceptance Criteria` |
| Q3b | Which end-to-end scenario must work when every criterion above is met? (see **E2E acceptance criteria** below) | `## Acceptance Criteria` (last entries) |
| Q4 | Break down the tasks (in checklist format) | `## Task Breakdown` |

---

## E2E acceptance criteria (required)

Every plan must carry **at least one E2E acceptance criterion** in addition to its functional
ones. Functional ACs are fragments: each can be green while the thing as a whole is unusable.
The E2E AC is the criterion that the fragments add up.

**Notation** — an E2E AC is an ordinary numbered AC whose description starts with the `[E2E]`
marker:

```markdown
- [ ] AC-005: [E2E] {the through-flow that must work end to end}
```

Keep the `AC-NNN:` numbering continuous with the functional ACs and place the E2E entries last.
Do **not** invent a separate ID series (`AC-E01:`) — `.claude/hooks/spec-gate.py` parses
`AC-(\d{3}):`, and a different series would be invisible to the spec gate. The `[E2E]` marker
goes *after* the colon so the gate keeps matching, and `run-tests` / `pre-pr` locate E2E ACs by
grepping for the marker.

**Where the content comes from.** If a spec exists, take the scenarios from its
`## E2E シナリオ` section — one E2E AC per `E2E-NNN`, and reference it so the trace survives:

```markdown
- [ ] AC-005: [E2E] E2E-001 のとおり、{前提}から{完了条件}まで通しで実行できる
```

If the work is small enough that `/create-spec` was skipped, derive the E2E AC from the goal
image (`## ゴール像` の主要ユーザージャーニー) of the source US instead. If neither exists, ask
the user for the through-flow directly — **do not create a plan with functional ACs only.**

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
2. Confirm today's date in `YYYY-MM-DD` format
3. Create the `exec-plans/active/` directory if it doesn't exist
4. Apply the interview answers to the template and create `exec-plans/active/YYYY-MM-{name}.md`
5. Update the "Current Phase & Priority Tasks" section of `docs/07_ai_context/CONTEXT.md`
   - Add a link to the newly created plan file in the priority tasks section

---

## Completion criteria

- [ ] `exec-plans/active/YYYY-MM-{name}.md` has been created
- [ ] The file contains `status: active`, `created: YYYY-MM-DD`, goal, acceptance criteria, and task breakdown
- [ ] **At least one acceptance criterion is an E2E criterion** written as `- [ ] AC-NNN: [E2E] ...`,
      placed after the functional ACs, and traced to the spec's `E2E-NNN` (or to the US goal image
      when no spec exists)
- [ ] The plan states that it is not complete while any `[E2E]` criterion is unchecked
- [ ] The priority tasks in `docs/07_ai_context/CONTEXT.md` have been updated

Final report output by the agent:

```
=== Execution plan created ===

File     : exec-plans/active/YYYY-MM-{name}.md
機能 AC  : AC-001, AC-002, ...
E2E AC   : AC-NNN [E2E] ← E2E-001 (or "derived from US-XXX ゴール像")

Note: 機能 AC がすべて完了しても、[E2E] の AC が緑になるまでこのプランは完了しない。

Next step: Use the start-feature skill to begin implementation
```
