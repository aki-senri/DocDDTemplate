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
2. Check the plan's ACs for readiness (testability) before any code is written
3. Load the documents needed for implementation, **including the sources each AC condenses**
4. Determine the branch name
5. Record the start of work in the progress log

---

## Steps

### Step 0: Baseline test verification

Before starting implementation, verify that all tests currently pass.

- Run the `run-tests` skill (AC coverage check can be skipped)
- **All pass → proceed to the next step**
- **Expected reds are not failures here.** If the plan is being resumed and a test was frozen red by
  a red-first observation whose AC is still unchecked (`run-tests` Step 2c), it is the target being
  steered toward, not a broken baseline. Everything else must pass
- **If there are other failures → do not start implementation on this branch**
  - Determine the course of action through the spec alignment gate and fix the issues first
  - Starting implementation from a green test state makes it clear whether failures are caused by your changes or were pre-existing

### Step 1: Confirm the execution plan

List the files in `exec-plans/active/` and confirm the plan to work on with the user.

- If there is only one plan, select it
- If there are multiple plans, prompt the user to select one
- If there are no plans, prompt to run the `create-exec-plan` skill and stop

### Step 1b: AC readiness check

Check every unchecked AC of the selected plan against the five checks in
[`../create-exec-plan/ac-readiness.md`](../create-exec-plan/ac-readiness.md) — the same file
`create-exec-plan` and `run-exec-plan` use. Follow it; do not re-derive the criteria here.

| Verdict | Action |
|---------|--------|
| READY | Proceed |
| ⚠️ (R3 or R4 unmet for a stated reason) | Report it and proceed |
| **NOT READY** | Present every failing check by its own ID (any of `R1` / `R2` / `R5`, and `R3` / `R4` when no reason can be given) with the phrase that fails each one, and ask the user: rewrite the AC now, or proceed anyway. **Record the user's decision in the Progress Log** |

The human is present on this path, so a thin AC can be fixed in conversation rather than blocking.
Two things follow, and both are intended:

- Proceeding anyway is the user's call about *their own* next step. It does not clear the criterion —
  a later `run-exec-plan` will still halt on it (stop condition (a)), because an unattended loop
  cannot make the judgement the user just made.
- A plan created through `create-exec-plan` should already be clean here. A NOT READY criterion at
  this point usually means the plan came from somewhere else (a reconcile plan from `promote-spec`,
  or a hand-written one).

### Step 2: Load required documents

Load the following documents and confirm the implementation prerequisites.

| Document | Content to confirm |
|----------|-------------------|
| `docs/07_ai_context/CONTEXT.md` | Current phase, development rules, tech stack |
| `docs/04_implementation/invariants.md` | Invariants to follow (INV-XXX) |
| Selected `exec-plans/active/*.md` | Acceptance criteria, `## Sources`, and task breakdown |
| Everything the plan's `## Sources` names | The US bullets and spec sections each AC condenses |

**Why the sources and not just the plan.** An exec-plan AC is one line; `create-requirements` keeps
its 2–5 checkable bullets in the US file and `create-spec` keeps the behavior in the spec section
marked "satisfies AC-NNN". Starting from the one-liner means starting from an interpretation of it.
Open the AC rows you are about to work on and read what they point at — the same material the
autonomous driver reads in its Step 1b, per
[`../create-exec-plan/ac-sources.md`](../create-exec-plan/ac-sources.md).

| What you find | Action on this path |
|---------------|--------------------|
| **Refinement** of the AC line | Use it — it is the granularity to implement and test at |
| A **separate outcome**, or a **contradiction** with the AC line | Present both readings to the user and let them decide. The human is here, so this is a conversation rather than the HALT the unattended loop takes |
| The row says `n/a（理由）`, or the plan has no `## Sources` table | Note it and proceed on the AC text. Do not reconstruct sources from existing code |

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

**Before any of the layer ordering below: write the test first.** For each AC, transcribe its
given / when / then — from the AC line **and the sources loaded in Step 2**, never from existing
code — into a test, run it, and confirm it fails for the right reason **before**
writing the implementation — the red-first rule (`INV-T02`), defined in
[`../run-tests/red-first.md`](../run-tests/red-first.md). The layer order in this section decides
what to build first *once the failing test is in place*; it does not come before it.

If the plan has a `[E2E]` AC, its test goes in first, red, before the functional ACs are
implemented — same reason the autonomous driver does it in Step 0c: it is the one test in the run
that no implementation could have shaped.

If a test cannot be written from the AC text **and its sources** without deciding an expected result
none of them states, that is a readiness defect (`R2` / `R3`), not a test-writing problem — rewrite
the AC with the user, as in Step 1b.

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

- [ ] Confirmed that baseline tests all pass, expected reds aside (Step 0)
- [ ] Execution plan selected and confirmed
- [ ] AC readiness checked for every unchecked AC; any NOT READY criterion was raised with the user
      and their decision recorded in the Progress Log (Step 1b)
- [ ] Loaded `CONTEXT.md`, `invariants.md`, the selected execution plan, and the US / spec sections
      its `## Sources` names for the ACs being worked on (any conflict between a source and its AC
      line was put to the user)
- [ ] Branch name finalized
- [ ] "Implementation started" recorded in the execution plan's progress log
- [ ] The red-first order is understood for the first task: its test is written from the AC and
      observed failing before the implementation (see the implementation order guide)

Final report output by the agent:

```
=== Ready to start implementation ===

Baseline  : ✅ All {n} tests passed
Work plan : exec-plans/active/YYYY-MM-{name}.md
Readiness : ✅ {n} ACs READY   |   ⚠️ AC-NNN (R4: {reason})   |   ❌ AC-NNN NOT READY (R2) — {user's decision}
Branch    : feature/{name}
Confirmed : CONTEXT.md / invariants.md / execution plan
Sources   : {読んだ US / spec の節}   |   ⚠️ プランに ## Sources が無い   |   ➖ n/a ({理由})

First task: {first item in exec-plan task breakdown}
Order    : red-first — {対応する AC} のテストを AC 行と起点（`## Sources`）から起草し、赤を確認してから実装する
```
