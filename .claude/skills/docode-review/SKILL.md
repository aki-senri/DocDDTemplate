---
name: docode-review
description: |
  Launches an independent agent (with no implementation context) to review changed code.
  The agent reviews the diff against acceptance criteria (if available) — including the US bullets
  and spec sections the plan's ## Sources names, not only the one-line AC — and general code
  quality, providing an objective perspective separate from the implementing agent. It also judges whether
  each test expresses its AC rather than mirroring the implementation — the one check the agent
  that wrote both sides cannot perform on itself.
  Mandatory when `run-exec-plan` finishes a plan autonomously (its Step 4a calls this skill
  before handing off to `pre-pr`, and halts on a ❌ verdict) — optional, as before, on the
  manual `start-feature` path.
# disable-model-invocation is intentionally false: this skill's core function is to spawn
# an independent subagent via the Agent tool, which requires model invocation.
# All other skills set this to true because they only issue instructions to the current agent.
disable-model-invocation: false
---

# Skill: Independent Agent Code Review

> **When to run**: After implementation is complete, before running `/pre-pr`.
> **Mandatory** when the plan was completed autonomously by `/run-exec-plan` — its Step 4a calls
> this skill itself, once every AC is `- [x]`, and halts (stop condition (f)) on a ❌ verdict rather
> than handing off. **Optional**, as before, when a human implemented the plan via `/start-feature`
> — that path always had a human look at the diff before the PR, which is the gap this skill exists
> to fill only when nobody did.
>
> **Purpose**: Get an objective review from an agent that has no knowledge of the implementation
> decisions made during coding. This avoids confirmation bias from the implementing agent — the
> risk is structural (not a matter of diligence) when the same agent authored the code, the tests,
> and every green check along the way, which is exactly what a `run-exec-plan` completion is.
>
> **Prerequisites** (manual/human-invoked path):
> - The working tree is clean (all changes are committed — run `git status` to verify)
> - At least one commit exists on the current branch
> - The branch has diverged from `main` (there are changes to review)
>
> **On the `run-exec-plan` Step 4a path, these do not apply as written.** The autonomous loop reaches
> full completion before anything is necessarily committed — DocDD only commits when the user asks
> (see CLAUDE.md's git safety rules) — so Step 4a routinely calls this skill against an uncommitted,
> possibly fully-dirty tree. That is expected here, not a precondition violation: follow Step 1's
> "working tree is not clean" branch below (include `git diff --cached` and `git diff` in the review
> context) rather than asking the user to commit first.

---

## Background: the `Agent` tool

The `Agent` tool is a built-in Claude Code capability that spawns a **fresh subagent** in an
isolated context. The subagent:

- has **no memory** of the current session or implementation decisions
- receives only what you explicitly pass in its prompt
- cannot read the conversation history of the parent agent

This is what makes the review "independent": the reviewer sees only the diff and the spec,
not the rationale or constraints the implementing agent accumulated during coding.

**How to invoke**: Claude Code exposes the `Agent` tool automatically when running skills.
No extra configuration is required. When this skill instructs you to "use the `Agent` tool",
construct the prompt described in Step 3 and pass it as the `prompt` parameter.

---

## What this skill does

Spawns a **new, independent agent** via the `Agent` tool and passes it:

1. The full diff of committed changes (`git diff main...HEAD`) plus any uncommitted changes
2. The active exec-plan (AC definitions), if one exists
3. A structured review prompt

The independent agent has no memory of the current session and reviews the code from scratch.

---

## Steps

### Step 1: Collect context

Run the following commands to gather the review context.

```bash
# Verify working tree is clean
git status

# Changed files list (committed)
git diff --name-only main...HEAD

# Full diff (committed changes)
git diff main...HEAD

# Staged but not yet committed (include if non-empty)
git diff --cached

# Unstaged changes (include if non-empty)
git diff

# Active exec-plan contents (if any exist)
ls exec-plans/active/ && cat exec-plans/active/*.md 2>/dev/null || echo "No active exec-plan"
```

Then read the plan's `## Sources` table and **open every US / spec section it names**. The subagent
inherits no session context, so a path it cannot read is a path it will ignore: paste the relevant
sections into the prompt rather than referencing them. If a plan has no `## Sources` table, or every
row is `n/a`, note that in the prompt so the reviewer knows the AC lines are all there is.

**If the diff changes a documented process** — a skill definition, `CLAUDE.md`, a hook, or any rule
other rules consume — also collect the **referrers**, for review point 1d's dependency-backflow lap:

```bash
# Start from the changed single source's own call-site table — it is the curated list.
# Then widen by grep on BOTH the file name and the rule/step IDs it defines, since the
# table is hand-maintained and a site can name the rule without ever naming the file.
# 2>/dev/null || true so a missing range path (no docs/, no exec-plans/active/) and a
# no-match result both yield "nothing found" rather than a non-zero exit under set -e.
grep -rln "{changed single source basename without .md}\|{rule or step IDs: R2, INV-T02, Q3d, ⑤c}" \
  .claude/ exec-plans/active/ docs/ *.md 2>/dev/null || true
# then cat each hit — including the ones the diff did NOT touch, which are the point
```

Pass the result into the prompt under `## Referrers`. What is **required** is the annotated path
list — each referrer, and whether the diff touched it. Full contents are optional, for files the
reviewer could not otherwise reach.

The list is the part that matters because of what the subagent lacks: not file access, but the
reading of the diff that says **which rule other sites depend on**. That reading is the one the
caller has already done by getting here. A referrer nobody hands over is one nobody thinks to open,
and the sites nobody thought to open are the entire point of that lap. Marking which the diff
touched is what lets the reviewer tell a followed dependency from a missed one.

**If the working tree is not clean** (uncommitted changes exist):
- Remind the user to commit or stash all changes before running this skill, OR
- Include `git diff --cached` and `git diff` output in the review context in addition to `git diff main...HEAD`

**If `exec-plans/active/` is empty**, proceed without AC context (review for general code quality only).

**If multiple exec-plans exist**, include all of them and let the reviewer determine which ACs apply to the diff.

### Step 2: Determine review scope

| Condition | Review focus |
|-----------|-------------|
| exec-plan with AC-001~ exists, and its `## Sources` name US / spec sections | AC compliance **judged against those sections** + tests-vs-ACs independence + code quality |
| exec-plan with AC-001~ exists, but no `## Sources` (or all `n/a`) | Same, judged against the AC lines alone — say so in the verdict, since a one-liner is a weaker yardstick |
| No exec-plan | Code quality only (correctness, readability, security, maintainability) — the tests-vs-ACs check needs AC text to judge against |

### Step 3: Launch independent agent

Use the `Agent` tool to spawn a **subagent with no session context**.

Construct the prompt as follows (substitute `{…}` placeholders with the actual collected content):

```
You are a code reviewer with no prior context about this implementation.
Review the following changes objectively.

## Changed files
{output of: git diff --name-only main...HEAD}

## Full diff (committed)
{output of: git diff main...HEAD}

## Staged changes (uncommitted)
{output of: git diff --cached, or "none"}

## Unstaged changes
{output of: git diff, or "none"}

## Acceptance criteria (from exec-plan)
{contents of exec-plans/active/*.md, or "None — review for general quality only"}

## AC sources (the US bullets / spec sections each AC condenses)
{for each row of the plan's ## Sources table: the AC-ID, the section's path, and the section text.
 Or "None — the plan has no ## Sources table" / "n/a — {reason recorded in the plan}"}

## Referrers — sites that name what this diff changed (for review point 1d, dependency backflow)
{for each file the grep in Step 1 returned: its path and whether the diff touched it. Include full
 content only where the reviewer could not otherwise open it. Or "none — nothing outside the diff
 names what it changed" / "not applicable — the diff changes no documented process".
 Open these yourself and read them from the top. You may add referrers you find, but do not treat an
 empty or missing list as evidence that no site depends on the change — report that as a gap in the
 review context instead.}

## Review instructions

Perform a thorough review covering:

1. **AC compliance** (if AC exists)
   - Does the implementation satisfy each AC?
   - Are there any ACs not covered by the changes?
   - **Judge against the AC's sources, not only its one line.** An exec-plan AC is a condensation:
     the checkable bullets live in the US file and the behavior in the spec section. The plan's
     `## Sources` table names both — open them and judge the diff against what they say. An
     implementation can satisfy the wording of a one-liner and miss the bullets it stands for.
   - Report any AC where the diff satisfies the line but not its source, and any place the source
     and the AC line disagree (that is a spec defect, not an implementation one).
   - If the plan has no `## Sources` table, say so and review against the AC lines alone — do not
     guess which spec section applies.

1b. **`[E2E]` AC compliance — judge the whole, not only the fragments**
   - The plan's `[E2E]` acceptance criteria (`- [x] AC-NNN: [E2E] ...`) state the through-flow that
     must work. Per-AC compliance above can be ✅ across the board while the through-flow is broken:
     each fragment satisfies its own criterion and nothing connects them.
   - For each `[E2E]` AC, trace the flow through the diff: can a user actually get from its 前提 to
     its 完了条件 with this code? Name the first step that breaks if not.
   - Is there a test that exercises the whole flow, or only per-AC unit tests?
   - For a refactoring plan, the `[E2E]` AC asserts *preservation* — does the diff change observable
     behavior anywhere along that flow?
   - This is the check the authoring agent is least able to do for itself, since it verified each AC
     as it built it. Weight it accordingly.

1c. **Do the tests express the ACs, or the implementation?**
   - For each AC, read its test **against the AC text**, not against the code: are the test's
     given / when / then the ones the AC states? A test that restates what the implementation
     happens to do is green by construction and proves nothing.
   - Signs a test mirrors the implementation: it asserts internal calls, intermediate state, or a
     literal copied from the implementation; its expected value is whatever the code produces
     (an error message string, a rounding result, a default) rather than something the AC names;
     it was clearly written by reading the code (same helper structure, same edge cases, no case
     the AC mentions but the code omits).
   - Cross-check the plan's `## Decision Log`: each AC should have an `AC-NNN red-first:` entry
     recorded **before** its `AC-NNN done.` entry (the red observation that froze the expectation;
     the convention is in `.claude/skills/run-tests/red-first.md` if you want the details).
     A missing or out-of-order entry is not proof of a bad test — report it as a 🟡 finding and
     judge the test on its content.
   - Is there any AC the tests do not actually constrain — i.e. would they still pass if that AC's
     behavior were removed?
   - This, like 1b, is a check the implementing agent cannot perform on itself: it wrote both sides.

1d. **Process changes: does the process still run one lap?**
   - Applies when the diff changes a **documented process** — a loop, a resumable run, a stop
     condition, a gate, an exemption, or a rule other rules consume (skill definitions, CLAUDE.md,
     hooks). Skip for ordinary feature diffs.
   - Do not stop at "every call site describes the rule the same way". Walk the process and name the
     state after each step, at least: the **second iteration** (the state the first pass leaves is
     the next pass's input), a **resume** from the files alone mid-process, and the **exemption**
     path (does every downstream gate know about it?).
   - **Dependency backflow** — the lap that needs the diff, so it belongs here more than anywhere:
     for each rule, single source, record format or step label the diff changed, walk the sites that
     name it **from the top of each one's own file**, using the referrer contents supplied under
     `## Referrers` above. The point of the lap is the sites the diff did **not** touch. Ask whether
     the material the changed rule now requires is in hand at the moment that site runs, and whether
     a site that hands work onward (a subagent prompt, a handoff) actually passes it. A site can be
     textually unchanged, still agree with the rule, and be judging with what it does not have.
     If no referrers were supplied, say so rather than assuming there are none.
   - Report: a state that cannot be entered or left, two rules answering the same state differently,
     a gate that fires on the state meaning success, an entry condition the process's own output
     violates, a consumer left deciding without the material the change made necessary, or a pointer
     (`Q3d`, `Step 0b`, `⑤c`) that no longer resolves at its target. **Exclude `## Decision Log` and
     `## Progress Log` entries** — those are append-only history and record what was true when
     written; "correcting" them destroys the record of the correction. Checked-off ACs describing
     completed work are history too. Unchecked ACs and Task Breakdown entries are in scope.
   - The convention and its laps are in `.claude/skills/create-exec-plan/process-walkthrough.md`.

2. **Correctness**
   - Logic errors, edge cases not handled, off-by-one errors
   - Incorrect assumptions about inputs or state

3. **Security**
   - Injection vulnerabilities (SQL, command, XSS)
   - Improper input validation or output encoding
   - Hardcoded secrets or credentials

4. **Readability & maintainability**
   - Naming clarity (variables, functions, files)
   - Overly complex logic that could be simplified
   - Missing or misleading comments (only flag if a comment is needed but absent)

5. **Test coverage**
   - Are the changes adequately tested?
   - Do tests verify behavior, not just implementation details?

## Output format

=== Code Review Results ===

Reviewed by: Independent Agent (no implementation context)
Branch diff: main...HEAD

### AC Compliance
{For each AC: ✅ Satisfied / ❌ Not satisfied / N/A}

### [E2E] AC Compliance
{For each [E2E] AC: ✅ through-flow holds / ❌ breaks at {step} / N/A (no [E2E] AC in plan)}
{Whole-flow test exists? ✅ / ❌ per-AC tests only}

### Process walkthrough (only if the diff changes a documented process — omit otherwise)
{Second iteration: ✅ / ❌ <state where it breaks>}
{Resume from files alone: ✅ / ❌ <entry check that rejects the left-behind state>}
{Exemption path: ✅ / ❌ <downstream gate unaware of the exemption>}
{Dependency backflow: grep pattern used, referrers found <list them, marking which the diff touched>
 — ✅ / ❌ <untouched site now judging without the material the change requires>}

### Tests vs. ACs (independence)
{For each AC: ✅ the test asserts what the AC states / ⚠️ partially / ❌ the test mirrors the
implementation — with the line that gives it away}
{red-first evidence in the Decision Log: ✅ present and ordered / ⚠️ missing for AC-NNN / N/A}

### Findings

| # | Severity | File | Line | Issue | Suggestion |
|---|----------|------|------|-------|------------|
| 1 | 🔴 Critical | ... | ... | ... | ... |
| 2 | 🟠 High    | ... | ... | ... | ... |
| 3 | 🟡 Medium  | ... | ... | ... | ... |
| 4 | 🔵 Low     | ... | ... | ... | ... |

### Summary
- Critical issues: {count}
- High issues: {count}
- Medium issues: {count}
- Low issues: {count}

### Verdict
✅ Approved — no blocking issues
⚠️  Approved with suggestions — address medium/low items at your discretion
❌ Changes requested — fix critical/high issues before proceeding

Report the review result only. Do not make any code changes.
```

**Important**: The spawned agent must NOT make any edits or commits. It only reports findings.

### Step 4: Present findings to the user

After the independent agent returns its report, present it verbatim and guide next steps. The ❌
row differs by caller — **who may act on the findings is exactly what changed between the two
paths**:

| Verdict | Manual path (a human ran this skill) | Called from `run-exec-plan` Step 4a |
|---------|---------------------------------------|--------------------------------------|
| ✅ Approved | Proceed to `/pre-pr` | Continue to reporting; hand off to `pre-pr` |
| ⚠️  Approved with suggestions | Discuss items with user, then proceed to `/pre-pr` | Continue to reporting; hand off to `pre-pr`, mentioning the suggestions |
| ❌ Changes requested | Address critical/high findings yourself, then re-run `/docode-review` | **Halt with stop condition (f) and surface the findings verbatim. Do not fix them and re-run** — see `run-exec-plan/SKILL.md` Step 4a. Deciding which findings to act on is a governance call the driver may not make on its own behalf, precisely because it is the same agent whose self-review this gate exists to check |

---

## Result report format

```
=== Code Review — Independent Agent ===

{full report from the spawned agent}

---
Next step (manual path — a human ran this skill directly):
  ✅ Approved       → Run /pre-pr
  ⚠️  With suggestions → Discuss findings above, then run /pre-pr
  ❌ Changes needed  → Fix issues above, then re-run /docode-review

Next step (called from run-exec-plan Step 4a — see that skill, do not apply the manual-path row above):
  ✅ / ⚠️  → Hand off to /pre-pr
  ❌       → HALT with stop condition (f); do not fix and re-run
```

---

## Completion criteria

- [ ] Working tree state was verified (`git status`)
- [ ] `git diff main...HEAD` (and staged/unstaged diffs if applicable) were collected
- [ ] Active exec-plan contents were loaded (or confirmed absent)
- [ ] Independent agent was spawned via the `Agent` tool
- [ ] Agent report was presented to the user
- [ ] Next step was communicated based on the verdict
