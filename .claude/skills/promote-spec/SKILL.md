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
③ Diff & classify spec changes (NEW / CHANGED / REMOVED), and list the ADR candidates
④ Impact analysis against completed & active exec-plans (find stale impl + in-flight collisions)
⑤ Present the promotion impact report → STOP for human decision
⑥ Execute promotion after explicit confirmation (tag outgoing version, merge --no-ff)
⑦ Post-promotion bookkeeping (reconcile exec-plan, ADR drafts, Decision Log, CONTEXT.md)
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
- **E2E scenarios moved on `main`.** If `main` moved scenarios out of a spec's old-layout
  `## E2E シナリオ` section into `docs/01-02_e2e/` (DOC-INV-006 in `check-doc-invariants`) while the
  spec branch edited or added scenarios in that section, the merge conflicts there. Resolve it on
  the spec branch by applying the branch's change to the moved file (or, for a new scenario, a new
  file `docs/01-02_e2e/E2E-NNN_{slug}.md`) — never by restoring the section, which would bring the
  old layout back on promotion. The merge does not always conflict: a scenario the branch appended
  in a hunk that does not overlap the removed section merges cleanly and lands back in the old
  layout. So after the merge, check `git diff main...spec/<label> -- docs/02_spec/` for added
  `### E2E-` headings and move each into its own file the same way.
- **ADR numbers taken on both sides.** `docs/00_project/decisions.md` is appended to on `main` and on
  the spec branch alike, so the same `ADR-NNN` can be drafted on both; the merge usually conflicts at
  the end of the file, and may not. Resolve it on the spec branch by renumbering the **branch's** ADR to
  the next number free on `main`, and its citations on the branch with it — it has not taken effect
  yet, while `main`'s may already be cited (`../init-project/adr-format.md`「The format」). After the
  merge, check `grep -oE '^## ADR-[0-9]+' docs/00_project/decisions.md | sort | uniq -d` on the branch
  for a duplicate the merge did not flag.
- **Lines dropped on `main` for this version.** A gap or a contradiction resolved as next-version
  may have been handled by removing a line on `main` — a scenario step (②), or the broader side of a
  contradiction — on the understanding that this version brings it back
  (`../create-spec/e2e-interaction.md`「When `main` drops text the next version should bring back,
  record it」). Merging `main` into `spec/<label>` removes it from the branch too, silently, wherever
  the branch had not touched that line. Both checks below run **every time**, after the branch is
  current — whether this run merged `main` or an earlier merge did (a count of 0 above does not mean
  a line survived):
  1. **The deletion review.** List the lines `main` has removed from `docs/` since `spec/<label>` was
     branched from it, so the human can spot one the next version still wants — including one no plan
     recorded (a gap resolved from an advisory finding has no Decision Log to hold a marker). The base
     is the fork point — the first parent of the branch's first commit — which also covers a version
     branch opened before the previous promotion:
     ```bash
     git log --reverse --topo-order --format=%H main..spec/<label> | head -1   # → <first>; base = <first>^1
     git -c core.quotePath=false diff <first>^1 main -- docs/ | grep -E "^(\+\+\+ |-)" | grep -vE "^--- (\"?a/|/dev/null)" || true
     ```
     The greps keep each file's `+++ b/<file>` line, so every removed line shows which file it came
     from, and every removed line itself — a removed Markdown bullet shows in a diff as `-- …`, so a
     filter on `^-[^-]` would drop exactly the scenario steps and AC bullets this review is for. They
     drop only the `--- a/<file>` headers. `core.quotePath=false` keeps a non-ASCII path readable.
     The list includes ordinary in-version deletions; the human looks for the ones the next version
     meant to keep, and checks whether each is still on `spec/<label>`. Show it, grouped by file, in
     the Step 5 report.
  2. **The markers.** Check each marker for this label in active **and** completed plans:
     ```bash
     grep -rnE "^- E2E 次版戻し: spec/<label>( |$)" exec-plans/active/ exec-plans/completed/ 2>/dev/null || true
     grep -rnE "^- E2E 次版戻し 取消: spec/<label>( |$)" exec-plans/active/ exec-plans/completed/ 2>/dev/null || true
     git show spec/<label>:<file named in the marker> | grep -Fx -- "<the removed line, verbatim>" || echo "missing on spec/<label>"
     ```
     `-x` matches the whole line, so a reworded line that merely contains the old text does not pass
     as present. A file the branch has since moved (for example in the layout migration above) also
     reports "missing", and so can a whitespace difference — trailing spaces, or CRLF stored in the
     repository. Each errs toward stopping; the human looks before re-adding anything.
     A marker with a matching `取消` bullet is withdrawn and skipped. For the rest, a line missing on
     the branch **stops the promotion here**, like an out-of-date branch: a human re-adds it on
     `spec/<label>` (or withdraws the marker), then re-runs `/promote-spec` — Steps 3–4 must see the
     branch as it will be promoted. Which line, and where, is a spec decision. Show every marker and
     its result in the Step 5 report. Only a bullet that begins this way is a marker; `( |$)` keeps
     `sprint-1` from matching `sprint-12`.

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

