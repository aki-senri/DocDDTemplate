# Completion boundary — where the agent's work ends and the human's confirmation is recorded

> **Single source.** `complete-exec-plan` (entry condition, the complete commit, reopening), `pre-pr`
> (⑦ the boundary check, and which plan it reads), `create-exec-plan` (plan size), `run-exec-plan`
> (handoff), `docode-review` (which plan it reads), `start-feature` and `gc` (backstop) all apply
> **this** file. Do not restate the record format or the boundary check inline in a skill —
> reference this file.

## What `completed` means

A plan is `completed` when **a human has confirmed every AC of the plan, and that confirmation is
recorded**. It does not wait for a PR to merge.

What the human confirms is the behaviour each AC describes — not the code line by line. That is why
the unit of confirmation is the **whole plan** rather than a range of commits: a behaviour does not
map one-to-one onto the commits that produced it, so "which commits were confirmed" cannot be kept
up per commit range. Instead the plan is sized so that "confirmed" always means "every AC of the
plan" (see **Plan size** below).

Completion is a **commit on the implementation branch** — the *complete commit* — stacked after the
implementation commits. It is the boundary in the history: what comes before it is what the human
confirmed; an implementation change after it is not confirmed.

```
abc1234  feat: AC-001 ...                                   ← agent
def5678  feat: AC-002 ...                                   ← agent
0123abc  test: [E2E] ...                                    ← agent
9876fed  complete: 2026-10-login（確認: <確認者>, PR #12 のレビュー）  ← boundary
```

Why the boundary lives in the branch rather than after the merge: confirming the ACs is work the
human already does — in PR review, or by checking the commits before opening one. Completing after
the merge asked for the same confirmation a second time and a PR that only moved a file, and a plan
whose completion was forgotten stayed in `exec-plans/active/` with `CONTEXT.md` going stale. With
the complete commit in the branch, the PR carries its own completion.

---

## Order relative to the PR

Both paths finish in **one PR**. Neither needs a PR that only moves the plan.

| Path | Order |
|------|-------|
| Confirm, then open the PR | implementation commits → `pre-pr` → human confirms every AC (checking the commits) → complete commit → PR → merge |
| Confirm in PR review | implementation commits → `pre-pr` → PR → review confirms every AC → complete commit pushed to the same PR branch → merge |

`pre-pr` runs **before** the complete commit on both paths, while the plan is still in
`exec-plans/active/` — every check that reads `active/` (AC coverage, `[E2E]` coverage, DOC-INV-012)
sees the plan. When `pre-pr` is run again after the complete commit, it finds the plan in
`completed/` by the rule under **Finding the plan of this branch**.

