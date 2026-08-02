---
name: complete-exec-plan
description: |
  Skill to transition an execution plan to completed status.
  When all acceptance criteria are met, moves the plan from exec-plans/active/ to completed/ and updates CONTEXT.md.
disable-model-invocation: true
---

# Skill: Complete Execution Plan

> **When to run**: When all acceptance criteria of an execution plan are met and the PR has been merged
>
> **Purpose**: Record completed work as history and keep the "Current Phase & Priority Tasks" in CONTEXT.md up to date.
>
> **Prerequisites**:
> - The target execution plan must exist in `exec-plans/active/`
> - All acceptance criteria must be met (verified by the `pre-pr` skill)
> - The PR must have been merged

---

## What this skill does

1. Confirm the target execution plan
2. Final verification that all acceptance criteria are met
3. Move the file from `active/` to `completed/`
4. Update `docs/07_ai_context/CONTEXT.md`
5. Guide the user to the next task

---

## Steps

### Step 1: Confirm the target plan

List the files in `exec-plans/active/` and confirm which plan to complete.

- If there is only one file, select it
- If there are multiple files, prompt the user to select one

### Step 2: Final verification of acceptance criteria

Load the target execution plan file and verify all acceptance criteria are met.

- Confirm all criteria have `- [x]`
- If any criteria are unchecked, inform the user that the plan cannot be completed and prompt for action
  - If a criterion is deemed unnecessary, record the reason in the decision log before proceeding

Run the `run-tests` skill and verify the following:

- All tests pass
- All AC-IDs have corresponding tests (AC coverage)
- Each AC has a red-first record preceding its `done` record (⚠️ report only — see below)
- **Every `[E2E]` AC has a test that exists and passed** (E2E coverage) — a plan whose functional
  ACs are all `- [x]` is still not complete while the through-flow is unverified
- If any condition is not met, put the completion on hold and prompt for action

Two situations, two outcomes (same split as `run-tests` and `pre-pr`):

| Situation | Outcome |
|-----------|---------|
| The plan **has** a `[E2E]` AC, but its test is missing / did not run / failed | ❌ **hold the completion** |
| The plan has **no** `[E2E]` AC at all | ⚠️ **report only, completion may proceed** |

The second case has legitimate causes (the plan predates the E2E requirement, or it is
documentation-only — see `create-exec-plan`). Report it, record the reason in the decision log,
and proceed. Do not write the criterion here.

**Red-first evidence (⚠️ report only).** For each AC, check that the decision log contains an
`AC-NNN red-first:` entry **before** its `AC-NNN done.` entry — the record that the test was written
from the AC and observed failing before the implementation existed (see
[`../run-tests/red-first.md`](../run-tests/red-first.md)). Report any AC that lacks one; this does
**not** hold completion, for the same reason as in `pre-pr`: the evidence is hand-written, so a
missing entry cannot be told apart from a missed note, and completion is the wrong place to
reconstruct it. Never add the entry now — at this point nothing about the order can still be
observed.

### Step 3: Update and move the file

Update and move the target file in the following order.

1. Update the frontmatter:
   ```yaml
   ---
   status: completed
   created: YYYY-MM-DD
   completed: YYYY-MM-DD   ← enter today's date
   ---
   ```
2. Append a completion entry to the progress log:
   ```markdown
   ### YYYY-MM-DD
   - All acceptance criteria met. Transitioned plan to completed status.
   ```
3. Move the file to `exec-plans/completed/` (create it if it doesn't exist)

### Step 4: Update CONTEXT.md

Update the "Current Phase & Priority Tasks" section of `docs/07_ai_context/CONTEXT.md`.

- Remove the completed plan from the priority tasks
- Check remaining plans in `exec-plans/active/` and reflect the next priority tasks
- If `active/` is empty, write "Priority tasks: Please create the next exec-plan"
- If a phase transition occurs (e.g., Phase 1 → Phase 2), update the current phase as well

### Step 5: Guide to the next task

Guide the user to the next action based on the following.

| Situation | Guidance |
|-----------|---------|
| Other plans exist in `exec-plans/active/` | Guide the user to start the next plan with `start-feature` |
| `exec-plans/active/` is empty | Guide the user to create the next plan with `create-exec-plan` |
| A phase transition occurred | Guide the user to create the necessary documents for the next phase |

---

## Completion criteria

- [ ] Ran `run-tests` and all tests pass
- [ ] All AC-IDs have corresponding tests
- [ ] Every `[E2E]` AC has a passing test (or its absence was reported / recorded in the decision log)
- [ ] Red-first evidence was checked per AC and any missing entry was reported (⚠️ — it does not
      hold completion, and is never written after the fact)
- [ ] The target file's frontmatter shows `status: completed` and `completed: YYYY-MM-DD`
- [ ] The file has been moved to `exec-plans/completed/`
- [ ] The priority tasks in `docs/07_ai_context/CONTEXT.md` have been updated
- [ ] The next action has been communicated

Final report output by the agent:

```
=== Execution plan completed ===

Completed plan : exec-plans/completed/YYYY-MM-{name}.md
CONTEXT.md     : Priority tasks updated

Next action: {guidance based on situation}
```