**Classify the E2E scenarios too, by `E2E-NNN`.** A promotion can change a scenario's 前提, steps,
完了条件 or `満たす AC` while leaving every AC line alone, and a per-AC table then shows nothing —
yet every plan that froze the scenario has had its target moved
(`../create-spec/e2e-interaction.md`「The freeze is per plan」). Build a second table:

| Class | How to detect | Meaning |
|-------|---------------|---------|
| **NEW** | A new `docs/01-02_e2e/E2E-NNN_*.md` (or a new `### E2E-NNN:` block in an old-layout section) | A new through-flow. No plan has frozen it |
| **CHANGED** | The scenario's 前提, steps, 完了条件 or `満たす AC` differ (the frontmatter alone, or a move with unchanged text, is not a change) | Moves the target of every plan that froze it |
| **REMOVED** | The scenario file (or block) is gone | A plan that froze it now names nothing |

```bash
git diff --name-status main..spec/<label> -- docs/01-02_e2e/
git diff main..spec/<label> -- docs/01-02_e2e/ docs/02_spec/   # old layout: ### E2E-NNN blocks
```

**List the ADR candidates.** A CHANGED or REMOVED item reverses or narrows something already decided —
the decision a later reader will most want the reasons for, and the one most likely to be re-proposed
if they are lost ([`../init-project/adr-format.md`](../init-project/adr-format.md)「When a decision is
an ADR candidate」). Collect the ADRs the branch itself adds:

```bash
git diff main..spec/<label> -- docs/00_project/decisions.md | grep -E '^\+' || true   # the added ADRs, headings and bodies
```

Every CHANGED / REMOVED AC and every CHANGED / REMOVED `E2E-NNN` whose ID no added ADR names (an ADR
names the IDs it changed in its 結果 — `adr-format.md`「The format」) is an **ADR candidate**; one that
is named is covered. Matching by ID is a starting point, not a
verdict — show the added ADRs, and any research note the branch adds under `docs/00_project/research/`,
beside the list so the human can mark an item covered that the ID match missed (a research note that
names the rejected option also ends a candidacy — `adr-format.md`, condition 2). NEW items are not candidates here: they are scoped through `/create-exec-plan` after the
promotion, and their decisions were drafted with the spec (`create-spec` Step 2c).

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

**Then do the same for each CHANGED and REMOVED scenario**, keyed on `E2E-NNN` — the collision the
per-AC check cannot see. Only a hit inside a plan's `## Sources` row counts — that is what freezes a
scenario (`../create-spec/e2e-interaction.md`「The freeze point」). The same ID in a Decision Log is
history, and an `[E2E]` AC line in a plan with no `## Sources` table does not freeze it either (`gc`
counts such a line only as having taken the scenario up):

```bash
# Replace <NNN> with the 3-digit scenario ID before running.
grep -rn "E2E-<NNN>" exec-plans/active/    2>/dev/null || true   # frozen by an in-flight plan?
grep -rn "E2E-<NNN>" exec-plans/completed/ 2>/dev/null || true   # frozen by a completed plan?
```

