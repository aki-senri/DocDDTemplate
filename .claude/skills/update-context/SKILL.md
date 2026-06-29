---
name: update-context
description: |
  Skill to update docs/07_ai_context/CONTEXT.md to reflect the current state.
  Use when a phase transition, priority task change, or tech stack change occurs.
  Automatically called from the complete-exec-plan skill after exec-plan changes.
disable-model-invocation: true
---

# Skill: Update CONTEXT.md

> **When to run**:
> - When a phase transition occurs (Phase 1 → Phase 2, etc.)
> - When priority tasks change (exec-plan added or completed)
> - When the tech stack or development rules change
> - When called from the `complete-exec-plan` skill
> - When you want to periodically verify freshness (when called from the `gc` skill)
>
> **Purpose**: Maintain CONTEXT.md as a "navigation map readable in one screen" at all times.
> If content becomes too large, extract details to a separate document and replace with a pointer.
>
> **Prerequisites**: `docs/07_ai_context/CONTEXT.md` must exist

---

## What this skill does

1. Collect the current state
2. Update each section of CONTEXT.md to reflect the latest state
3. Extract details to a separate document if the file has grown too large

---

## Steps

### Step 1: Collect current state

Verify the following.

| Item | Reference |
|------|-----------|
| Current phase | Determined from the state of `exec-plans/active/` and `exec-plans/completed/` |
| Priority tasks | List of files in `exec-plans/active/` |
| Tech stack changes | Latest entries in `docs/00_project/decisions.md` |
| Development rule changes | Confirmation from user, or changes in `decisions.md` |

**Phase determination criteria:**

| State | Phase |
|-------|-------|
| `docs/00_project/overview.md` does not exist | Phase 0 incomplete |
| `docs/04_implementation/invariants.md` does not exist | Phase 1 incomplete |
| `docs/01_requirements/` is incomplete | Phase 2 in progress |
| An implementation plan exists in `exec-plans/active/` | Phase 3 in progress |
| Only periodic GC work | Phase 4 (continuous quality maintenance) |

### Step 2: Update CONTEXT.md

Review each section of CONTEXT.md and update outdated content.

**Required section structure of CONTEXT.md:**

```markdown
## Project Overview
(3 lines or fewer; keep as-is if unchanged)

## Tech Stack
(Per platform; update if changed)

## Development Rules
- Branch strategy
- PR & review policy
- Testing policy
- AI involvement

## Document Structure
(Paths to each document; update if changed)

## Naming Conventions & Core Coding Principles
(Details as pointer to invariants.md)

## Current Phase & Priority Tasks    ← Updated most frequently
Phase: Phase X (description)
Priority tasks:
  - exec-plans/active/YYYY-MM-{name}.md

## Reference Documents
(Update if changed)
```

### Step 3: Bloat check and extraction

If CONTEXT.md exceeds "one screen (approx. 50 lines)", extract details according to the following criteria.

| Sections prone to bloat | Extraction target |
|------------------------|------------------|
| Tech stack details | `docs/00_project/overview.md` |
| Development rule details | `docs/04_implementation/coding_standards.md` |
| Naming convention details | `docs/04_implementation/invariants.md` |

After extraction, leave a "See {file path} for details" pointer in CONTEXT.md.

---

## Completion criteria

- [ ] Current phase is accurately stated
- [ ] Priority tasks reflect the current state of `exec-plans/active/`
- [ ] No outdated information in tech stack or development rules
- [ ] CONTEXT.md is within 50 lines (extract details if it exceeds this)
- [ ] Changes have been briefly reported

Final report output by the agent:

```
=== CONTEXT.md updated ===

Changes:
  - Current phase: Phase X
  - Priority tasks: {count}
  - {other changes}

Line count: {updated line count} lines (limit: 50 lines)
```
