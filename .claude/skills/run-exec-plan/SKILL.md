---
name: run-exec-plan
description: |
  Autonomous driver that implements an exec-plan's acceptance criteria one at a time
  without stopping for confirmation between criteria. Before the loop starts it gates on
  AC readiness (testability), so an untestable criterion stops the run before any code is
  written rather than mid-implementation, and puts the plan's [E2E] test in place as a failing
  test. For each unchecked AC it runs
  read the AC's sources (the US bullets and spec section its one line condenses) ->
  write the failing test -> implement -> run-tests -> check-invariants -> re-anchor to the spec
  section, and on green it checks the
  box, records a Decision Log entry, and moves to the next AC. When every AC is checked, it runs
  `docode-review` as a mandatory independent goal check before handing off to `pre-pr` — the
  self-implementing loop is the case that most needs an outside look, since the same agent wrote
  the code and the tests. Halts ONLY on explicit stop conditions
  (missing/ambiguous AC, tests still red after bounded retries, a test change required,
  an irreversible/outward action, an INV violation needing scope expansion, or the independent
  review requesting changes).
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
| **Inner loop — automate** | Read the AC's frozen sources, transcribe them into a test and observe it red, implement the AC, run tests, fix a failing test caused by an implementation bug, re-run, check the result against the AC's spec section, advance to the next AC, **invoke `docode-review` once every AC is `- [x]` (Step 4a — the call itself is automatic; interpreting a ❌ verdict is not, see below)** | **This skill (no confirmation)** |
| **Outer gate — never automate** | What to build (defining AC), **deciding an expected result neither the AC nor its sources state**, **choosing between two frozen documents that disagree**, changing a test's expectation once frozen, **deciding which `docode-review` findings to act on when Step 4a returns ❌**, modifying the spec, `promote-spec`, creating/pushing a PR | **Human (halt and ask)** |

Writing a test is on the inner-loop side **only in the transcription sense**: the given / when / then
come from material a human already froze — the AC line, plus the US bullets and spec section it
condenses (Step 1b, [`../create-exec-plan/ac-sources.md`](../create-exec-plan/ac-sources.md)) — and
readiness (`R2`) guarantees they are present in it. The moment the driver would have to *decide* an
expected result none of that material states, it is on the outer-gate side
and must halt — see [`../run-tests/red-first.md`](../run-tests/red-first.md).

The point of autonomy here is *not* "stop less". It is "stop **only** at the boundaries that
genuinely need a human, and never in the middle of executing a frozen AC."

---

## What this skill does

1. Select the active exec-plan, confirm baseline is green, gate on **AC readiness**
   (every unchecked AC is testable as written — otherwise halt before the loop starts), and put
   each `[E2E]` AC's test in place **as a failing test** before any AC is implemented
2. Loop over each unchecked AC:
   a. Read the AC's **sources** — the US bullets and spec section named in the plan's `## Sources`
   b. Write the test for this AC **first**, from the AC and its sources, and observe it fail (red-first)
   c. Implement the AC
   d. Run `run-tests` (spec alignment gate)
   e. Run `check-invariants` (and `check-doc-freshness`, advisory)
   f. **Re-anchor to the spec**: confirm the implemented behavior does what the AC's spec section
      describes — a green test set proves only what was transcribed into it
   g. On green: check the AC box, append a Decision Log entry, continue to the next AC
   h. On red: attempt a **bounded** self-repair (default 3 tries); if still red, **halt**
3. When all ACs are checked: run `docode-review` (**mandatory** — see Step 4) as an independent
   goal check before handing off to `pre-pr`. On ✅ or ⚠️, produce a summary and hand off. On ❌,
   **halt** with stop condition (f) — do not hand off. (If a stop condition fires before all ACs
   are checked, the loop stops there and this step does not run; `docode-review` stays optional on
   that path, same as any human-implemented plan)

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

`R2` is judged against the AC line **together with its sources**, so read the plan's `## Sources`
rows and open what they name before running the gate — the per-AC read in Step 1b comes too late to
inform a gate that must clear the whole set up front. Judging the one-liners alone would halt the
loop on ACs whose detail is correctly recorded in the US, which is not what NOT READY means. When a
row is `n/a` or the plan has no table, `R2` falls back to the AC line, as `ac-readiness.md` states.

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
following [`../run-tests/red-first.md`](../run-tests/red-first.md). Read its row in the plan's
`## Sources` first and open **whatever that row names** — 前提, 完了条件 and the journey are written
there in full, and the AC line is their one-line condensation:

| The `[E2E]` AC's source row names… | What to open |
|-----------------------------------|--------------|
| A spec `E2E-NNN` | `docs/02_spec/**` の `### E2E-NNN` シナリオ |
| `n/a（spec 未作成…）` with a US section — `/create-spec` was skipped for a small change | the US `## ゴール像` の主要ユーザージャーニー, which is what `create-exec-plan` derived the AC from |
| `n/a` for both, or the plan has no `## Sources` | Nothing to open — transcribe from the AC line alone and say so in the report |

Transcribe the through-flow from the AC text **and that material**, run it, and confirm
**valid red**. Record the
observation in the Decision Log; that entry freezes the expectation.

| Situation | Action |
|-----------|--------|
| Valid red observed for every `[E2E]` AC | Record it and start the loop |
| An earlier session already placed it (a recorded `red-first` entry, AC still `- [ ]`) | Re-run it, confirm the same red, and start the loop — do not rewrite the test |
| The through-flow cannot be transcribed without inventing a step or an expected result the AC and spec do not state | **HALT** with stop condition (a) — this is a readiness escape, not a test-writing problem |
| The source scenario or journey **contradicts** the `[E2E]` AC line (different 完了条件) | **HALT** with (a) — which one is the target is a spec judgement (`ac-sources.md`) |
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

### Step 1b: Read the AC's sources (before drafting its test)

The AC line is a **condensation** — `create-requirements` keeps the 2–5 checkable bullets in the US
file, and `create-spec` keeps the behavior in the spec section marked "satisfies AC-NNN". Steering
by the one line means steering by whatever the driver reads into it.

Open the AC's row in the plan's `## Sources` and read what it names. Follow
[`../create-exec-plan/ac-sources.md`](../create-exec-plan/ac-sources.md); do not re-derive the
admissible sources here. **Do not read implementation code for this AC** — the widened source set is
frozen spec material only, and reading the code would undo what Step 2a exists for.

| What you find | Action |
|---------------|--------|
| **Refinement** — the same outcome with concrete preconditions, boundaries or expected values | Use it. Step 2a transcribes at *that* granularity, not the one-liner's |
| **A separate outcome** the AC line does not cover | **HALT** with (a). Either the AC bundles several results (`R1`) or a criterion was never written; both are a human's call |
| **A contradiction** — the same outcome, a different expected value | **HALT** with (a). Do not pick a side, and do not edit the AC or the spec to agree |
| **One column** is `n/a（理由）` (typically spec, when `/create-spec` was skipped) | Read the other one. A partial `n/a` is not an exemption — the goal simply lives one layer up |
| **Both columns** are `n/a（理由）` | Nothing to read. The AC line is the whole goal — go to Step 2a |
| The plan has **no** `## Sources` table (it predates the convention) | Continue, and say so in the run's report. Do not reconstruct sources by reading the code — that is the one reading this step forbids |

Reading is execution; resolving a disagreement between two frozen documents is governance. That is
why the two conflict rows halt instead of choosing.

### Step 2a: Write the test for this AC and observe it red

**Before writing or reading implementation code for this AC**, follow
[`../run-tests/red-first.md`](../run-tests/red-first.md):

1. Transcribe the AC's given / when / then into a test, tagged with the AC-ID. Take them from the
   **AC text and the sources read in Step 1b**, not from the code that happens to exist.
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

**If an earlier session already placed this test** — the Decision Log has an `AC-NNN red-first:`
entry and the AC is still `- [ ]` — do **not** write it again. Re-run it, confirm the same red, and
go to Step 2b. Rewriting it would author a new expectation over a frozen one, which is (c). (Same
rule as the resumed-`[E2E]` row in Step 0c.) If it now fails for a *different* reason, it has
stopped measuring: fix that first, counting against `MAX_REPAIR_ATTEMPTS`.

If the test cannot be written without deciding an expected result **neither the AC nor its sources**
state, **halt** with stop-condition (a). That is a readiness escape (`R2` / `R3` slipped through
Step 0b), and the fix is a human rewriting the AC — not the driver choosing what "correct" means.
Note the bar moved with Step 1b: an expected result that is missing from the one-liner but present
in the US bullets is *transcription*, not invention, and does not halt.

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