**Merge condition.** A branch that implements a plan is merged only once it carries the plan's
complete commit and no implementation change after it. A plan is **not merged in an intermediate
state** — a branch that has checked some of the plan's ACs and left others unchecked stays
unmerged. (A branch that only adds or re-opens a plan, with no implementation of it — a new plan,
a reconcile plan's re-opened ACs — is not an intermediate state; there is nothing to confirm yet.)

A run that stops partway (a HALT, an interrupted session) leaves the plan in `active/` on the same
branch, and work continues there. Confirmation happens once, when every AC is done.

**When an AC is no longer wanted.** The human withdraws it — a decision about what the plan
delivers. The line is removed from `## Acceptance Criteria` (and its `## Sources` row), and the
Decision Log keeps it: `- 取り下げ: AC-NNN（<元の AC 行の文言>）— <理由>`. No colon directly after
the ID there — `spec-gate.py` and `run-tests` read every `AC-NNN:` as a criterion to implement and
test, and a withdrawn one must not reach them. Not the agent's call, and not a way to pass completion
with an AC nobody implemented.

**When part of a plan has to merge before the rest.** Split the plan: the human moves the
unfinished ACs into a new plan (written through `create-exec-plan`, so they pass its readiness and
sources questions), records the split in both plans' Decision Logs, and the remaining plan is then
confirmed and completed as a whole. Splitting is a decision about what this plan delivers, so it is
the human's — not the agent's, and not a reason to merge with unchecked ACs.

**The new plan does not ride on this branch.** It is added by a change of its own (or after this
branch merges), and implemented on a branch of its own. A branch that carries one plan's
implementation and a second plan's unfinished ACs has no way to tell the checks below which code
belongs to which plan, so it would read as an intermediate state; keeping one implemented plan per
branch is what lets "this branch's plan" stay unambiguous.

---

## Plan size

A plan is written to the size that **one branch can implement in full, and one human confirmation
can cover in full**. `create-exec-plan` asks this before the plan is finalized; a plan that does not
fit is split there, where splitting costs nothing.

Signs that a plan should be split (a guide, not a limit):

| Sign | Split along |
|------|-------------|
| Some ACs could ship and be used without the others | The groups that are useful on their own — each gets its own `[E2E]` AC |
| An AC waits on a decision or a promotion that has not happened | Put that AC in a later plan |
| The human could not confirm every AC's behaviour in one sitting | Smaller plans, each confirmable at once |
| Roughly more than ten functional ACs | Usually one of the lines above already applies |

**Do not split across an `[E2E]` AC's through-flow.** The ACs a scenario's flow passes through
belong to the plan that carries that `[E2E]` AC; split between flows, not inside one.

---

## The human confirmation record

The entry condition of completion. It lives in the plan's `## Decision Log`, as a bullet at the
start of a line:

```markdown
- 人の確認: 全 AC（AC-001〜AC-NNN）— <確認者>, YYYY-MM-DD, <方法>。根拠: <根拠>
```

| Field | What it holds |
|-------|---------------|
| `<確認者>` | The person who confirmed — a name or account, as they are known in the project |
| `<方法>` | How they confirmed: `PR #NN のレビュー`, `コミット後の確認（<short sha> まで）`, or a short description of another method |
| `<根拠>` | What the record rests on — exactly one of the three below |

| `<根拠>` | When | Written as |
|----------|------|------------|
| The person's own statement | They said, in this session, that they confirmed every AC of the plan | `発言「<their words, verbatim>」` |
| A PR approval | The PR that carries the plan was approved | `PR #NN approve（<reviewer>, <submittedAt>, <commit の short sha>）` — read with `gh pr view NN --json reviews` |
| The person wrote the record | The record was written by the person themselves | `本人記入` |

**Who writes it.** The human, or the agent **transcribing** one of the first two. The agent never
infers or composes the fact of confirmation. None of these is a confirmation:

- tests passing, `pre-pr` passing, a `docode-review` verdict — those are the agent's checks, which
  the human confirmation is added to;
- the human not objecting, or asking for the next step;
- a statement or an approval that covers only some ACs (`AC-001 は OK`) — ask about the rest;
- a statement from an earlier session that is not in the plan file — it is not in hand; ask again.

**An approval covers the commit it was given on.** If the approval's commit is older than the
branch's last implementation change (the same check as **After the boundary** below, run from the
approval's commit instead of the boundary), it does not cover what came after; ask for a new
confirmation. And it must still stand: among the reviewer's reviews in
`gh pr view NN --json reviews`, the latest **decisive** one — `APPROVED` or `CHANGES_REQUESTED`;
a `COMMENTED` review decides nothing and is skipped — is `APPROVED`, and it has not been dismissed.

**Whose approval counts.** A person the project recognizes as a reviewer: `authorAssociation` is
`OWNER`, `MEMBER` or `COLLABORATOR`, and the author is not a bot or an app. GitHub accepts an
approval from anyone who can see the PR, so an approval outside this — or one you are unsure about —
is not transcribed; ask the human instead.

**When no record and no evidence is in hand, completion stops** and asks the human whether they
have confirmed every AC, and how. Their answer is the evidence (`発言「…」`). Asking is not the
same as answering for them: a reply that does not say every AC was confirmed is not a record.

**Which record counts.** The last `- 人の確認:` bullet that comes after the last `- 再オープン:`
bullet (see **Reopening before the merge**). A confirmation before a reopen covered a state that no
longer exists. Both bullets stay — the Decision Log is append-only.

---

## The complete commit

A commit that carries **only** the completion:

1. The confirmation record, if it is being transcribed now
2. Frontmatter: `status: completed`, `completed: YYYY-MM-DD`
3. A Progress Log entry for the completion
4. The move `exec-plans/active/<plan>.md` → `exec-plans/completed/<plan>.md`
5. The priority-task update in `docs/07_ai_context/CONTEXT.md`

Nothing else — no implementation, no test, no other document. The boundary has to change no
behaviour, so that the commit itself needs no confirmation and "after the boundary" can be checked
mechanically.

**Author.** The agent or the human — the condition is the confirmation record, not who commits.
**Pushing** the commit (the second path pushes it to the PR branch) is an outward action and
happens when the human asks for it. A repository that dismisses approvals on new commits will ask for
the PR to be approved again; the complete commit changes no behaviour, so that approval is of the
boundary only.

**Message (recommended, not checked).** So that a person can find the boundary in `git log` at a
glance:

```
complete: <plan file name without .md>（確認: <確認者>, <方法>）

Confirmed-by: <確認者>
Confirmed-via: <方法>
```

No gate reads the message. The plan's Decision Log is the record; the message is a reading aid.

---

## Finding the plan of this branch

Skills that read "the plan" (`pre-pr`, `docode-review`) take **the plans this branch touched**, in
two places, so that they work both before and after the complete commit:

```bash
# plans in active/ that this branch added or edited (another active plan is not this branch's;
# AM leaves out the old path of a plan the branch has since moved to completed/)
# (against the merge-base, so committed, staged and unstaged edits all count)
git diff --name-only --diff-filter=AM "$(git merge-base main HEAD)" -- exec-plans/active/ 2>/dev/null || true
git ls-files --others -- exec-plans/active/ 2>/dev/null || true   # new, untracked — gitignored ones included
# plans this branch moved into completed/ (rename or add) — the complete commit
git diff --name-only --diff-filter=AR main...HEAD -- exec-plans/ 2>/dev/null | grep '^exec-plans/completed/' || true
# a move into completed/ not committed yet (an interrupted complete-exec-plan run) — matched on the
# destination; a move out of completed/ is an interrupted reopen, and its plan is the one in active/
git status --porcelain -uall -- exec-plans/ 2>/dev/null | grep -E '^(A|\?\?) +exec-plans/completed/|^R.* -> exec-plans/completed/' || true
```

The `active/` queries match what `check-doc-invariants` counts as this PR's plans in PR mode (it, too, lists
untracked files including gitignored ones), so `pre-pr` ③ and ⑤–⑦ read the same plan.

