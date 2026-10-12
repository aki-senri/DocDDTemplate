---
name: complete-exec-plan
description: |
  Skill to transition an execution plan to completed status.
  When a human has confirmed every acceptance criterion of the plan and that confirmation is
  recorded, moves the plan from exec-plans/active/ to completed/, updates CONTEXT.md, and makes
  the complete commit on the implementation branch — the boundary between the agent's work and
  the human's confirmation. Runs before the merge, in the same PR as the implementation.
  Also reopens a plan completed on the branch when a finding arrives before the merge.
disable-model-invocation: true
---

# Skill: Complete Execution Plan

> **When to run**: When a human has confirmed every acceptance criterion of the plan — by checking
> the commits before opening a PR, or in PR review — **before the merge, on the implementation
> branch**
>
> **Purpose**: Record where the agent's work ends and the human's confirmation begins, as a commit
> in the branch, and keep the "Current Phase & Priority Tasks" in CONTEXT.md up to date.
>
> **Prerequisites**:
> - The target execution plan must exist in `exec-plans/active/`
> - Every acceptance criterion is `- [x]`
> - **A human has confirmed every AC, and the record of it is in the plan or its evidence is in
>   hand** — see [`completion-boundary.md`](completion-boundary.md)「The human confirmation record」.
>   A merged PR is not required, and not the condition.

The meaning of `completed`, the record format, the complete commit, the merge condition and the
reopen rule live in [`completion-boundary.md`](completion-boundary.md) (single source). This skill
is the procedure.

---

## What this skill does

1. Confirm the target execution plan
2. Confirm the human confirmation record (stop and ask when there is none)
3. Re-run the blocking checks
4. Update and move the plan file
5. Update `docs/07_ai_context/CONTEXT.md`
6. Make the complete commit
7. Guide the user to the next step

Reopening a plan this branch already completed is a separate procedure — see **Reopening before the
merge** at the end.

---

## Steps

### Step 1: Confirm the target plan

Find the plan this branch implements with the commands in
[`completion-boundary.md`](completion-boundary.md)「Finding the plan of this branch」 — not every
file in `exec-plans/active/`, which can hold other plans that came from `main`. When they find
nothing, fall back to listing `exec-plans/active/`.

- If there is only one candidate, confirm it with the user
- If there are multiple, prompt the user to select one
- **Resuming an interrupted run**: if `git status` shows a plan already moved into
  `exec-plans/completed/` but not committed, an earlier run stopped before its commit (Step 6), and
  the checks of Step 3 no longer describe the tree as it is now. Undo the uncommitted completion and
  start again: `git mv` the file back to `exec-plans/active/`, set `status: active` and empty
  `completed:`, remove the uncommitted completion entry from the Progress Log, and revert the
  uncommitted `CONTEXT.md` change. **Keep a `- 人の確認:` bullet** the moved file carries — Step 2
  then finds it and does not ask again. Select that plan

### Step 2: Confirm the human confirmation record

Look in the plan's `## Decision Log` for the record that counts — the last `- 人の確認:` bullet
after the last `- 再オープン:` bullet ([`completion-boundary.md`](completion-boundary.md)「Which
record counts」).

| What is in hand | Action |
|-----------------|--------|
| A record that counts, covering every AC | Proceed |
| No record, but the user said **in this session** that they confirmed every AC of the plan | Transcribe it with `根拠: 発言「<their words, verbatim>」` and proceed |
| No record, but the PR carrying the plan is approved | Read the reviews (`gh pr view NN --json reviews`) and apply [`completion-boundary.md`](completion-boundary.md)「An approval covers the commit it was given on」「Whose approval counts」: the reviewer is the project's (`authorAssociation` `OWNER` / `MEMBER` / `COLLABORATOR`, not a bot or an app); their latest decisive review (`APPROVED` or `CHANGES_REQUESTED` — `COMMENTED` is skipped) is `APPROVED` and not dismissed; and it was given on the commit that carries the branch's last implementation change, or later. Then transcribe it with `根拠: PR #NN approve（…）` and proceed. If any of these fails, or you are unsure, it is not a confirmation — ask |
| None of the above, or evidence covering only some ACs | **Stop.** Ask the user whether they have confirmed every AC of the plan, and how. Do not proceed on a reply that does not say every AC was confirmed |