The four items run **in order**, and Step 3b is reached only through item 4 — a green test run is
not by itself permission to check the box.

1. `run-tests` (invoke via the Skill tool)
   - **All green** -> continue to item 2.
   - **Only expected reds remain** (`run-tests` Step 2c — recorded red-first tests whose AC is still
     unchecked, typically the `[E2E]` test from Step 0c) -> this is the expected state for most of
     the loop. Treat the run as green for this AC and continue to item 2.
     **An expected red belonging to the AC being processed right now does not qualify.** Its box is
     about to be checked, so its own measurement must be green — including any test added during
     Step 3a, which is recorded red-first against this same still-unchecked AC and would otherwise
     read as "expected". Only *other* ACs' pending reds are expected here. `run-tests` reports these
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
4. **Spec re-anchor** — see below. Run it after the tests are green, before Step 3b.

#### Step 3a: Spec re-anchor (before the box is checked)

Green tests prove the expectations that were *transcribed* hold. They cannot prove the
implementation does what the spec section describes: the tests are bounded by what Step 2a wrote
down, and the transcription may have condensed something. `create-spec` records
`AC → spec → code` traceability precisely so it can be read back here — without this step it is
traceability on paper only.

Open what this AC's `## Sources` row names — the spec section, or the US bullets when the spec
column is `n/a` because `/create-spec` was skipped (the selection table is in
[`../create-exec-plan/ac-sources.md`](../create-exec-plan/ac-sources.md); "no spec section" is not
the same as "no re-anchor"). Ask **"does the behavior now
implemented do what this material describes for this AC?"** — not "did the tests pass" (already
known) and not "does the code look right". Take the verdict from the table in that file; the loop's
actions are:

| Verdict | Action in the loop |
|---------|--------------------|
| **一致** | Go to Step 3b and check the box |
| **spec の振る舞いを満たしていない** | Implementation gap the transcribed tests missed. Fix and re-run Step 3. Counts against `MAX_REPAIR_ATTEMPTS`; if exhausted, **halt** with (b) |
| **spec が述べる振る舞いに対応するテストが無い** | Measurement gap. Add a **new** test for it red-first (Step 2a's procedure), then implement to green. Counts against `MAX_REPAIR_ATTEMPTS`. Never edit or weaken a frozen test to cover the gap — that is (c) |
| **spec が AC 行と矛盾** | **Halt** with (a). Change neither side |
| **The missing behavior is a separate outcome, not part of this AC** | **Halt** with (a) — same row as Step 1b's "separate outcome" |
| **起点なし** — both columns `n/a`, or the plan has no `## Sources` table | Nothing to anchor to. Record `spec 再アンカー: n/a（{理由}）` and go to Step 3b |

**Scope the comparison to this AC.** A spec section — and an `E2E-NNN` scenario in particular —
usually names several ACs (`満たす AC: AC-001, AC-003, AC-005`). Behavior it attributes to an AC
outside this plan, or to one still unchecked, is **not** a gap in the AC being verified: note it and
continue. Without this, the re-anchor of the last `[E2E]` AC would halt at the moment the run
succeeded, because the scenario always describes more than any single criterion.

This step reads documents and compares them with behavior. It never edits the spec: if the spec
looks wrong, that is a spec change — outer gate, stop condition (a).

**Step 3b — on green:**
- Change the AC's `- [ ]` to `- [x]` in the plan.
- Append a Decision Log entry **including the re-anchor result** (see "Resume-state convention" below).
- Return to Step 1 **without asking the user**.

### Step 4: Finish the loop

When a stop condition fired before every AC was checked, stop the loop and report (see format
below) — Step 4a does not run on this path. `docode-review` remains optional here, same as any
plan a human is implementing (`start-feature` path): the loop did not reach an unattended
completion, so there is nothing for the mandatory gate to guard yet.

When every AC is `- [x]`, continue to **Step 4a** before reporting.

#### Step 4a: Mandatory independent review (self-implementing completion only)

This is the one point in the loop where the implementer and the verifier are the same agent from
start to finish — every AC, every test, every re-anchor was judged by the driver against its own
work. `docode-review` exists precisely to catch what a self-reviewer cannot: run it now, via the
`Skill` tool (`docode-review` is model-invocable), **before** reporting completion or handing off
to `pre-pr`.

- Collect context exactly as `docode-review`'s own Step 1 describes (diff, this plan's `## Sources`
  and the sections they name) and launch it. Do not skip its independent-subagent design by
  reviewing the diff yourself instead — that would defeat the reason this step exists.
