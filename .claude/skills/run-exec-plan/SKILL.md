---
name: run-exec-plan
description: |
  Autonomous driver that implements an exec-plan's acceptance criteria one at a time
  without stopping for confirmation between criteria. Before the loop starts it gates on
  AC readiness (testability), so an untestable criterion stops the run before any code is
  written rather than mid-implementation. For each unchecked AC it runs
  implement -> run-tests -> check-invariants, and on green it checks the box, records a
  Decision Log entry, and moves to the next AC. Halts ONLY on explicit stop conditions
  (missing/ambiguous AC, tests still red after bounded retries, a test change required,
  an irreversible/outward action, or an INV violation needing scope expansion).
  Opt-in: runs only when the user explicitly invokes it; default behavior is unchanged.
disable-model-invocation: true
---

# Skill: Run Execution Plan (Autonomous Driver)

> **When to run**: When the user explicitly wants the agent to implement an exec-plan's
> acceptance criteria autonomously, without being asked to confirm between each AC.
>
> **Purpose**: Provide the missing "Generator" / inner loop of DocDD. Automate only the
> **execution** of work whose spec (AC) is already frozen — implement, verify, self-repair,
> advance — while leaving every **governance** decision to the human. This addresses
> issue #11 (reduce mid-implementation stops) without dissolving DocDD's spec gates.
>
> **Prerequisites**:
> - An active plan must exist in `exec-plans/active/` with at least one `AC-NNN:` defined
> - `start-feature` should already have run (baseline green, branch chosen, docs loaded)
> - `docs/05_quality/test_strategy.md` must have `test_command` set (used by `run-tests`)

---

## Design principle (read first)

This skill automates the **inner loop only**. It must never make a **governance** decision
on the human's behalf.

| Layer | Examples | Who decides |
|-------|----------|-------------|
| **Inner loop — automate** | Implement an AC, run tests, fix a failing test caused by an implementation bug, re-run, advance to the next AC | **This skill (no confirmation)** |
| **Outer gate — never automate** | What to build (defining AC), changing a test's expectation, modifying the spec, `promote-spec`, creating/pushing a PR | **Human (halt and ask)** |

The point of autonomy here is *not* "stop less". It is "stop **only** at the boundaries that
genuinely need a human, and never in the middle of executing a frozen AC."

---

## What this skill does

1. Select the active exec-plan, confirm baseline is green, and gate on **AC readiness**
   (every unchecked AC is testable as written — otherwise halt before the loop starts)
2. Loop over each unchecked AC:
   a. Implement the AC
   b. Run `run-tests` (spec alignment gate)
   c. Run `check-invariants` (and `check-doc-freshness`, advisory)
   d. On green: check the AC box, append a Decision Log entry, continue to the next AC
   e. On red: attempt a **bounded** self-repair (default 3 tries); if still red, **halt**
3. When all ACs are checked (or a stop condition fires): produce a summary and hand off
   to `pre-pr` (which remains a separate, human-reviewed step)

---

## Steps

### Step 0: Preconditions

- Confirm exactly one target plan. If several active plans exist, ask the user which one
  (this is plan *selection*, an outer-gate choice — confirm it once, up front).
- Run `run-tests` as a baseline. If baseline is already red, **halt** — do not start a loop
  on a red baseline (you could not attribute failures to your own changes).
- **Run the AC readiness gate** (below) over every unchecked AC.
- See **Retry budget** below; default `MAX_REPAIR_ATTEMPTS = 3`.

#### Step 0b: AC readiness gate (before the loop, not inside it)

Check **every** unchecked AC in the plan — not just the first — against the five checks in
[`../create-exec-plan/ac-readiness.md`](../create-exec-plan/ac-readiness.md). Follow that file;
do not re-derive the criteria here.

| Verdict | Action |
|---------|--------|
| All READY (⚠️ allowed with its reason recorded) | Start the loop |
| Any **NOT READY** | **Do not start the loop.** Halt with stop condition (a) |

Record the result in the plan's `## Decision Log` either way — as
`AC readiness: all N ACs READY (Step 0b)`, or as the HALT entry described in the resume-state
convention, naming the failing check and the phrase that fails it.

Why the whole set and not just the next AC: the point of the gate is to spend the human's attention
**once**, before implementation, rather than halting three ACs later on a defect that was already
visible. A criterion that is READY today does not become unready by being implemented, so nothing is
lost by checking early.

Why the driver may not fix a NOT READY criterion itself: rewriting an AC decides *what to build* —
outer-gate (see the Design principle above). Halting is the only correct move when no human is
present, which is exactly why `create-exec-plan` runs the same check at authoring time, where a
human is.

### Step 1: Pick the next AC

- From the plan, take the first `- [ ]` (unchecked) AC in order.
- Step 0b already cleared the whole set for readiness. If implementing it nonetheless reveals that
  the AC is ambiguous or under-specified (e.g. it reads as testable but two incompatible readings
  both satisfy it), **halt** with stop-condition (a). Do not guess the intent.
- If no unchecked AC remains, go to Step 4.

### Step 2: Implement the AC

- Implement following the order guidance in `docs/04_implementation/patterns.md`
  (stable layer first), same as `start-feature` describes.
- Keep the change scoped to this AC. If satisfying it requires expanding scope or violating
  an invariant you cannot resolve within scope, **halt** with stop-condition (e).

### Step 3: Verify

