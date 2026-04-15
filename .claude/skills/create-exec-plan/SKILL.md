---
name: create-exec-plan
description: |
  Creates a new execution plan in exec-plans/active/.
  Used when starting a substantial piece of work (feature implementation, documentation, refactoring, etc.) in Phase 2 (requirements/design) or later.
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
2. Generate `exec-plans/active/YYYY-MM-{name}.md`
3. Update the "Current Phase & Priority Tasks" section of `docs/06_ai_context/CONTEXT.md`

---

## Interview

The agent asks the following questions **one at a time, in order**.

| # | Question | Used for |
|---|----------|----------|
| Q1 | What is the name of this plan? (alphanumeric and hyphens, e.g. `user-auth`, `refactor-service-layer`) | Filename |
| Q2 | Please describe the goal and scope in 3 lines or fewer | `## Goal & Scope` |
| Q3 | List the acceptance criteria to consider this plan complete (numbered as `AC-001`, `AC-002`, ...) | `## Acceptance Criteria` |
| Q4 | Break down the tasks (in checklist format) | `## Task Breakdown` |

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

## Task Breakdown
{Answer to Q4 in checklist format}

## Progress Log

### YYYY-MM-DD
- Plan created

## Decision Log

```

---

## Steps

1. Complete the Q1–Q4 interview
2. Confirm today's date in `YYYY-MM-DD` format
3. Create the `exec-plans/active/` directory if it doesn't exist
4. Apply the interview answers to the template and create `exec-plans/active/YYYY-MM-{name}.md`
5. Update the "Current Phase & Priority Tasks" section of `docs/06_ai_context/CONTEXT.md`
   - Add a link to the newly created plan file in the priority tasks section

---

## Completion criteria

- [ ] `exec-plans/active/YYYY-MM-{name}.md` has been created
- [ ] The file contains `status: active`, `created: YYYY-MM-DD`, goal, acceptance criteria, and task breakdown
- [ ] The priority tasks in `docs/06_ai_context/CONTEXT.md` have been updated

Final report output by the agent:

```
=== Execution plan created ===

File: exec-plans/active/YYYY-MM-{name}.md
Next step: Use the start-feature skill to begin implementation
```