A file without an `## Acceptance Criteria` section is not a plan — a `/gc` report
(`exec-plans/completed/YYYY-MM-gc.md`) is the usual one; leave it out.

**A plan this branch has not started.** A branch can carry a plan without implementing it: it adds
a new plan, or re-opens ACs in a reconcile plan together with the spec fix that re-opens them. There
is nothing to confirm yet, and its ACs are not held as uncovered (`pre-pr` ⑤ / ⑦, `run-tests`).
Both of these must hold, so that a branch which implemented code but did not tick a box is not taken
for one:

```bash
# (a) no AC line goes to [x] on this branch — working tree included
git diff "$(git merge-base main HEAD)" -- <plan> 2>/dev/null | grep -E '^\+- \[x\] AC-' || true   # for an untracked plan: grep the file itself
# (b) nothing changed outside exec-plans/ and docs/ — committed, staged, unstaged or untracked
git diff --name-only "$(git merge-base main HEAD)" -- . ':(exclude)exec-plans/' ':(exclude)docs/' 2>/dev/null || true
git ls-files --others --exclude-standard -- . ':(exclude)exec-plans/' ':(exclude)docs/' 2>/dev/null || true
```

No output from all three means not started. This judges the whole branch, which is why a branch
carries one implemented plan at most (「When part of a plan has to merge before the rest」).

(b) cannot separate the work of a **documentation-only** plan (its Decision Log records
`E2E: n/a (documentation-only)`) from a spec fix, since both live in `docs/`. For such a plan, a
branch that changed `docs/` and ticked no box is **not** taken as not started: it is reported as an
intermediate state (⚠️), so documentation work cannot pass unconfirmed by leaving its boxes empty.
One case reads the same and is not: a documentation-only reconcile plan re-opened together with the
docs fix that re-opens it. The routing sends that fix to `main` directly, where no `pre-pr` runs; if
it goes through a PR instead, the ⚠️ does not block, and the human says it is a re-open.

**A change with no plan** implements none of the plans in `active/`, so their ACs are not held
against it: its tests must pass, and that is all. Finding no plan is not enough to call a change
plan-less — a branch can implement a plan that is already on `main` without ever editing the plan
file — so it is decided from what the branch changed and what its commits record:

| No plan found, and the branch… | Then |
|-------------------------------|------|
| changed nothing outside `exec-plans/` and `docs/` (a spec fix, a document change) | Plan-less. Nothing there can be a plan's code. (A documentation-only plan from `main` that the branch works on without ticking a box reads the same; its boxes are ticked as the work is done) |
| changed something else, and a commit message carries a `Spec-Override: <理由>` trailer | Plan-less — the `exec-plans/.spec-override` exception (CLAUDE.md「例外処理」 has the trailer written, since the override file is deleted before the PR) |
| changed something else, with no such trailer | Ask the human which plan the change implements; until they answer, hold on the coverage of every plan in `active/`, as if each might be it. If they answer that it implements none — it was an override — record their answer as the trailer, in an empty commit on the branch (`git commit --allow-empty`, `Spec-Override: <理由>（<確認者>, YYYY-MM-DD の回答）`), and it is plan-less from then on |

```bash
git log --format=%B main..HEAD 2>/dev/null | grep -E '^Spec-Override:' || true
```

Use the branch the PR merges into in place of `main`, and make sure it is current (`git fetch`, then
`origin/main` if the local `main` lags): a stale `main` makes plans completed there look like this
branch's, and its commits look like the branch's own.

## After the boundary

The **boundary** of a plan that this branch completed is the commit that brought its file into
`completed/` — the complete commit, or after a reopen the latest one:

```bash
git log -1 --diff-filter=AR --format=%H main..HEAD -- exec-plans/completed/<plan>.md
```

Not "the last commit that touched the file": a later edit to the completed plan (a note appended, a
merge of `main` that edits it) would move the boundary past implementation changes that came before
it, and every check below would go silent.

An **implementation change after the boundary** is any change the branch itself made after that
commit, outside `exec-plans/` and `docs/07_ai_context/CONTEXT.md` — committed or not:

```bash
# the branch's own commits after the boundary; ^main leaves out what a merge of main brought in
git log --no-merges --format= --name-only <boundary>..HEAD ^main -- . ':(exclude)exec-plans/' ':(exclude)docs/07_ai_context/CONTEXT.md'
# uncommitted changes
git status --porcelain -- . ':(exclude)exec-plans/' ':(exclude)docs/07_ai_context/CONTEXT.md'
```

Any output means the confirmation does not cover the branch as it stands. **Reopen** the plan (below)
and confirm again. Documents count too: a spec edit after the boundary can change what an AC means.

**The boundary itself** must carry only the completion. Anything else folded into it was never
before the boundary, so the confirmation did not cover it:

```bash
git show --format= --name-only <boundary> -- . ':(exclude)exec-plans/' ':(exclude)docs/07_ai_context/CONTEXT.md'
```

Any output is the same finding as a change after the boundary.

What this does not see: an implementation edit made while resolving a conflict inside a merge commit
(`--no-merges` skips it), and an edit to the completed plan's own AC lines (`exec-plans/` is
excluded so that the plan's records can be added to; only an unchecked box is caught, below). Both
are a reader's to notice.

**Merging `main` into the branch** after the boundary is not the branch's own change and is not
counted by the command above. Two things it can bring in still matter, and both are checked:

| What came in from `main` | Why it matters | Check |
|--------------------------|----------------|-------|
| A change to a file the plan's `## Sources` names — including its move or rename | The human confirmed against a target that has since moved. Whether the named *section* changed is a reading, so it is reported, not blocked. This is also the only check that sees a Sources row broken after the complete commit: DOC-INV-012 reads `active/` plans only | `git diff --name-only --no-renames <boundary> HEAD` (so a renamed file shows its **old** path) intersected with the `## Sources` paths → the human decides whether to reopen |
| An unchecked AC inside the completed plan | A fix on `main` appended a re-opened AC to this plan while it was in flight. CLAUDE.md closes a reconcile plan to appends once its implementation has started, but from `main` that is not always visible — this branch's plan was still in `active/` there. Git carries the appended line into the moved file, and a completed plan with an unchecked AC is one nobody will implement | `grep -nE '^- \[ \] AC-[0-9]{3}:' exec-plans/completed/<plan>.md` → reopen |