Never write the record from anything else — not from green tests, a `pre-pr` pass, a
`docode-review` verdict, or the user's silence. Those are checks the confirmation is added to, not
the confirmation ([`completion-boundary.md`](completion-boundary.md)「Who writes it」).

### Step 3: Re-run the blocking checks

The human confirmed behaviour; this step makes sure the branch they confirmed is still green.
Run only the checks that **block** completion — the ⚠️ evidence checks (red-first, process
walkthrough, `## Sources`, `docode-review` record) are reported by `pre-pr` and not repeated here.

- Confirm every criterion has `- [x]`
  - If any criterion is unchecked, the plan cannot be completed: finish it, split the plan (the
    new plan goes to a change and a branch of its own), or — if
    the human no longer wants it — have them withdraw it
    ([`completion-boundary.md`](completion-boundary.md)「When part of a plan has to merge before the
    rest」「When an AC is no longer wanted」 — both the human's decision, recorded in the decision
    log). Do not complete with unchecked criteria
- Check that the plan's `## Sources` rows still resolve, while the plan is still in `active/` —
  after the move DOC-INV-012 no longer reads it: run `check-doc-invariants`' DOC-INV-012 on this plan
  alone (its Step 8, "One plan's rows only"). An ❌ holds the completion; present the row to the user, who repoints it (do not repair it here —
  `../create-exec-plan/ac-sources.md`「When a source cannot be opened」)
- Run the `run-tests` skill — for **this plan's** ACs (it narrows to the plan this branch implements
  when called from here) — and verify:
  - All tests pass
  - All AC-IDs have corresponding tests (AC coverage)
  - **Every `[E2E]` AC has a test that exists and passed** (E2E coverage) — a plan whose functional
    ACs are all `- [x]` is still not complete while the through-flow is unverified
- If any condition is not met, put the completion on hold and prompt for action

These are re-run rather than taken from `pre-pr` because they are mechanical and cheap, and because
fixes can land between `pre-pr` and the confirmation (the second path in
[`completion-boundary.md`](completion-boundary.md)「Order relative to the PR」 completes after
review).

Two situations, two outcomes (same split as `run-tests` and `pre-pr`):

| Situation | Outcome |
|-----------|---------|
| The plan **has** a `[E2E]` AC, but its test is missing / did not run / failed | ❌ **hold the completion** |
| The plan has **no** `[E2E]` AC at all | ⚠️ **report only, completion may proceed** |

The second case has legitimate causes (the plan predates the E2E requirement, or it is
documentation-only — see `create-exec-plan`). Report it, record the reason in the decision log,
and proceed. Do not write the criterion here.

### Step 4: Update and move the file

Update and move the target file in the following order.

1. If the confirmation record was transcribed in Step 2, append it to the `## Decision Log`
2. Update the frontmatter:
   ```yaml
   ---
   status: completed
   created: YYYY-MM-DD
   completed: YYYY-MM-DD   ← enter today's date
   ---
   ```
3. Append a completion entry to the progress log:
   ```markdown
   ### YYYY-MM-DD
   - All acceptance criteria met and confirmed by <確認者> (<方法>). Transitioned plan to completed status.
   ```