| Impact | Condition | Attention |
|--------|-----------|-----------|
| **In-flight E2E collision** | A CHANGED or REMOVED scenario that an active plan's `## Sources` row names — its `[E2E]` test may already be frozen red against the old text | 🔴 Critical — same handling as an in-flight AC collision: finish under the current scenario first, or defer the promotion; never promote over it without the user's acknowledgement. A REMOVED one is also a row this promotion breaks (below) |
| **Stale E2E** | A **CHANGED** scenario that a completed plan's `## Sources` row names — the through-flow it verified is no longer the target | 🟠 High — re-opened in the reconcile plan (Step 7) |
| **Removed E2E** | A **REMOVED** scenario that a completed plan's `## Sources` row names — the flow it verified is no longer wanted | 🟡 Medium — nothing to re-open; suggest retiring its `[E2E]` test (a human's call, like deprecating code for a REMOVED AC) and note it in the promotion record (Step 7). It does not by itself call for a reconcile plan |
| **Target-only** | No plan names it | 🔵 Low |

A scenario can collide while none of its ACs does; report it even then — that is the case this check
exists for. A **REMOVED** scenario that an active plan's row names is also a row this promotion
breaks: list it with the moved sources below, so the human repoints the row (to a successor
scenario) or writes `n/a（理由）` in Step 6, after the merge and before the push. When the same plan
collides on both an AC and the scenario, report both lines; the precedence rule below (in-flight
wins over completed) applies to scenarios the same way.

> **Sources that move are a collision this table does not show.** The analysis above is per AC, so
> a promotion that keeps every AC but moves a spec file or retitles a section raises no in-flight
> collision — and still breaks the `## Sources` rows of active plans that name it. List them here
> (`grep -rn "<moved path or old section name>" exec-plans/active/ 2>/dev/null || true`), show them
> in the Step 5 report, and have the human repoint them **in Step 6, right after the merge and before
> anything is pushed** — not before the promotion (the new path does not exist on `main` yet, so a
> repointed row would fail there) and not after the push (the shared `main` would already be broken).
> Repairing a row is a human's call (`../create-exec-plan/ac-sources.md`「When a source cannot be
> opened」). A moved or renamed file left behind is a DOC-INV-012 ❌, and the promotion is not
> stopped by it — it never passes `pre-pr`. After the push it blocks the PR of each plan whose row it
> is, shows up in every other PR's `pre-pr` ③ as another plan's row (not blocking), and stays an ❌
> in `gc` until repointed (`../check-doc-invariants/SKILL.md`「Which ❌ blocks which run」); a
> retitled section is a ⚠️.

> **Plans deferred until this promotion.** An active plan may be waiting for exactly this `<label>`:
> a requirements gap in a scenario it froze was judged next-version, and the human deferred the plan
> rather than drop the step on `main` (`../create-spec/e2e-interaction.md`「Deferring a plan, and
> lifting it」). List them
> (`grep -rnE "^- deferred: spec/<label>( |$)" exec-plans/active/ 2>/dev/null || true` — only a
> bullet that begins this way is a deferral, and `( |$)` keeps `sprint-1` from matching `sprint-12`;
> skip any followed by a bullet beginning `- deferred 解除:`) and show them in the Step 5 report. Lifting
> a deferral is the human's: after the merge in Step 6, each owner checks that the promoted
> documents now state the outcome, then records `deferred 解除: YYYY-MM-DD（理由）` in that plan's
> Decision Log. This skill does not lift it — without this list, though, nothing reads the deferral
> once its reason is gone, and the plan stays parked.
>
> **Such a plan can also show up above as a 🔴 in-flight collision** — an AC collision when the gap
> it waits on is promoted (①) into an AC section the plan itself owns, or an E2E collision when the
> promotion edits the scenario it froze (① written as a new AC adds it to `満たす AC`, which edits
> the scenario). For a plan deferred until this `<label>`, either collision is the **awaited**
> change, not one to coordinate around: the advice above (finish first, or defer the promotion) is
> exactly wrong for it, since the plan cannot proceed until the promotion lands. Report the AC or the
> scenario under the deferred list instead of as 🔴, and say why.

