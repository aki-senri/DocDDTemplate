---
name: docode-review
description: |
  Launches an independent agent (with no implementation context) to review changed code.
  The agent reviews the diff against acceptance criteria (if available) and general code quality,
  providing an objective perspective separate from the implementing agent. It also judges whether
  each test expresses its AC rather than mirroring the implementation — the one check the agent
  that wrote both sides cannot perform on itself.
# disable-model-invocation is intentionally false: this skill's core function is to spawn
# an independent subagent via the Agent tool, which requires model invocation.
# All other skills set this to true because they only issue instructions to the current agent.
disable-model-invocation: false
---

# Skill: Independent Agent Code Review

> **When to run**: After implementation is complete, before running `/pre-pr`
>
> **Purpose**: Get an objective review from an agent that has no knowledge of the implementation
> decisions made during coding. This avoids confirmation bias from the implementing agent.
>
> **Prerequisites**:
> - The working tree is clean (all changes are committed — run `git status` to verify)
> - At least one commit exists on the current branch
> - The branch has diverged from `main` (there are changes to review)

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

**If the working tree is not clean** (uncommitted changes exist):
- Remind the user to commit or stash all changes before running this skill, OR
- Include `git diff --cached` and `git diff` output in the review context in addition to `git diff main...HEAD`

**If `exec-plans/active/` is empty**, proceed without AC context (review for general code quality only).

**If multiple exec-plans exist**, include all of them and let the reviewer determine which ACs apply to the diff.

### Step 2: Determine review scope

| Condition | Review focus |
|-----------|-------------|
| exec-plan with AC-001~ exists | AC compliance + tests-vs-ACs independence + code quality |
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

## Review instructions

Perform a thorough review covering:

1. **AC compliance** (if AC exists)
   - Does the implementation satisfy each AC?
   - Are there any ACs not covered by the changes?

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

After the independent agent returns its report, present it verbatim and guide next steps:

| Verdict | Recommended action |
|---------|--------------------|
| ✅ Approved | Proceed to `/pre-pr` |
| ⚠️  Approved with suggestions | Discuss items with user, then proceed to `/pre-pr` |
| ❌ Changes requested | Address critical/high findings, then re-run `/docode-review` |

---

## Result report format

```
=== Code Review — Independent Agent ===

{full report from the spawned agent}

---
Next step:
  ✅ Approved       → Run /pre-pr
  ⚠️  With suggestions → Discuss findings above, then run /pre-pr
  ❌ Changes needed  → Fix issues above, then re-run /docode-review
```

---

## Completion criteria

- [ ] Working tree state was verified (`git status`)
- [ ] `git diff main...HEAD` (and staged/unstaged diffs if applicable) were collected
- [ ] Active exec-plan contents were loaded (or confirmed absent)
- [ ] Independent agent was spawned via the `Agent` tool
- [ ] Agent report was presented to the user
- [ ] Next step was communicated based on the verdict
