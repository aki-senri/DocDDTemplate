---
name: start-feature
description: |
  Preparation skill for starting feature implementation.
  Selects work from exec-plans and reviews the necessary documents before beginning implementation.
  Use when you're unsure what to implement or need to know what to confirm before starting.
disable-model-invocation: true
---

# Skill: Start Feature Implementation

> **When to run**: When selecting new work from `exec-plans/active/` and beginning implementation
>
> **Purpose**: Prevent overlooked pre-implementation checks and ensure the agent can start implementation with the correct assumptions.
>
> **Prerequisites**:
> - An active plan must exist in `exec-plans/active/`
> - Phase 1 (knowledge base construction) must be complete (`docs/04_implementation/invariants.md` must exist)

---

## What this skill does

1. Confirm and select the execution plan
2. Load the documents needed for implementation
3. Determine the branch name
4. Record the start of work in the progress log

---

## Steps

### Step 0: Baseline test verification

Before starting implementation, verify that all tests currently pass.

- Run the `run-tests` skill (AC coverage check can be skipped)
- **All pass → proceed to the next step**
- **If there are failures → do not start implementation on this branch**
  - Determine the course of action through the spec alignment gate and fix the issues first
  - Starting implementation from a green test state makes it clear whether failures are caused by your changes or were pre-existing

### Step 1: Confirm the execution plan

List the files in `exec-plans/active/` and confirm the plan to work on with the user.

- If there is only one plan, select it
- If there are multiple plans, prompt the user to select one
- If there are no plans, prompt to run the `create-exec-plan` skill and stop

### Step 2: Load required documents

Load the following documents and confirm the implementation prerequisites.

| Document | Content to confirm |
|----------|-------------------|
| `docs/07_ai_context/CONTEXT.md` | Current phase, development rules, tech stack |
| `docs/04_implementation/invariants.md` | Invariants to follow (INV-XXX) |
| Selected `exec-plans/active/*.md` | Acceptance criteria and task breakdown |

Also load the following depending on the platform:

| Condition | Additional documents to read |
|-----------|----------------------------|
| Requirements definition phase | `docs/01_requirements/user_stories/{platform}.md` |
| Design needed | `docs/03_design/architecture.md` |
| Web application | `docs/03_design/api_spec.md` |

### Step 3: Determine the branch name

Suggest a branch name following the "branch strategy" rule in CONTEXT.md.

- Standard pattern: `feature/{exec-plan-name}`
- Example: `feature/user-auth`

### Step 4: Update the progress log

Append the following to the selected `exec-plans/active/*.md`.

```markdown
### YYYY-MM-DD
- Implementation started. Branch: feature/{name}
```

---

## Implementation order guide

**Basic principle of implementation order**: Implement from the stable layer (the depended-upon side) first, then the unstable layer (the depending side) afterward.
The specific order follows the definitions in `docs/04_implementation/patterns.md`.

**Common pattern:**
```
Data structures (Model / Entity / Type)
  → Data access layer (Repository / DAO) interface
  → Business logic layer (Service / UseCase) interface
  → Implementation of each layer
  → UI / Presentation layer
```

> **Example (layered architecture + MVVM):**
> ```
> Model → Repository (Interface) → Service (Interface)
>          ↓                         ↓
>         Repository (impl)     Service (impl) → ViewModel → View
> ```
>
> **Example (Web API + SPA):**
> ```
> BE: Entity → Repository (Interface) → Service → Controller
> FE: Type definitions → API client → Logic layer → UI components → Pages
> ```

See `docs/04_implementation/patterns.md` for detailed implementation order and project-specific patterns.

---

## Completion criteria

- [ ] Confirmed that baseline tests all pass (Step 0)
- [ ] Execution plan selected and confirmed
- [ ] Loaded `CONTEXT.md`, `invariants.md`, and the selected execution plan
- [ ] Branch name finalized
- [ ] "Implementation started" recorded in the execution plan's progress log

Final report output by the agent:

```
=== Ready to start implementation ===

Baseline  : ✅ All {n} tests passed
Work plan : exec-plans/active/YYYY-MM-{name}.md
Branch    : feature/{name}
Confirmed : CONTEXT.md / invariants.md / execution plan

First task: {first item in exec-plan task breakdown}
```