> **Precedence when an AC is both in-flight and already completed:** treat it as an in-flight
> collision (the stricter case) — the active plan owner reconciles it; do **not** also create a
> separate reconcile plan for it in Step 7.

### Step 5: Present the promotion impact report → STOP

Output the report (format below) and then **halt for the human decision**:

> "This changes the development target. Per project rule, promotion is a human decision.
> Review the diff and impacts above. Proceed with promotion of `spec/<label>` into `main`?
> (yes / adjust the spec branch first / cancel)"

Do not proceed to Step 6 without an explicit "yes".

**Ask about the ADR candidates in the same reply** (per `adr-format.md`「The procedure at a call
site」): for each, record it as an ADR — yes or no — and, for a yes, where:

| Where | When to choose it |
|-------|-------------------|
| **On `spec/<label>`, before the merge** | Choose "adjust the spec branch first": the decision and its reasons are promoted together and tagged in `spec-target-<label>`. Draft it there now — `git switch spec/<label>`, draft per `adr-format.md`「The procedure at a call site」 step 3, commit, `git switch main` — then the human re-runs `/promote-spec` |
| **On `main`, in Step 7** | The promotion goes ahead now; the ADR is drafted after the merge, with the reconcile plan |

A no — or no answer about the candidates — does not hold the promotion: the decision this step waits
for is the merge, not the ADRs. A no is not written anywhere, so a re-run (after adjusting the branch
for any other reason) lists the same candidate again; answer it again. That costs one line of a report
the human reads anyway, and keeps the record of a no from becoming a file nobody maintains.

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

   **Then, if Step 4 listed `## Sources` rows this promotion breaks**, stop again before tagging:
   the human repoints those rows now, as a commit on `main` on top of the merge. This is the only
   point where it works — the new paths exist, and nothing has been pushed. Do not repoint them
   yourself (`../create-exec-plan/ac-sources.md`「When a source cannot be opened」).

   **If Step 4 listed plans deferred until `spec/<label>`**, remind their owners now that the
   promotion the deferral waits for is merged: each checks that the promoted documents state the
   outcome and records `deferred 解除: YYYY-MM-DD（理由）` in the plan's Decision Log. Lifting is
   theirs; this skill neither writes the line nor blocks on it.
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
> If there are **no CHANGED/REMOVED ACs and no stale E2E** (a purely additive promotion), skip the
> reconcile plan entirely — only the NEW-AC `/create-exec-plan` suggestions below apply.