4. Move the file to `exec-plans/completed/` (create it if it doesn't exist) with `git mv`, so the
   history shows a move

### Step 5: Update CONTEXT.md

Update the "Current Phase & Priority Tasks" section of `docs/07_ai_context/CONTEXT.md`.

- Remove the completed plan from the priority tasks
- Check remaining plans in `exec-plans/active/` and reflect the next priority tasks
- If `active/` is empty, write "Priority tasks: Please create the next exec-plan"
- If a phase transition occurs (e.g., Phase 1 → Phase 2), update the current phase as well

Another branch completing a plan in parallel edits the same section; a conflict at merge is
resolved from the state of `exec-plans/active/` after both merges.

### Step 6: Make the complete commit

Commit Steps 4–5 as one commit that carries **nothing else** — no implementation, no test, no other
document ([`completion-boundary.md`](completion-boundary.md)「The complete commit」).

If the working tree has other changes — anything outside the plan file and `CONTEXT.md` — **do not
commit them before the complete commit**: anything
committed before the boundary reads as confirmed, and the human did not confirm them. Stop and ask the
user. Either they set the changes aside and the complete commit is made without them, or the changes
belong to the plan — then they are committed, Step 3 runs again, and the confirmation (Step 2) must
cover them, which for a confirmation given before they existed means asking again.

Recommended message (not checked by any gate):

```
complete: <plan file name without .md>（確認: <確認者>, <方法>）

Confirmed-by: <確認者>
Confirmed-via: <方法>
```

**Do not push** unless the user asks. On the "confirm in PR review" path, the commit goes to the
existing PR branch; on the "confirm, then open the PR" path, the PR is created next. Either way it is
the user's step.

### Step 7: Guide to the next task

| Situation | Guidance |
|-----------|---------|
| The PR is not open yet | Push and create the PR; it can merge as it stands — it carries its own completion |
| The PR is open | Push the complete commit to the PR branch; the PR can then merge |
| Other plans exist in `exec-plans/active/` | After the merge, start the next plan with `start-feature` |
| `exec-plans/active/` is empty | After the merge, create the next plan with `create-exec-plan` |
| A phase transition occurred | Create the necessary documents for the next phase |

If a finding arrives before the merge — a review comment, a spec fix from `main` — the plan is
reopened (below), not left completed while the code changes.

---

## Reopening before the merge

When the human decides that a plan this branch already completed must change before the merge,
follow [`completion-boundary.md`](completion-boundary.md)「Reopening before the merge」: one commit
that moves the plan back to `exec-plans/active/`, sets `status: active` and empties `completed:`,
appends `- 再オープン: …` to the Decision Log, unchecks the ACs whose behaviour the fix changes, and
updates the priority tasks in `CONTEXT.md`.

The decision to reopen is the human's — it withdraws their confirmation. Do not reopen on your own
judgement, and do not fix the code while the plan stays in `completed/`: a change after the boundary
is exactly what `pre-pr` ⑦ reports as ❌.

After reopening, the plan is an ordinary active plan: implement, `pre-pr`, a new confirmation, and
this skill again for a new complete commit.

---

## Completion criteria

- [ ] A confirmation record that counts — covering every AC, with its evidence (`発言「…」`,
      `PR #NN approve（…）` or `本人記入`) — is in the plan's Decision Log, and none was written from
      anything else
- [ ] Every AC is `- [x]` (or the plan was split by the human and the remaining ACs are all `- [x]`)
- [ ] The plan's `## Sources` rows resolve (DOC-INV-012 on this plan, before the move)
- [ ] Ran `run-tests` and all tests pass
- [ ] All AC-IDs have corresponding tests
- [ ] Every `[E2E]` AC has a passing test (or its absence was reported / recorded in the decision log)
- [ ] The target file's frontmatter shows `status: completed` and `completed: YYYY-MM-DD`
- [ ] The file has been moved to `exec-plans/completed/`
- [ ] The priority tasks in `docs/07_ai_context/CONTEXT.md` have been updated
- [ ] The complete commit carries only the completion, and was not pushed without the user asking
- [ ] The next action has been communicated

Final report output by the agent:

```
=== Execution plan completed ===

Completed plan : exec-plans/completed/YYYY-MM-{name}.md
人の確認       : <確認者>, <方法>（根拠: 発言 / PR approve / 本人記入）
Complete commit: <short sha>  complete: YYYY-MM-{name}（確認: …）
CONTEXT.md     : Priority tasks updated

Next action: {push and create the PR | push to the PR branch, then merge | …}
```