In either case reopen the plan in this branch and record why, the same as a stale in-progress plan
(CLAUDE.md「現バージョン修正による stale の扱い」: a plan completed on a branch that has not merged is
still in progress). If the PR is merged without the branch first taking in `main`, git combines them
at the merge and no check on the branch sees it — `gc` reports an unchecked AC in a completed plan on
`main` afterwards.

---

## Reopening before the merge

When a finding arrives after the complete commit and before the merge — a review comment, a spec fix
from `main`, a change someone already made after the boundary — the plan goes back to `active/` in
the same branch. Deciding to reopen is the human's (it withdraws their confirmation); the commit
can be made by the agent on their instruction.

The reopen commit carries only:

1. The move `exec-plans/completed/<plan>.md` → `exec-plans/active/<plan>.md`
2. Frontmatter: `status: active`, `completed:` emptied
3. A Decision Log bullet:
   ```markdown
   - 再オープン: <理由 — 指摘・main の修正・境界後の変更>。対象 AC: AC-NNN, …（無ければ「なし — <理由>」）
   ```
4. The ACs whose behaviour the fix changes set back to `- [ ]`. ACs the fix does not change stay
   `- [x]`; a fix that changes no AC's behaviour (a refactor, a wording fix) unchecks none.
5. The priority-task update in `docs/07_ai_context/CONTEXT.md`

From there the plan is an ordinary active plan: `run-exec-plan` and `start-feature` find it in
`active/`, the unchecked ACs go through the per-AC flow (`../run-tests/red-first.md` applies to them
as to any re-opened AC), `pre-pr` runs again, and the human confirms every AC again before a new
complete commit. The earlier `- 人の確認:` bullet stays in the log and no longer counts.

**After the merge** nothing is reopened in place. A completed plan on `main` is history; a later
change to what it delivered follows CLAUDE.md「現バージョン修正による stale の扱い」 (a reconcile plan
re-opens the same AC-ID) or a new plan.

**A plan merged without its complete commit** — the merge condition was skipped, or the plan predates
this rule and was merged before completion — is completed afterwards the same way: a confirmation
record, then the complete commit, in whatever change the project uses for a fix on `main`. This is
the one case that needs a change of its own; it is the cost of the skipped condition, not a second
path.

---

## Where this is applied

| Call site | When | Action |
|-----------|------|--------|
| `create-exec-plan` | Before the plan is finalized | Ask whether one branch can implement every AC and one confirmation cover them (**Plan size**); split there if not |
| `run-exec-plan` | Handoff after the loop | Names the next steps: `pre-pr`, then the human's confirmation and `complete-exec-plan` **on this branch, before the merge**. Never completes the plan itself — the confirmation is not the driver's |
| `pre-pr` | Before the PR — and again if re-run | Reads the plan from `active/` or from this branch's `completed/` (**Finding the plan of this branch**), and has `run-tests` cover that plan's ACs. ⑦: plan not yet completed → ℹ️ (does not block — the second path completes after the PR); ACs left unchecked → ⚠️ (do not merge an intermediate state); implementation change after the boundary, or an unchecked AC inside the completed plan → ❌; a merge of `main` after the boundary changed a file the plan's `## Sources` names → ⚠️ |
| `complete-exec-plan` | After the human's confirmation, before the merge | Entry condition = the confirmation record (stop and ask when absent); makes the complete commit — resuming one an earlier run moved but did not commit; reopens before the merge |
| `run-tests` | AC coverage | Covers the ACs of the plan in `active/`, or of the plan this branch moved into `completed/` when `pre-pr` is re-run after the complete commit |
| `docode-review` | When it collects the plan | Reads the plan from `active/` or from this branch's `completed/`, so a review of a diff that includes the complete commit still has the ACs |
| `start-feature` | Choosing the plan | A plan this branch already completed is reopened first, not re-created |
| `spec-gate.py` (and CLAUDE.md's spec-first table) | An implementation request with no plan in `active/` | Besides proposing `create-exec-plan`, points at reopening when the work fixes a plan this branch already completed |
| `gc` | Weekly, on `main` | A plan still in `active/` whose ACs are all `- [x]` was merged without its complete commit: report it and suggest the confirmation and `complete-exec-plan`. A plan in `completed/` with an unchecked AC took in a re-opened AC after its confirmation: report it so the AC is re-opened in a reconcile plan |

**What no site checks.** The commit message format, and whether the person named in a record really
looked. The record says who confirmed and on what evidence; the evidence itself is the human's.
