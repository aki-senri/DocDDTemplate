---
name: run-exec-plan
description: |
  Autonomous driver that implements an exec-plan's acceptance criteria one at a time
  without stopping for confirmation between criteria. Before the loop starts it gates on
  AC readiness (testability), so an untestable criterion stops the run before any code is
  written rather than mid-implementation, and puts the plan's [E2E] test in place as a failing
  test. For each unchecked AC it runs
  write the failing test -> implement -> run-tests -> check-invariants, and on green it checks the
  box, records a Decision Log entry, and moves to the next AC. Halts ONLY on explicit stop conditions
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
| **Inner loop — automate** | Transcribe a frozen AC into a test and observe it red, implement the AC, run tests, fix a failing test caused by an implementation bug, re-run, advance to the next AC | **This skill (no confirmation)** |
| **Outer gate — never automate** | What to build (defining AC), **deciding an expected result the AC does not state**, changing a test's expectation once frozen, modifying the spec, `promote-spec`, creating/pushing a PR | **Human (halt and ask)** |

Writing a test is on the inner-loop side **only in the transcription sense**: the given / when / then
come from an AC that a human already froze, and readiness (`R2`) guarantees they are present in its
text. The moment the driver would have to *decide* an expected result, it is on the outer-gate side
and must halt — see [`../run-tests/red-first.md`](../run-tests/red-first.md).

The point of autonomy here is *not* "stop less". It is "stop **only** at the boundaries that
genuinely need a human, and never in the middle of executing a frozen AC."

---

## What this skill does

1. Select the active exec-plan, confirm baseline is green, gate on **AC readiness**
   (every unchecked AC is testable as written — otherwise halt before the loop starts), and put
   each `[E2E]` AC's test in place **as a failing test** before any AC is implemented
2. Loop over each unchecked AC:
   a. Write the test for this AC **first**, from the AC text, and observe it fail (red-first)
   b. Implement the AC
   c. Run `run-tests` (spec alignment gate)
   d. Run `check-invariants` (and `check-doc-freshness`, advisory)
   e. On green: check the AC box, append a Decision Log entry, continue to the next AC
   f. On red: attempt a **bounded** self-repair (default 3 tries); if still red, **halt**
3. When all ACs are checked (or a stop condition fires): produce a summary and hand off
   to `pre-pr` (which remains a separate, human-reviewed step)

---

## Steps

### Step 0: Preconditions

- Confirm exactly one target plan. If several active plans exist, ask the user which one
  (this is plan *selection*, an outer-gate choice — confirm it once, up front).
- Run `run-tests` as a baseline. If baseline is already red, **halt** — do not start a loop
  on a red baseline (you could not attribute failures to your own changes).
  **Expected reds do not count as a red baseline.** When resuming a partly-done plan, the tests
  frozen red by an earlier session (`run-tests` Step 2c: a recorded `AC-NNN red-first:` entry whose
  AC is still `- [ ]`) are the reference signal this run is steering toward, not breakage. Baseline
  is green when everything *else* passes. Any other failure still halts.
- **Run the AC readiness gate** (below) over every unchecked AC.
- **Put every `[E2E]` AC's test in place as a failing test** (Step 0c below).
- See **Retry budget** below; default `MAX_REPAIR_ATTEMPTS = 3`.

#### Step 0b: AC readiness gate (before the loop, not inside it)

Check **every** unchecked AC in the plan — not just the first — against the five checks in
[`../create-exec-plan/ac-readiness.md`](../create-exec-plan/ac-readiness.md). Follow that file;
do not re-derive the criteria here.

| Verdict | Action |
|---------|--------|
| All READY | Start the loop |
| ⚠️ (R3 / R4 unmet) **and the reason is already in the plan's Decision Log** | Start the loop |
| ⚠️ with no recorded reason | Treat as NOT READY — the driver may not author the reason itself |
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

#### Step 0c: E2E red-first (still before the loop)

