---
name: promote-spec
description: |
  Promotes accumulated next-version spec changes from a spec/* branch into the current
  development target (main), under human supervision.
  Generates the spec diff, analyses impact on already-implemented and in-flight ACs,
  tags the outgoing version for recoverability, and creates reconciliation exec-plans
  for ACs whose spec changed after they were implemented.
disable-model-invocation: true
---

# Skill: Promote Spec Version

> **When to run**: When the next-version spec accumulated on a `spec/*` branch is ready to
> become the active development target — typically at a sprint boundary.
>
> **Purpose**: Make spec-version promotion a *controlled, visible* event instead of an ad-hoc
> merge. The new spec target is defined by `main`; future spec changes are isolated on a
> `spec/*` branch so in-flight implementation builds against a stable target. Promotion is the
> single reconciliation point: here we surface the concrete spec diff, find which already-built
> work the new spec invalidates, preserve the old version, and turn the drift into explicit
> follow-up work.
>
> **Prerequisites**:
> - A `spec/*` branch exists with committed `docs/**` changes (see CLAUDE.md "仕様バージョンの管理")
> - The working tree is clean and the current branch is the promotion target (normally `main`)
> - Phase 1 documents exist (`docs/`, `exec-plans/`)

---

## Core principle: the merge is a human decision

Promotion changes **what the whole team is building toward**. Per the project rule that
target changes are made carefully by a person, this skill does **not** merge silently:

- It performs the **analysis before** (diff, impact, in-flight collisions) and the
  **bookkeeping after** (reconcile plans, tags, CONTEXT.md).
- The merge itself runs **only after explicit human confirmation** in Step 6.
- If the merge conflicts, the skill **stops and hands resolution to the human** — it never
  forces a resolution.

---

## Terminology

| Term | Meaning |
|------|---------|
| **Current target** | The spec on `main`. What implementation must follow *now*. |
| **Next-version spec** | Spec changes accumulated on a `spec/<label>` branch (docs only). |
| **In-version correction** | A fix to a deficiency in the *current* target. Goes straight to `main`, **not** here. Propagates to in-flight work by design. |
| **Promotion** | Merging a `spec/*` branch into `main`, making it the new current target. |
| **Stale impl** | An AC whose spec changed *after* its code was implemented — code must be reconciled to the new spec. |

> This skill handles **next-version promotion** only. In-version corrections are normal `main`
> commits; record their routing rationale in the Decision Log of the affected exec-plan.

---

## What this skill does

```
① Identify the spec/* branch to promote
② Drift guard: check the spec branch is current with main
③ Diff & classify spec changes (NEW / CHANGED / REMOVED)
④ Impact analysis against completed & active exec-plans (find stale impl + in-flight collisions)
⑤ Present the promotion impact report → STOP for human decision
⑥ Execute promotion after explicit confirmation (tag outgoing version, merge --no-ff)
⑦ Post-promotion bookkeeping (reconcile exec-plan, Decision Log, CONTEXT.md)
⑧ Final report
```

---

## Steps

### Step 1: Identify the spec branch to promote

```bash
git branch --list 'spec/*'
git branch -r --list 'origin/spec/*'
git rev-parse --abbrev-ref HEAD   # confirm we are on the promotion target (normally main)
```

- If exactly one `spec/*` branch exists, select it; otherwise ask the user which to promote.
- If none exists, stop and report:
  > "No `spec/*` branch found. Next-version spec changes are accumulated on a `spec/*` branch.
  > See CLAUDE.md → 仕様バージョンの管理（ブランチ運用）."
- Derive the **label** from the branch name (`spec/sprint-12` → `sprint-12`).
- Verify the current branch is the intended target (normally `main`) and the working tree is clean
  (`git status --porcelain` is empty). If not, stop and ask the user to commit/stash first.

### Step 2: Drift guard (keep the spec branch current with main)

In-version corrections may have landed on `main` since the spec branch diverged. Promoting a
stale branch can drop or conflict with those corrections.

```bash
git rev-list --count spec/<label>..main   # commits on main not yet in the spec branch
```

- If the count is **0**, the branch is current — continue.
- If **> 0**, warn the user and recommend bringing the branch up to date **first**:
  ```bash
  git switch spec/<label>
  git merge main          # resolve any conflicts here, on the spec branch
  git switch main
  ```
  Do **not** auto-run this if conflicts are likely — recommend it and let the user resolve, then
  re-run `/promote-spec`. Only proceed past this step once the branch is current.

### Step 3: Diff & classify spec changes

```bash
git diff main..spec/<label> -- docs/
git diff --name-status main..spec/<label> -- docs/
```

Classify every change so the human sees exactly *what* moves (this is the concrete diff that a
bare version number cannot give):

| Class | How to detect | Meaning |
|-------|---------------|---------|
| **NEW** | New US file, or new `AC-NNN` / new `ac_ids:` entry not on `main` | New target AC. No existing impl to reconcile. |
| **CHANGED** | Existing US/design doc body or AC text modified | May invalidate already-built work. |
| **REMOVED** | US/AC deleted, or `ac_ids:` entry removed | Corresponding code/docs may need deprecation. |

Build a per-AC table. For CHANGED, capture *which* AC-IDs changed (diff the `## 受け入れ条件`
sections and `ac_ids:` frontmatter), not just which files changed.

### Step 4: Impact analysis (find stale impl + in-flight collisions)

For each **CHANGED** and **REMOVED** AC, determine whether it was already built or is being built:

```bash
# Match the AC only where a plan OWNS it as a deliverable (a checkbox line),
# not where it is merely mentioned in prose (e.g. a Decision Log entry).
# Replace <NNN> with the specific 3-digit AC-ID (e.g. 007) before running; anchoring to the
# checkbox line and the literal ID keeps AC-007 from matching AC-070. This is consistent with
# (and stricter than) how check-doc-invariants Step 5 extracts AC-IDs.
grep -rlE "^- \[[ x]\] AC-<NNN>:" exec-plans/completed/ 2>/dev/null   # already implemented?
grep -rlE "^- \[[ x]\] AC-<NNN>:" exec-plans/active/    2>/dev/null   # in flight?
# What code does its spec govern? (tracks: of the owning US/design doc)
#   read the `tracks:` globs from the changed doc, then list matching source files
```

Classify the impact of each changed/removed AC:

| Impact | Condition | Attention |
|--------|-----------|-----------|
| **Stale impl** | AC found in `exec-plans/completed/` (code exists for the old spec) | 🟠 High — must be reconciled |
| **In-flight collision** | AC found in `exec-plans/active/` (someone is mid-implementation) | 🔴 Critical — coordinate timing |
| **Target-only** | AC not yet implemented anywhere | 🔵 Low — just becomes the new target |

> **In-flight collisions are the case the team must decide carefully (point 4).** Recommend
> either (a) finishing and shipping the in-flight AC under the current spec first, then promoting,
> or (b) deferring promotion so it does not land on an AC under active implementation. Do not
> promote over an in-flight collision without the user's explicit acknowledgement.

> **Precedence when an AC is both in-flight and already completed:** treat it as an in-flight
> collision (the stricter case) — the active plan owner reconciles it; do **not** also create a
> separate reconcile plan for it in Step 7.

### Step 5: Present the promotion impact report → STOP

Output the report (format below) and then **halt for the human decision**:

> "This changes the development target. Per project rule, promotion is a human decision.
> Review the diff and impacts above. Proceed with promotion of `spec/<label>` into `main`?
> (yes / adjust the spec branch first / cancel)"

Do not proceed to Step 6 without an explicit "yes".

### Step 6: Execute promotion (only after explicit confirmation)

> A `spec-target-*` tag marks a **promotion — a change to the shared development target** — and is
> created here only. **Do NOT create one per developer, per feature, or per PR**: ordinary feature
> work merges to `main` against the current target through the normal PR flow and is never tagged by
> this skill. `<label>` is the shared version/promotion label, never a person's or a feature's name.
> The authoritative record is the promotion merge commit (always on `main`); the tag is a naming
> convenience, so old tags may be pruned later without losing recoverability.

1. **Ensure the outgoing target is tagged** so the pre-promotion spec stays recoverable. Each target
   carries its *own* label, so the outgoing target normally **already has** its tag
   (`spec-target-<prev>`) from the promotion that made it the target — there is nothing new to tag
   here. The **only** exception is the very first promotion, where no `spec-target-*` tag exists yet;
   only then, seed one for the current target *before* merging. Fetch tags first — `git tag --list`
   sees only local tags, so without a fetch a baseline could be seeded over a `spec-target-*` that
   already exists on the remote (causing a later push rejection):
   ```bash
   git fetch --tags origin                      # sync the local tag view with the shared remote first
   # first promotion only: <current> = current target label from CONTEXT.md, else "baseline"
   git tag --list 'spec-target-*' | grep -q . || git tag spec-target-<current>
   ```
   **Never overwrite an existing promotion tag.** Git *can* move a tag with `-f`, but the rule here
   is that a `spec-target-*` tag is permanent. If `spec-target-<label>` (the incoming label) already
   exists — a re-promotion or a reused label — **stop and ask the user for a disambiguated label**
   (e.g. `<label>-r2`) rather than forcing it.
2. **Merge with an explicit promotion commit** (with `--no-ff`, the merge's first parent stays the
   outgoing `main`):
   ```bash
   git merge --no-ff spec/<label> -m "promote spec: <label> becomes the current target"
   ```
3. **On conflict: stop.** Report the conflicting files and hand resolution to the human. Do not
   auto-resolve. Proceed to Step 7 **only after the merge commit actually exists on `main`**.
4. **Tag the new target snapshot** (the post-merge `main`):
   ```bash
   git tag spec-target-<label>
   ```
   Branch `spec/<label>` and tag `spec-target-<label>` are distinct refs (different names); keeping
   `<label>` unique per promotion avoids confusion. Any version-to-version spec diff is then
   `git diff spec-target-<prev>..spec-target-<label> -- docs/`, where `<prev>` is the most recent
   prior tag: `git tag --list 'spec-target-*' --sort=-creatordate | sed -n 2p`. On the **first**
   promotion no prior tag exists, so `<prev>` is empty — fall back to the merge commit's first
   parent `spec-target-<label>^1` (the pre-promotion `main`), or the baseline tag seeded in 6.1.
   In the common case `<prev>` and the seeded `<current>` (6.1) name the same outgoing target.
5. **Publish to the shared remote.** Tags created in 6.1 and 6.4 (the numbered items above in this
   Step 6) live only in the local clone until pushed — a tag no one else has cannot restore the old
   version for the team, so "recoverable" only holds once these are on the remote:
   ```bash
   git push origin main                         # the promotion merge
   git push origin spec-target-<label>          # the new target snapshot tag
   git push origin spec-target-<current>        # the seeded outgoing/baseline tag, if newly created in 6.1
   ```

### Step 7: Post-promotion bookkeeping

> Run this step **only after the merge commit exists on `main`** (in the conflict case, after the
> human has completed the merge). The reconcile plan references ACs from the *new* spec, so creating
> it while `main` still holds the old spec would put `exec-plans/active/` out of sync with the
> current target.
>
> If there are **no CHANGED/REMOVED ACs** (a purely additive promotion), skip the reconcile plan
> entirely — only the NEW-AC `/create-exec-plan` suggestions below apply.

1. **Create a reconciliation exec-plan** for every **stale impl** AC, so implementation can catch
   up to the new spec. Re-open the *same* AC-IDs — for **CHANGED** ACs the ID still traces to its
   US `ac_ids:`, so DOC-INV-004 stays satisfied (this does **not** hold for REMOVED ACs; see below):

   `exec-plans/active/YYYY-MM-reconcile-<label>.md`
   ```markdown
   ---
   status: active
   created: YYYY-MM-DD
   completed:
   ---

   # reconcile-<label>

   ## Goal & Scope
   Reconcile implementation to the spec promoted from spec/<label>.
   These ACs were implemented under the previous spec and must be brought in line with the new target.

   ## Acceptance Criteria
   - [ ] AC-003: <new AC text> — was implemented under old spec; update impl to match
   - [ ] AC-007: <new AC text> — ...

   ## Task Breakdown
   - [ ] Review `git diff spec-target-<prev>..spec-target-<label> -- docs/` for each AC
   - [ ] Update implementation and tests for each stale AC
   - [ ] Run /check-doc-freshness and /check-invariants

   ## Progress Log

   ### YYYY-MM-DD
   - Plan created by /promote-spec (spec promotion <label>)

   ## Decision Log
   - Promotion <label>: AC-003, AC-007 marked stale (spec changed after implementation).
   ```

   - **NEW** ACs are *not* auto-planned — they need scoping. Suggest the user run
     `/create-exec-plan` for them.
   - **REMOVED** ACs: the AC-ID no longer exists in any US `ac_ids:`, so any `active/` plan still
     carrying it now **violates DOC-INV-004** and `spec-gate.py` would still accept the orphaned ID.
     Close or annotate that AC line in the active plan (mark it removed, with a Decision Log note)
     so traceability is not left broken, and suggest deprecating the corresponding code/docs
     (set the owning doc `status: deprecated`). Do not delete code automatically.

2. **Record the promotion** in the reconcile plan's Decision Log (and/or a project Promotion Log):
   version label, date, summary of NEW/CHANGED/REMOVED, stale ACs, how in-flight collisions were
   handled, and the routing rationale.

3. **Update `docs/06_ai_context/CONTEXT.md`** — set the current target version/label and the new
   priority tasks (the reconcile plan + any new-AC plans).

4. **Retire the spec branch** (optional, recommended): it is preserved in history and by the tag.
   ```bash
   git branch -d spec/<label>
   ```
   Offer this; do not force it.

### Step 8: Final report

Output the result report (below).

---

## Result report format

```
=== Spec promotion impact report ===

Spec branch : spec/<label>   →   target: main
Drift guard : ✅ up to date  /  ⚠️ main is N commits ahead (bring branch current first)

── Spec changes ──────────────────────────────
NEW     : {count}   (US-012, AC-015, AC-016, ...)
CHANGED : {count}   (AC-003, AC-007, ...)
REMOVED : {count}   (AC-009, ...)

── Impact on existing work ───────────────────
🔴 In-flight collisions : {count}
  - AC-007  (active: exec-plans/active/2026-06-search.md) — coordinate timing before promoting
🟠 Stale impl           : {count}
  - AC-003  (completed: 2026-05-login.md; tracks src/auth/**) — needs reconciliation
🔵 Target-only          : {count}

── Decision required ─────────────────────────
Promotion changes the development target — confirm to proceed (yes / adjust / cancel).

── After promotion (filled in once executed) ─
Outgoing version preserved : spec-target-<prev>  (baseline seeded if first promotion)
New target snapshot tagged  : spec-target-<label>
Reconcile plan created      : exec-plans/active/YYYY-MM-reconcile-<label>.md (AC-003, ...)
New-AC plans suggested      : /create-exec-plan for AC-015, AC-016
CONTEXT.md                  : current target updated to <label>
Spec branch                 : retired (or kept)
Next action                 : /start-feature on the reconcile plan; /create-exec-plan for NEW ACs
```

---

## Completion criteria

- [ ] The target `spec/*` branch was identified and the working tree was clean
- [ ] Drift guard checked (branch current with `main`, or user brought it current)
- [ ] Spec diff classified into NEW / CHANGED / REMOVED at the AC level
- [ ] Impact analysed against `completed/` and `active/` plans (stale impl + in-flight collisions surfaced)
- [ ] Impact report presented and **explicit human confirmation** obtained before merging
- [ ] Outgoing version recoverable and new target snapshot tagged (`spec-target-<label>`)
- [ ] Reconcile exec-plan created for stale-impl ACs; NEW ACs flagged for `/create-exec-plan`
- [ ] Promotion recorded in the Decision Log and `docs/06_ai_context/CONTEXT.md` updated