- Append the verdict to this plan's `## Decision Log`:
  ```markdown
  ### YYYY-MM-DD
  - docode-review (Step 4a): verdict {✅ Approved | ⚠️ Approved with suggestions | ❌ Changes requested}.
    {one-line summary of the findings, or "no findings"}.
  ```

| Verdict | Action |
|---------|--------|
| ✅ Approved | Continue to reporting; hand off to `pre-pr` |
| ⚠️ Approved with suggestions | Continue to reporting; hand off to `pre-pr`. Mention the suggestions in the summary so the human sees them at handoff, even though they do not block it |
| ❌ Changes requested | **Halt** with stop condition (f). Surface the findings verbatim. Do **not** attempt to fix them yourself and re-run — deciding which findings to act on (and how) is the same governance judgment as rewriting an AC, and this gate exists so a human makes it, not the agent that just finished implementing |

**Do not call it twice to produce one report.** "Same pass" means: no new tool call boundary, no new
message from the user, and no gap in which the human could have changed the repo — i.e., you are
still inside the single execution that just produced this verdict, about to write it into the final
report. Anything else (a new invocation of this skill, a later turn, a session that re-reads the
plan from disk) is a **resumed session** under the rule below, even if it feels like "continuing the
same conversation" — the file is the only thing that can be trusted to reflect the current diff.

**On a resumed session, always run it fresh — never reuse a recorded verdict.** A `docode-review
(Step 4a):` entry from an earlier session is evidence about the diff *as it was then*, not now. Two
concrete ways the diff can have moved since that entry, neither of which touches an AC checkbox:
a human made fixes after a ❌ halt without reopening any AC, or a reconcile plan reopened and
re-completed different ACs in a later session. Either way, `- [x]` on every AC no longer implies
"the diff `docode-review` last saw is the diff sitting here now" — so re-run it and append a new
entry rather than trusting the old one. (A stale ❌ is not a shortcut to skip re-review, either: if
the human wants to proceed past it, that happens by getting a fresh ✅/⚠️ or by the human directly
overriding the halt, not by the driver reasoning "it was already reviewed.")

