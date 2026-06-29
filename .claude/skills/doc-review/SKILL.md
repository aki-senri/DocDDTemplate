---
name: doc-review
description: |
  Launches an independent agent (with no authoring context) to review a requirement
  or design document from a DocDD perspective.
  Checks AC testability, completeness, ambiguity, and cross-reference integrity.
  Optional skill — run after writing docs, before /create-exec-plan.
# disable-model-invocation is intentionally false: this skill's core function is to spawn
# an independent subagent via the Agent tool, which requires model invocation.
disable-model-invocation: false
---

# Skill: Independent Document Review

> **When to run**: After writing or updating a requirements or design document,
> before running `/create-exec-plan`
>
> **Purpose**: Get an objective review from an agent that has no knowledge of the authoring
> decisions. This catches DocDD-specific quality issues — vague ACs, untraceable references,
> broken lifecycle state — that automated structural checks cannot detect.
>
> **Prerequisites**:
> - The target document must exist and be saved
> - `docs/` directory structure must be in place (Phase 1 complete)

---

## Background: the `Agent` tool

This skill spawns a **fresh subagent** via the `Agent` tool in an isolated context.
The subagent has no memory of the current session and reviews the document from scratch,
providing the same independence guarantee as `/code-review`.

---

## What this skill does

1. Identify the target document and its type
2. Load the document content and related context files
3. Spawn an independent agent with a structured DocDD-aware review prompt
4. Present the findings and recommend the next step

---

## Steps

### Step 1: Identify target

If the user has not specified a document path, ask:

> "Which document do you want to review? Please provide the path
> (e.g., `docs/01_requirements/user_stories/US-001_foo.md`)"

Then determine the document type from its path:

| Path pattern | Document type |
|-------------|---------------|
| `docs/01_requirements/user_stories/US-*.md` | User Story |
| `docs/03_design/**/*.md` | Design document |
| `docs/04_implementation/**/*.md` | Implementation document |
| `exec-plans/**/*.md` | Exec-plan |
| Other `docs/**/*.md` | General document |

### Step 2: Load context

Collect content for the review prompt using the appropriate commands below.

```bash
# Target document (always)
cat {target document path}

# For User Story review: load constraints and any related exec-plan
cat docs/01_requirements/constraints.md 2>/dev/null || echo "not found"
grep -l "AC-" exec-plans/active/*.md 2>/dev/null | head -3 | xargs cat 2>/dev/null || echo "no active exec-plans"

# For exec-plan review: load the referenced US file(s)
# Extract US references from exec-plan frontmatter or body, then:
cat docs/01_requirements/user_stories/{referenced-US}.md 2>/dev/null || echo "not found"

# Project documentation rules
cat CLAUDE.md
```

**If related files are not found**, proceed with what is available and note the absence in the review prompt.

### Step 3: Launch independent agent

Use the `Agent` tool to spawn a **subagent with no session context**.

Construct the prompt as follows (substitute `{…}` placeholders with actual content):

```
You are a document reviewer with no prior context about this document's authoring.
Review the following document from a DocDD (Document-Driven Development) perspective.

## Document type
{User Story / Design document / Exec-plan / Implementation document / General document}

## Document to review
{full content of target document}

## Related context
### constraints.md (if applicable)
{content, or "not available"}

### Related User Story or exec-plan (if applicable)
{content, or "not available"}

### Project documentation rules (CLAUDE.md excerpt)
{relevant sections covering doc rules, diagram rules, etc.}

## Review criteria

### 1. DocDD structural compliance
- Does the frontmatter include the required fields (`status:`, `tracks:`, `ac_ids:` as applicable)?
- Is `status:` appropriate for the document's actual state?
- For US files: is `ac_ids:` present and consistent with the ACs defined in the document body?
- Are there any forward references (requirements doc linking to design/implementation)?

### 2. Acceptance criteria quality (for User Stories and exec-plans)
- Is each AC specific and verifiable — can it be confirmed pass/fail by a test or manual check?
- Are ACs free from implementation details (what, not how)?
- Are happy-path, error-case, and boundary conditions covered?
- Are any ACs vague, overlapping, or contradictory?

### 3. Clarity and completeness
- For User Stories: is the "As a / I want / So that" structure clear?
  Is the "So that" (the why) meaningful and not circular?
- Are there ambiguous terms that different readers could interpret differently?
- Is there missing information that an implementer would need to proceed?

### 4. Cross-reference integrity
- Do all Markdown links point to files that exist (based on path plausibility)?
- Are constraint IDs (TC-001 etc.) referenced correctly and consistently with constraints.md?
- Are AC-IDs consistent between the US body, `ac_ids:` frontmatter, and any exec-plan?

### 5. Diagram rules compliance (CLAUDE.md)
- Are flow / sequence / class diagrams written in Mermaid?
- Does each ASCII art figure have a plain-text explanation immediately following it?

## Output format

=== Document Review Results ===

Reviewed by: Independent Agent (no authoring context)
Document: {path}
Type: {document type}

### Structural compliance
{For each frontmatter check: ✅ Present / ❌ Missing / N/A}

### AC quality (if applicable)
| AC | Testable? | Clear? | Notes |
|----|-----------|--------|-------|
| AC-001 | ✅ | ✅ | — |
| AC-002 | ⚠️ | ✅ | Vague threshold: "performs well" — specify a measurable value |

### Findings

| # | Severity | Section / Line | Issue | Suggestion |
|---|----------|---------------|-------|------------|
| 1 | 🔴 Critical | ... | ... | ... |
| 2 | 🟠 High    | ... | ... | ... |
| 3 | 🟡 Medium  | ... | ... | ... |
| 4 | 🔵 Low     | ... | ... | ... |

### Summary
- Critical: {count}
- High: {count}
- Medium: {count}
- Low: {count}

### Verdict
✅ Approved — document is ready for the next step
⚠️ Approved with suggestions — address medium/low items at your discretion
❌ Revision needed — fix critical/high issues before proceeding

Report the review result only. Do not modify any files.
```

**Important**: The spawned agent must NOT make any edits or commits. It only reports findings.

### Step 4: Present findings

After the independent agent returns its report, present it verbatim and guide next steps:

| Verdict | Recommended action |
|---------|--------------------|
| ✅ Approved | For US: proceed to `/create-exec-plan`. For exec-plan: proceed to `/start-feature` |
| ⚠️ Approved with suggestions | Discuss items with user, then proceed |
| ❌ Revision needed | Fix critical/high issues, then re-run `/doc-review` |

---

## Result report format

```
=== Document Review — Independent Agent ===

{full report from the spawned agent}

---
Next step:
  ✅ Approved         → /create-exec-plan (for US) or /start-feature (for exec-plan)
  ⚠️ With suggestions → Discuss findings above, then proceed
  ❌ Revision needed  → Fix issues above, then re-run /doc-review
```

---

## Completion criteria

- [ ] Target document identified
- [ ] Related context collected (or absence noted)
- [ ] Independent agent spawned via `Agent` tool
- [ ] Agent report presented to the user verbatim
- [ ] Next step communicated based on the verdict