For **every unchecked `[E2E]` AC** in the plan, write its test now — before any AC is implemented —
following [`../run-tests/red-first.md`](../run-tests/red-first.md). Transcribe the through-flow from
the AC text (which traces to the spec's `E2E-NNN`), run it, and confirm **valid red**. Record the
observation in the Decision Log; that entry freezes the expectation.

| Situation | Action |
|-----------|--------|
| Valid red observed for every `[E2E]` AC | Record it and start the loop |
| An earlier session already placed it (a recorded `red-first` entry, AC still `- [ ]`) | Re-run it, confirm the same red, and start the loop — do not rewrite the test |
| The through-flow cannot be transcribed without inventing a step or an expected result the AC and spec do not state | **HALT** with stop condition (a) — this is a readiness escape, not a test-writing problem |
| Red is **invalid** (as defined in `red-first.md`) | Fix the test or harness — minimal signatures only, no behavior — within `MAX_REPAIR_ATTEMPTS`; if still not valid red, **HALT** with (b) |
| The `[E2E]` AC is a **preservation** criterion (refactoring / reconcile: the existing flow must keep working) and an existing test already covers it, green | Red-first is n/a — record the exemption line from `red-first.md` and start the loop |
| The plan has **no** `[E2E]` AC (documentation-only, or it predates the requirement) | Nothing to do here — continue |

**Why the E2E test goes first, before any functional AC.** It is the criterion the functional ACs
add up to, and it is the one most likely to be quietly rewritten to fit whatever the fragments
produced. Placed red at the start, it is the only test in the run that no implementation could have
shaped. It stays red for most of the loop — that is expected, not a failure: it is the reference
signal the run is steering toward, and the run is not done until it goes green on its own.

Because the E2E test is red by design here, the baseline check in Step 0 is what establishes "all
other tests are green"; do not re-interpret the failing E2E test as a red baseline.

### Step 1: Pick the next AC

- From the plan, take the first `- [ ]` (unchecked) AC in order.
- Step 0b already cleared the whole set for readiness. If implementing it nonetheless reveals that
  the AC is ambiguous or under-specified (e.g. it reads as testable but two incompatible readings
  both satisfy it), **halt** with stop-condition (a). Do not guess the intent.
- If no unchecked AC remains, go to Step 4.

### Step 2a: Write the test for this AC and observe it red

**Before writing or reading implementation code for this AC**, follow
[`../run-tests/red-first.md`](../run-tests/red-first.md):

1. Transcribe the AC's given / when / then into a test, tagged with the AC-ID. Take them from the
   **AC text**, not from the code that happens to exist.
2. Run it and classify the failure (`run-tests`, red-first run — the criteria are in `red-first.md`):
   - **Valid red** → go to Step 2b.
   - **Invalid red** → the test measured nothing. Add the **minimal signature** the test names —
     no behavior — and re-run. This counts against `MAX_REPAIR_ATTEMPTS`; if it is still not valid
     red, **halt** with (b).
   - **Green on the first run** → stop and think before proceeding. Either the AC is already
     satisfied (record that, go to Step 3, and let Step 3b check the box — do not write code to have
     written code) or the test does not actually assert the AC. Rewriting the test to be *weaker* is
     never the resolution here; if you cannot tell the two apart, **halt** with (a).
3. Append the `red-first` line from `red-first.md` to the Decision Log **before** implementing.
   From that point the expectation is frozen: changing it is stop condition (c).

If the test cannot be written without deciding an expected result the AC does not state, **halt**
with stop-condition (a). That is a readiness escape (`R2` / `R3` slipped through Step 0b), and the
fix is a human rewriting the AC — not the driver choosing what "correct" means.

**For a `[E2E]` AC** the test already exists from Step 0c — do not write it again. Re-run it:

| Result | What it means | Next |
|--------|---------------|------|
| **Green** | The functional ACs added up: the through-flow now works. This is the run succeeding, not an anomaly — the "green on first run" branch above does **not** apply | Go to Step 3 (full verification), then Step 3b checks the box |
| **Still red, same reason as Step 0c** | The fragments do not yet add up — something in the flow is missing | Go to Step 2b and implement what connects them |
| **Red for a different reason** (no longer compiles, setup broke) | The test stopped measuring | Fix that first (counts against `MAX_REPAIR_ATTEMPTS`), then re-assess |

For a preservation AC covered by an existing green test, record the `n/a` exemption line and go to
Step 2b.

### Step 2b: Implement the AC

- Implement following the order guidance in `docs/04_implementation/patterns.md`
  (stable layer first), same as `start-feature` describes.
- Keep the change scoped to this AC. If satisfying it requires expanding scope or violating
  an invariant you cannot resolve within scope, **halt** with stop-condition (e).
- **Do not change the expectation of the test written in Step 2a** — its given / when / then are
  frozen. (Mechanical edits that leave all three identical — renaming, extracting a helper — are
  allowed, per `red-first.md`.) If the expectation itself now looks wrong, that is stop condition
  (c), not an edit to make in passing.

### Step 3: Verify

Run the verification skills. Note the two invocation modes (they differ by
`disable-model-invocation`):
- `run-tests` is model-invocable (`false`) — invoke it directly via the Skill tool.
- `check-invariants` / `check-doc-freshness` are non-invocable (`true`) — execute them by reading
  their `SKILL.md` and following the steps inline. Do not try to call them via the Skill tool; it
  is not exposed for them.

1. `run-tests` (invoke via the Skill tool)
   - **All green** -> continue to Step 3b.
   - **Only expected reds remain** (`run-tests` Step 2c — recorded red-first tests whose AC is still
     unchecked, typically the `[E2E]` test from Step 0c) -> this is the expected state for most of
     the loop. Treat the run as green for this AC and continue to Step 3b. `run-tests` reports these
     apart from failures and flags any whose failure reason changed; a changed reason is a real
     failure, so fix it (it counts against `MAX_REPAIR_ATTEMPTS`).
   - **Red because the implementation has a bug** (spec alignment gate option A): this is the
     normal inner-loop case. Fix the implementation and re-run. Count this attempt against
     `MAX_REPAIR_ATTEMPTS`.
   - **Red because the test's expectation must change** (spec alignment gate option B): a test
     change is an outer-gate action — **halt** with stop-condition (c). Never edit a test's
     expectation to match implementation behavior (INV-T01), and never weaken a test frozen in
     Step 0c / Step 2a to get past it.
   - **Still red after `MAX_REPAIR_ATTEMPTS`** -> **halt** with stop-condition (b).
   - **Green, but `run-tests` returns a hold on an uncovered `[E2E]` AC**: the tests that ran do
     not include one for the through-flow, so "green" does not mean the E2E criterion is met.
     This should be unreachable — Step 0c puts that test in place before the loop — so reaching it
     means Step 0c was skipped or its test was lost. **Halt** with stop-condition (a): write the
     E2E test at its proper time (before implementation, per `red-first.md`), not now, when
     anything you write would be shaped by the code that already exists.
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
| (a) | An AC is missing, ambiguous, or under-specified. Detected **before the loop** by the Step 0b readiness gate (any NOT READY criterion) and by Step 0c / Step 2a when its test cannot be transcribed without inventing an expected result, and as a backstop during the loop — including a `[E2E]` AC whose test does not exist, so `run-tests` holds | Deciding *what to build* (and what the through-flow is) is outer-gate (spec-first principle) |
| (b) | Tests still red after `MAX_REPAIR_ATTEMPTS` self-repair tries — including a red-first test that never reaches **valid red** | Repeated failure signals a real problem the human should see |
| (c) | A test's *expectation* must change to pass — including any change to an expectation frozen by a Step 0c / Step 2a red observation | Test changes must be grounded in a spec change (INV-T01 / INV-T02) |
| (d) | An irreversible / outward-facing action is next (create or push a PR, `promote-spec`, deleting tags) | Outward effects require human authorization |
| (e) | An INV violation cannot be resolved without expanding scope | Scope expansion is a planning decision, not execution |

If none apply, **keep going** — do not stop merely because progress feels "far enough" or to
ask for reassurance. (This is the "context anxiety" failure mode the loop exists to avoid.)

---

## Resume-state convention (file-based handoff)

So that a fresh session can resume from files alone (no conversation history), every loop
iteration records enough state in the plan itself:

- AC checkboxes (`- [x]`) are the canonical "what is done" marker.
- **Before** implementing each AC (Step 0c for `[E2E]` ACs, Step 2a for the rest), append the
  red observation — this is the freeze, and its position before the `done` entry is the evidence
  that the test was not written to fit the code:
  ```markdown
  ### YYYY-MM-DD
  - AC-NNN red-first: `<test file>::<test name>` を AC 本文から起草し、実行して赤を観測
    (expected: <…>, actual: <…>)。以降この期待値は凍結。
  ```
  (or the `n/a` exemption line from [`../run-tests/red-first.md`](../run-tests/red-first.md))
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
(spec alignment gate option A), in-scope invariant fixes that re-run verification, and attempts to
turn an **invalid red** into a valid one in Step 0c / Step 2a — not green re-verifications. When the
budget is exhausted, halt with stop-condition (b).

---

## Completion criteria

- [ ] Target plan selected and baseline confirmed green — expected reds aside (Step 0)
- [ ] AC readiness gate run over **every** unchecked AC before the loop, and its result recorded in
      the Decision Log (Step 0b)
- [ ] Every `[E2E]` AC had its test written and observed in **valid red** before the loop started,
      with the observation recorded (Step 0c) — or its exemption recorded
- [ ] Each processed AC went through write-the-failing-test -> implement -> run-tests ->
      check-invariants, and its `red-first` Decision Log entry precedes its `done` entry
- [ ] No test frozen by a red observation was edited to make it pass
- [ ] Every AC reached is either `- [x]` (green) or recorded as a HALT in the Decision Log
- [ ] Decision Log updated per the resume-state convention
- [ ] No PR was created by this skill (handoff to `pre-pr` only)

Final report output by the agent:

```
=== Autonomous run complete ===

Plan      : exec-plans/active/YYYY-MM-{name}.md
Readiness : ✅ {n} ACs READY (Step 0b)   |   ❌ AC-NNN NOT READY (R2) → loop not started
E2E red   : ✅ AC-NNN [E2E] → {test name} 赤で配置 (Step 0c)   |   n/a (no [E2E] AC)
Red-first : ✅ {n}/{n} ACs で赤を観測してから実装   |   ⚠️ AC-NNN n/a ({理由})
Processed : AC-001 ✅  AC-002 ✅  AC-003 ⏸ (HALT: stop condition c)  AC-004 …
Tests     : ✅ {n} passing
Stopped at: {none | AC-NNN, stop condition <id>: <reason>}

Next action: {run /pre-pr for the completed ACs | human decision needed for the HALT}
```