Run the verification skills. Note the two invocation modes (they differ by
`disable-model-invocation`):
- `run-tests` is model-invocable (`false`) — invoke it directly via the Skill tool.
- `check-invariants` / `check-doc-freshness` are non-invocable (`true`) — execute them by reading
  their `SKILL.md` and following the steps inline. Do not try to call them via the Skill tool; it
  is not exposed for them.

1. `run-tests` (invoke via the Skill tool)
   - **All green** -> continue to Step 3b.
   - **Red because the implementation has a bug** (spec alignment gate option A): this is the
     normal inner-loop case. Fix the implementation and re-run. Count this attempt against
     `MAX_REPAIR_ATTEMPTS`.
   - **Red because the test's expectation must change** (spec alignment gate option B): a test
     change is an outer-gate action — **halt** with stop-condition (c). Never edit a test's
     expectation to match implementation behavior (INV-T01).
   - **Still red after `MAX_REPAIR_ATTEMPTS`** -> **halt** with stop-condition (b).
   - **Green, but `run-tests` returns a hold on an uncovered `[E2E]` AC**: the tests that ran do
     not include one for the through-flow, so "green" does not mean the E2E criterion is met.
     **Halt** with stop-condition (a) — writing the E2E test means deciding what the through-flow
     is, which is an outer-gate judgement. Do not check the `[E2E]` AC's box on the strength of the
     functional tests, and do not author the E2E test to unblock yourself.
     (A plan with **no** `[E2E]` AC at all is only a ⚠️ from `run-tests` — continue the loop.)
2. `check-invariants` (follow inline)
   - Violation resolvable within the current AC's scope -> fix and re-run Step 3. This counts
     against `MAX_REPAIR_ATTEMPTS` (same budget as test repair); if exhausted, **halt** with
     stop-condition (b).
   - Violation requiring scope expansion -> **halt** with stop-condition (e).
3. `check-doc-freshness` (follow inline, advisory) — update any docs whose `tracks:` matches changed files.

**Step 3b — on green:**
- Change the AC's `- [ ]` to `- [x]` in the plan.
- Append a Decision Log entry (see "Resume-state convention" below).
- Return to Step 1 **without asking the user**.

### Step 4: Finish the loop

When all ACs are `- [x]` (or a stop condition fired), stop the loop and report (see format
below). **Do not create a PR.** Hand off to `pre-pr` as a separate, human-reviewed step.

---

## Stop conditions (halt and ask the human)

The driver continues autonomously **except** in these cases. When one fires, stop, write the
current state to the Decision Log, and surface a concise summary to the user.

| ID | Condition | Why it is a human decision |
|----|-----------|----------------------------|
| (a) | An AC is missing, ambiguous, or under-specified. Detected **before the loop** by the Step 0b readiness gate (any NOT READY criterion), and as a backstop during the loop — including a `[E2E]` AC whose test does not exist, so `run-tests` holds | Deciding *what to build* (and what the through-flow is) is outer-gate (spec-first principle) |
| (b) | Tests still red after `MAX_REPAIR_ATTEMPTS` self-repair tries | Repeated failure signals a real problem the human should see |
| (c) | A test's *expectation* must change to pass | Test changes must be grounded in a spec change (INV-T01) |
| (d) | An irreversible / outward-facing action is next (create or push a PR, `promote-spec`, deleting tags) | Outward effects require human authorization |
| (e) | An INV violation cannot be resolved without expanding scope | Scope expansion is a planning decision, not execution |

If none apply, **keep going** — do not stop merely because progress feels "far enough" or to
ask for reassurance. (This is the "context anxiety" failure mode the loop exists to avoid.)

---

## Resume-state convention (file-based handoff)

So that a fresh session can resume from files alone (no conversation history), every loop
iteration records enough state in the plan itself:

- AC checkboxes (`- [x]`) are the canonical "what is done" marker.
- After each completed AC, append to `## Decision Log`:
  ```markdown
  ### YYYY-MM-DD
  - AC-NNN done. <one line: what was implemented + key files>. Tests green ({n} passing).
  ```
- On any halt, append:
  ```markdown
  ### YYYY-MM-DD
  - HALT at AC-NNN (stop condition <id>). <what is blocking> <what the human must decide>.
  ```

A new session resuming this plan must be able to continue using only the checkboxes and the
Decision Log — never assume the prior conversation is available.

## Retry budget

`MAX_REPAIR_ATTEMPTS` defaults to **3** per AC. Counts implementation-bug repair attempts
(spec alignment gate option A) and in-scope invariant fixes that re-run verification — not green
re-verifications. When the budget is exhausted, halt with stop-condition (b).

---

## Completion criteria

- [ ] Target plan selected and baseline confirmed green (Step 0)
- [ ] AC readiness gate run over **every** unchecked AC before the loop, and its result recorded in
      the Decision Log (Step 0b)
- [ ] Each processed AC went through implement -> run-tests -> check-invariants
- [ ] Every AC reached is either `- [x]` (green) or recorded as a HALT in the Decision Log
- [ ] Decision Log updated per the resume-state convention
- [ ] No PR was created by this skill (handoff to `pre-pr` only)

Final report output by the agent:

```
=== Autonomous run complete ===

Plan      : exec-plans/active/YYYY-MM-{name}.md
Readiness : ✅ {n} ACs READY (Step 0b)   |   ❌ AC-NNN NOT READY (R2) → loop not started
Processed : AC-001 ✅  AC-002 ✅  AC-003 ⏸ (HALT: stop condition c)  AC-004 …
Tests     : ✅ {n} passing
Stopped at: {none | AC-NNN, stop condition <id>: <reason>}

Next action: {run /pre-pr for the completed ACs | human decision needed for the HALT}
```