1. **Create a reconciliation exec-plan** for every **stale impl** AC and every **stale E2E**, so
   implementation can catch up to the new spec. Re-open the *same* AC-IDs — for **CHANGED** ACs the
   ID still traces to its US `ac_ids:`, so DOC-INV-004 stays satisfied (this does **not** hold for
   REMOVED ACs; see below):

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
   - [ ] AC-NNN: [E2E] E2E-NNN のとおり、<前提>から<完了条件>まで通しで実行できる
         （再オープンした AC を含む通しフローが、新しい spec のもとで成立する）

   > このプランは、機能 AC がすべて `- [x]` でも `[E2E]` の AC が緑でなければ完了ではない。

   ## Sources

   | AC | US（検証可能な bullet） | spec（振る舞いの節） |
   |----|------------------------|---------------------|
   | AC-003 | `docs/01_requirements/user_stories/US-XXX_<name>.md` § AC-003 | `docs/02_spec/<file>.md` §「<新 spec の該当節>」 |
   | AC-007 | 同上 § AC-007 | 同上 §「<新 spec の該当節>」 |
   | AC-NNN [E2E] | 同上 § ゴール像／主要ユーザージャーニー | `docs/01-02_e2e/E2E-NNN_<slug>.md` § E2E-NNN |

   ## Task Breakdown
   - [ ] Review `git diff spec-target-<prev>..spec-target-<label> -- docs/` for each AC
   - [ ] For each stale AC: update its test **first** to the new expectation and observe it red
         (red-first / INV-T02), then update the implementation until it is green
   - [ ] Run /check-doc-freshness and /check-invariants

   ## Progress Log

   ### YYYY-MM-DD
   - Plan created by /promote-spec (spec promotion <label>)

   ## Decision Log
   - Promotion <label>: AC-003, AC-007 marked stale (spec changed after implementation).
   - AC readiness / red-first: このプランは `create-exec-plan` の起票インタビューを経ていない。
     readiness は `/start-feature`（Step 1b）または `/run-exec-plan`（Step 0b）で検査される。
   ```

   **The `## Sources` table must point at the *new* spec** (`../create-exec-plan/ac-sources.md`).
   A reconcile plan exists because the spec moved; if its sources still named the pre-promotion
   sections, the implementer would be steered by the very text the promotion replaced, and
   `run-exec-plan`'s Step 3a re-anchor would confirm the old behavior as correct. Fill each row from
   the post-merge sections the diff in Step 4 flagged as CHANGED — in `docs/02_spec/**`, and for the
   `[E2E]` row the post-merge scenario file in `docs/01-02_e2e/` (in a project not yet migrated, the
   spec's `§ E2E-NNN` instead) — and use `git diff spec-target-<prev>..spec-target-<label> -- docs/`
   to locate them. If a re-opened AC's
   spec section cannot be identified, write `n/a（理由）` rather than guessing; do not leave a cell
   blank.

   **The `[E2E]` AC is required here** (`create-exec-plan` → "When it is required": a reconcile plan
   re-opening AC-IDs carries one). A reconcile plan that only fixes fragments can go all-green while
   the flow the new spec describes does not work — the exact failure the criterion exists for.

   - **Which ID to use.** Do not invent a new ID series or a number outside the spec: use the AC-ID
     that the new scenario (`E2E-NNN`) traces to — normally one of the re-opened IDs — so DOC-INV-004
     traceability still holds. If no re-opened AC owns the through-flow, do **not** fabricate one:
     tell the user to add it via `/create-exec-plan`, where a human decides what the flow is.
   - **Red-first for a re-opened AC** (`run-tests/red-first.md`): the spec *changed*, so the old
     test states the old expectation. Rewrite the expectation from the new AC text, observe it red,
     record it — the "preservation AC" exemption does **not** apply here; it covers ACs whose
     behavior is unchanged. Grounding the test change in the promoted spec is what keeps this from
     being an INV-T01 violation, so name the promotion label and AC-ID in the Decision Log entry.

   - **Stale E2E** (Step 4): for each completed plan whose frozen scenario CHANGED, re-open its
     `[E2E]` AC in this reconcile plan, with its `## Sources` row pointing at the post-promotion
     scenario file. The ID follows「Which ID to use」 above — normally the completed plan's own
     `[E2E]` AC-ID, which already traces to a US AC; never a new one. It is the reconcile plan's
     `[E2E]` AC when the scenario covers the re-opened functional ACs; a re-opened scenario whose ACs
     did not change still gets its own `[E2E]` line — the flow moved even though no fragment did.
     Name the promotion label and the scenario in the Decision Log entry, as for a stale AC.
   - **In-flight E2E collision promoted with the user's acknowledgement** (Step 4): the active plan's
     frozen scenario has now moved. **Remind its owner** to record it in that plan's Decision Log —
     `E2E-NNN は <label> の昇格で変更 — {凍結済み [E2E] テストへの影響と人の判断}` — in a follow-up
     commit (Step 6.5 has already pushed the promotion). The judgement half is the owner's; this skill
     does not write it, as it does not write `deferred 解除:`. This is the record
     `../create-spec/e2e-interaction.md`「The freeze is per plan」 requires for a hit in `active/`,
     and what keeps `gc`'s E2E backstop from raising it a week later. Remind the owner of a plan
     deferred until this `<label>` whose scenario the promotion edited (the awaited change) the same
     way. What the change means for the frozen `[E2E]` test is the owner's call — a changed
     expectation is stop condition (c) territory, not something this skill decides.
   - **REMOVED scenario**: the active plans whose rows name it were repaired by the human in Step 6
     (listed in Step 4 with the rows this promotion breaks). A scenario removed under a completed plan
     is a **Removed E2E** (Step 4): note it, and the suggestion to retire its `[E2E]` test, in the
     promotion record (item 2 below) — it re-opens nothing. Remind each active plan's owner to record
     the removal in its Decision Log (`E2E-NNN は <label> の昇格で削除 — 行は {後継シナリオ | n/a（理由）}
     に`), in the same follow-up commit. Do not repoint or blank a row yourself
     (`../create-exec-plan/ac-sources.md`「When a source cannot be opened」).

   - **NEW** ACs are *not* auto-planned — they need scoping. Suggest the user run
     `/create-exec-plan` for them.
   - **REMOVED** ACs: the AC-ID no longer exists in any US `ac_ids:`, so any `active/` plan still
     carrying it now **violates DOC-INV-004** and `spec-gate.py` would still accept the orphaned ID.
     Close or annotate that AC line in the active plan (mark it removed, with a Decision Log note)
     so traceability is not left broken, and suggest deprecating the corresponding code/docs
     (set the owning doc `status: deprecated`). Do not delete code automatically.

1b. **Draft the ADRs the human said yes to "on `main`"** (Step 5) in `docs/00_project/decisions.md`,
   in the format of [`../init-project/adr-format.md`](../init-project/adr-format.md), taking 検討した代替案と却下理由
   — normally the pre-promotion behavior, and why it was replaced — from the human, never inventing
   it. Commit them with the reconcile plan, and have the human review that commit before it is pushed
   — on `main`, that review is the ADR's approval (`adr-format.md`「The format」, 状態). In prose, an ADR names the promoted sections and the label
   (`spec-target-<label>`); it does not link them (layer 0). This step runs even for a purely additive
   promotion that skips the reconcile plan, if any yes was given.

2. **Record the promotion** in the reconcile plan's Decision Log (and/or a project Promotion Log):
   version label, date, summary of NEW/CHANGED/REMOVED, stale ACs, how in-flight collisions were
   handled, and the routing rationale.

3. **Update `docs/07_ai_context/CONTEXT.md`** — set the current target version/label and the new
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
次版戻し    : {count} — docs/01-02_e2e/E2E-001_tag-and-filter.md「- 完了条件: 一覧を CSV に書き出せる」
              (2026-06-export.md) ✅ present on spec/<label>  /  ❌ missing — stopped; re-add on the branch
              (or withdraw: 次版戻し 取消) and re-run  /  ➖ withdrawn
削除の確認  : {n} lines main removed from docs/ since the fork point <first>^1 — listed by file below, reviewed by the human (Step 2)
  - docs/01-02_e2e/E2E-001_tag-and-filter.md: "- 完了条件: 一覧を CSV に書き出せる" — ✅ still on spec/<label> / ❌ gone

── Spec changes ──────────────────────────────
NEW     : {count}   (US-012, AC-015, AC-016, ...)
CHANGED : {count}   (AC-003, AC-007, ...)
REMOVED : {count}   (AC-009, ...)
ADR 候補 : {count}   (AC-003 CHANGED, E2E-002 CHANGED, AC-009 REMOVED — no ADR added on the branch names them)
          added on the branch: ADR-014 「…」 (covers AC-007)  /  "none"

── Impact on existing work ───────────────────
🔴 In-flight collisions : {count}
  - AC-007  (active: exec-plans/active/2026-06-search.md) — coordinate timing before promoting
🟠 Stale impl           : {count}
  - AC-003  (completed: 2026-05-login.md; tracks src/auth/**) — needs reconciliation
🔵 Target-only          : {count}
🔴 In-flight E2E collisions : {count}
  - E2E-001 CHANGED (active: exec-plans/active/2026-06-search.md, [E2E] AC-005 frozen) — no AC line changed; coordinate before promoting
  - E2E-003 REMOVED (active: exec-plans/active/2026-06-export.md) — also listed under Sources rows this promotion breaks
🟠 Stale E2E            : {count}
  - E2E-002 CHANGED (completed: 2026-05-login.md, [E2E] AC-004) — re-opened in the reconcile plan
🟡 Removed E2E          : {count}
  - E2E-006 REMOVED (completed: 2026-04-import.md, [E2E] AC-002) — suggest retiring its [E2E] test
⚠️ Sources rows this promotion breaks : {count}
  - exec-plans/active/2026-06-search.md:19 → docs/02_spec/app_spec.md (moved) — the human repoints it in Step 6, before pushing
  - exec-plans/active/2026-06-export.md:21 → docs/01-02_e2e/E2E-003_export.md (removed) — successor scenario or n/a（理由）, in Step 6
⏸ Plans deferred until spec/<label> : {count}
  - exec-plans/active/2026-06-export.md — 「CSV に書き出せる」(E2E-001) — the owner lifts it after the merge (deferred 解除:)

── Decision required ─────────────────────────
Promotion changes the development target — confirm to proceed (yes / adjust / cancel).

── After promotion (filled in once executed) ─
Outgoing version preserved : spec-target-<prev>  (baseline seeded if first promotion)
New target snapshot tagged  : spec-target-<label>
Reconcile plan created      : exec-plans/active/YYYY-MM-reconcile-<label>.md (AC-003, ... + [E2E] AC-NNN)
ADR 候補                    : {n} 件 — ADR-NNN 追記 {n}（branch {n} / main {n}）/ 見送り {n}; or "none"
New-AC plans suggested      : /create-exec-plan for AC-015, AC-016
CONTEXT.md                  : current target updated to <label>
Deferrals to lift           : exec-plans/active/2026-06-export.md (deferred until spec/<label>) — owner records deferred 解除:
Spec branch                 : retired (or kept)
Next action                 : /start-feature on the reconcile plan; /create-exec-plan for NEW ACs
```

---

## Completion criteria

- [ ] The target `spec/*` branch was identified and the working tree was clean
- [ ] Drift guard checked (branch current with `main`, or user brought it current)
- [ ] With the branch current, the lines `main` removed from `docs/` since the branch's fork point
      were shown to the human, by file; and every `- E2E 次版戻し: spec/<label>` marker in active and completed plans not
      withdrawn by a `取消` bullet was checked against `spec/<label>` — a missing line stopped the run
      until a human re-added it (or withdrew the marker)
- [ ] Spec diff classified into NEW / CHANGED / REMOVED at the AC level
- [ ] Impact analysed against `completed/` and `active/` plans (stale impl + in-flight collisions surfaced)
- [ ] E2E scenarios classified by `E2E-NNN` (NEW / CHANGED / REMOVED) and matched against the plans'
      `## Sources` rows — in-flight E2E collisions and stale E2E reported even where no AC line changed;
      a stale E2E's `[E2E]` AC re-opened in the reconcile plan, and a removed scenario's rows left to the human
- [ ] Active plans whose `## Sources` names a file or section this promotion moves were listed, and their owners asked to repoint the rows
- [ ] Active plans deferred until `spec/<label>` were listed in the report, and their owners asked to
      decide whether to lift the deferral after the merge
- [ ] ADR candidates (CHANGED / REMOVED ACs and scenarios that no ADR added on the branch names) were
      listed in the report and asked about; an ADR was drafted for each yes — on the branch before the
      merge, or on `main` in Step 7 — and a no did not hold the promotion
- [ ] Impact report presented and **explicit human confirmation** obtained before merging
- [ ] Outgoing version recoverable and new target snapshot tagged (`spec-target-<label>`)
- [ ] Reconcile exec-plan created for stale-impl ACs; NEW ACs flagged for `/create-exec-plan`
- [ ] The reconcile plan carries an `[E2E]` AC (using an existing AC-ID from the new spec, not an
      invented one) and states that it is not complete while that criterion is unchecked
- [ ] The reconcile plan carries a `## Sources` table with a row per re-opened AC, pointing at the
      **post-promotion** spec sections (or an explicit `n/a（理由）`) — never the replaced text
- [ ] Promotion recorded in the Decision Log and `docs/07_ai_context/CONTEXT.md` updated
