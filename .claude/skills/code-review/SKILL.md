---
name: code-review
description: |
  Launches an independent agent (with no implementation context) to review changed code.
  The agent reviews the diff against acceptance criteria (if available) and general code quality,
  providing an objective perspective separate from the implementing agent.
disable-model-invocation: false
---

# Skill: Independent Agent Code Review

> **When to run**: After implementation is complete, before running `/pre-pr`
>
> **Purpose**: Get an objective review from an agent that has no knowledge of the implementation
> decisions made during coding. This avoids confirmation bias from the implementing agent.
>
> **Prerequisites**:
> - At least one commit exists on the current branch
> - The branch has diverged from `main` (there are changes to review)

---

## What this skill does

Spawns a **new, independent agent** via the `Agent` tool and passes it:

1. The full diff of changes (`git diff main...HEAD`)
2. The active exec-plan (AC definitions), if one exists
3. A structured review prompt

The independent agent has no memory of the current session and reviews the code from scratch.

---

## Steps

### Step 1: Collect context

Run the following commands to gather the review context.

```bash
# Changed files list
git diff --name-only main...HEAD

# Full diff
git diff main...HEAD

# Active exec-plan (if exists)
ls exec-plans/active/
```

If `exec-plans/active/` is empty, proceed without AC context (review for general code quality only).

### Step 2: Determine review scope

| Condition | Review focus |
|-----------|-------------|
| exec-plan with AC-001~ exists | AC compliance + code quality |
| No exec-plan | Code quality only (correctness, readability, security, maintainability) |

### Step 3: Launch independent agent

Use the `Agent` tool to spawn a **subagent with no session context**.

Construct the prompt as follows:

```
You are a code reviewer with no prior context about this implementation.
Review the following changes objectively.

## Changed files
{output of git diff --name-only main...HEAD}

## Full diff
{output of git diff main...HEAD}

## Acceptance criteria (from exec-plan)
{contents of exec-plans/active/*.md, or "None — review for general quality only"}

## Review instructions

Perform a thorough review covering:

1. **AC compliance** (if AC exists)
   - Does the implementation satisfy each AC?
   - Are there any ACs not covered by the changes?

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
| ❌ Changes requested | Address critical/high findings, then re-run `/code-review` |

---

## Result report format

```
=== Code Review — Independent Agent ===

{full report from the spawned agent}

---
Next step:
  ✅ Approved       → Run /pre-pr
  ⚠️  With suggestions → Discuss findings above, then run /pre-pr
  ❌ Changes needed  → Fix issues above, then re-run /code-review
```

---

## Completion criteria

- [ ] `git diff main...HEAD` was collected
- [ ] Active exec-plan was loaded (or confirmed absent)
- [ ] Independent agent was spawned via the `Agent` tool
- [ ] Agent report was presented to the user
- [ ] Next step was communicated based on the verdict