When all ACs are `- [x]` (and, on this path, Step 4a's verdict is ✅ or ⚠️), stop the loop and report
(see format below). **Do not create a PR.** Hand off to `pre-pr` as a separate, human-reviewed step.

---

## Stop conditions (halt and ask the human)

The driver continues autonomously **except** in these cases. When one fires, stop, write the
current state to the Decision Log, and surface a concise summary to the user.

| ID | Condition | Why it is a human decision |
|----|-----------|----------------------------|
| (a) | An AC is missing, ambiguous, or under-specified. Detected **before the loop** by the Step 0b readiness gate (any NOT READY criterion); by Step 0c / Step 2a when its test cannot be transcribed without inventing an expected result; by **Step 1b** when a source states a separate outcome or contradicts the AC line; by **Step 3a** when the spec section contradicts the AC; and as a backstop during the loop — including a `[E2E]` AC whose test does not exist, so `run-tests` holds | Deciding *what to build* (and what the through-flow is) is outer-gate (spec-first principle). Choosing between two frozen documents that disagree is the same decision |
| (b) | Tests still red after `MAX_REPAIR_ATTEMPTS` self-repair tries — including a red-first test that never reaches **valid red** | Repeated failure signals a real problem the human should see |
| (c) | A test's *expectation* must change to pass — including any change to an expectation frozen by a Step 0c / Step 2a red observation | Test changes must be grounded in a spec change (INV-T01 / INV-T02) |
| (d) | An irreversible / outward-facing action is next (create or push a PR, `promote-spec`, deleting tags) | Outward effects require human authorization |
| (e) | An INV violation cannot be resolved without expanding scope | Scope expansion is a planning decision, not execution |
| (f) | `docode-review` (Step 4a), run mandatorily once every AC is `- [x]`, returns ❌ Changes requested | Deciding which findings to act on — and how — is the same governance judgment as rewriting an AC; the driver that just finished implementing is the one party who cannot make it objectively |

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
  - AC-NNN red-first: `<test file>::<test name>` を AC 行と起点（`## Sources`）から起草し、実行して赤を観測
    (expected: <…>, actual: <…>)。以降この期待値は凍結。
  ```
  (or the `n/a` exemption line from [`../run-tests/red-first.md`](../run-tests/red-first.md))
- After each completed AC, append to `## Decision Log` — the re-anchor line is part of the entry,
  not an optional extra, because it is the only record that Step 3a happened:
  ```markdown
  ### YYYY-MM-DD
  - AC-NNN done. <one line: what was implemented + key files>. Tests green ({n} passing).
    spec 再アンカー: `<spec ファイル>` §「<節>」と照合し一致。
  ```
  (or `spec 再アンカー: n/a（起点なし — <理由>）`)
- On any halt, append:
  ```markdown
  ### YYYY-MM-DD
  - HALT at AC-NNN (stop condition <id>). <what is blocking> <what the human must decide>.
  ```

A new session resuming this plan must be able to continue using only the checkboxes and the
Decision Log — never assume the prior conversation is available.

## Retry budget

`MAX_REPAIR_ATTEMPTS` defaults to **3** per AC. Counts implementation-bug repair attempts
(spec alignment gate option A), in-scope invariant fixes that re-run verification, attempts to
turn an **invalid red** into a valid one in Step 0c / Step 2a, and fixes prompted by the Step 3a
re-anchor (an implementation gap, or a missing test added red-first) — not green re-verifications.
When the budget is exhausted, halt with stop-condition (b).

---

## Completion criteria

- [ ] Target plan selected and baseline confirmed green — expected reds aside (Step 0)
- [ ] AC readiness gate run over **every** unchecked AC before the loop, and its result recorded in
      the Decision Log (Step 0b)
- [ ] Every `[E2E]` AC had its test written and observed in **valid red** before the loop started,
      with the observation recorded (Step 0c) — or its exemption recorded
- [ ] Each processed AC went through read-the-sources -> write-the-failing-test -> implement ->
      run-tests -> check-invariants -> spec re-anchor, and its `red-first` Decision Log entry
      precedes its `done` entry
- [ ] Every processed AC's `done` entry carries a `spec 再アンカー:` line — the section it was
      checked against, or an explicit `n/a（理由）`
- [ ] No test frozen by a red observation was edited to make it pass
- [ ] Every AC reached is either `- [x]` (green) or recorded as a HALT in the Decision Log
- [ ] Decision Log updated per the resume-state convention
- [ ] **If every AC reached `- [x]`**: `docode-review` was run (Step 4a) via the `Skill` tool and its
      verdict recorded in the Decision Log **before** handoff; a ❌ verdict halted with stop
      condition (f) instead of handing off (a run that stopped early on another stop condition does
      not need this — `docode-review` stays optional there)
- [ ] No PR was created by this skill (handoff to `pre-pr` only)

Final report output by the agent:

```
=== Autonomous run complete ===

Plan      : exec-plans/active/YYYY-MM-{name}.md
Readiness : ✅ {n} ACs READY (Step 0b)   |   ❌ AC-NNN NOT READY (R2) → loop not started
E2E red   : ✅ AC-NNN [E2E] → {test name} 赤で配置 (Step 0c)   |   n/a (no [E2E] AC)
Sources   : ✅ {n}/{n} AC の起点を読んでから起草 (Step 1b)   |   ⚠️ プランに ## Sources が無い
Red-first : ✅ {n}/{n} ACs で赤を観測してから実装   |   ⚠️ AC-NNN n/a ({理由})
再アンカー: ✅ {n}/{n} AC を spec 該当節と照合 (Step 3a)   |   ➖ n/a ({理由})
Processed : AC-001 ✅  AC-002 ✅  AC-003 ⏸ (HALT: stop condition c)  AC-004 …
Tests     : ✅ {n} passing
docode-review (Step 4a): ✅ Approved | ⚠️ Approved with suggestions | ❌ Changes requested → HALT (f)
                         | n/a (loop stopped before every AC was checked — see Stopped at)
Stopped at: {none | AC-NNN, stop condition <id>: <reason>}

Next action: {run /pre-pr for the completed ACs | human decision needed for the HALT}
```
