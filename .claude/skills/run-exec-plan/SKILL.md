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
  `docode-review` as a mandatory independent goal check before the pre-PR check — the
  self-implementing loop is the case that most needs an outside look, since the same agent wrote
  the code and the tests. Halts ONLY on explicit stop conditions
  (missing/ambiguous AC, tests still red after bounded retries, a test change required,
  an irreversible/outward action, an INV violation needing scope expansion, or the independent
  review requesting a change that needs a human's judgement). A question that arises before any code
  for an AC holds that AC and lets the unrelated ones go on, so the questions reach the human
  together; review findings the reviewer classified as implementation errors or missing tests are
  repaired by the driver under a fresh review, at most twice.
  One invocation covers the whole autonomous path: it prepares the run itself (what start-feature
  does on the manual path — plan, branch, baseline, readiness, sources, start record), and after the
  review it runs the pre-PR check. Only when the human says so at invocation ("PR まで") does it then
  push the branch and open a draft PR; merging, the human's confirmation and completion stay human.
  Opt-in: runs only when the user explicitly invokes it; default behavior is unchanged.
disable-model-invocation: true
---

# Skill: Run Execution Plan (Autonomous Driver)

> **When to run**: When the user explicitly wants the agent to implement an exec-plan's
> acceptance criteria autonomously, without being asked to confirm between each AC.
>
> **Purpose**: Provide the missing "Generator" / inner loop of DocDD. Automate only the
> **execution** of work whose spec (AC) is already frozen — implement, verify, self-repair,
> advance — while leaving every **governance** decision to the human. This reduces the
> mid-implementation stops a manual chain of skills incurs, without dissolving DocDD's spec gates.
>
> **Prerequisites**:
> - An active plan must exist in `exec-plans/active/` with at least one `AC-NNN:` defined. A plan
>   this branch already completed (moved to `exec-plans/completed/` by its complete commit) is not
>   picked up from there: reopening it withdraws the human's confirmation, so the human reopens it
>   first ([`../complete-exec-plan/completion-boundary.md`](../complete-exec-plan/completion-boundary.md)
>   「Reopening before the merge」)
> - `start-feature` is **not** needed first: Step 0 prepares the run itself. `start-feature` is the
>   manual path, where a human present resolves in conversation what this skill halts on. Running it
>   first does no harm — Step 0 finds its records and does not repeat them
> - `docs/05_quality/test_strategy.md` must have `test_command` set (used by `run-tests`)

---

## Design principle (read first)

This skill automates the **inner loop only**. It must never make a **governance** decision
on the human's behalf.

| Layer | Examples | Who decides |
|-------|----------|-------------|
| **Inner loop — automate** | Prepare the run (Step 0: plan, branch, baseline, readiness, sources, start record), read the AC's frozen sources, transcribe them into a test and observe it red, implement the AC, run tests, fix a failing test caused by an implementation bug, re-run, check the result against the AC's spec section, advance to the next AC, **invoke `docode-review` once every AC is `- [x]` (Step 4a — the call itself is automatic; interpreting a ❌ verdict is not, see below)**, then the pre-PR check (Step 4b) | **This skill (no confirmation)** |
| **Outer gate — never automate** | What to build (defining AC), **deciding an expected result neither the AC nor its sources state**, **choosing between two frozen documents that disagree**, changing a test's expectation once frozen, **deciding which `docode-review` findings to act on when Step 4a returns ❌**, modifying the spec, `promote-spec`, creating/pushing a PR — **unless the human asked for it when invoking this run** (「PR まで」: Step 4c pushes the branch and opens a draft PR, nothing more), the human's confirmation of every AC, completion, merging | **Human (halt and ask)** |

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

1. Prepare the run (Step 0): select the active exec-plan — a plan **deferred** until a promotion is
   not started at all — put the work on a branch of its own, confirm baseline is green, gate on
   **AC readiness**
   (every unchecked AC is testable as written — otherwise halt before the loop starts), and put
   each `[E2E]` AC's test in place **as a failing test** before any AC is implemented, and record the
   start
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
3. When all ACs are checked: sweep the whole branch with the checks that can rewrite files, then run
   `docode-review` (**mandatory** — see Step 4) as an independent goal check. On ❌, **halt** with
   stop condition (f). On ✅ or ⚠️, run the pre-PR check (`pre-pr`, Step 4b) on the diff the review
   saw; if the human asked for it at invocation and the check has no ❌, push and open a **draft** PR
   (Step 4c). (If a stop condition fires before all ACs are checked, the loop stops there and this
   step does not run; `docode-review` stays optional on that path, same as any human-implemented
   plan)

---

## Steps

### Step 0: Preconditions and preparation

Step 0 is the preparation `start-feature` does on the manual path, with this skill's actions on a
finding: where `start-feature` asks the human present, this step halts (or, for a deferral, does not
start). The two paths apply the same single sources; only the action differs.

- **If `exec-plans/active/` has no plan**, say so and end: propose `create-exec-plan` — or, when the
  work fixes a plan this branch already completed, reopening it, which is the human's call
  ([`../complete-exec-plan/completion-boundary.md`](../complete-exec-plan/completion-boundary.md)
  「Reopening before the merge」). Nothing is written.
- Confirm exactly one target plan. If the current branch already implements a different plan (it
  ticked that plan's ACs or changed code for it), stop and say so: one implemented plan per branch
  ([`../complete-exec-plan/completion-boundary.md`](../complete-exec-plan/completion-boundary.md)
  「When part of a plan has to merge before the rest」) — the user switches branches.
  If several active plans exist, ask the user which one
  (this is plan *selection*, an outer-gate choice — confirm it once, up front).
- **If the plan awaits its bundled approval, do not start.** A plan with a `- 一括承認:` bullet whose
  definition PR is not merged yet — the plan file, or a document the bullet names, is not on `main`
  as it is here (`git diff --quiet origin/main -- <the plan and those documents>` fails) — was written
  on its definition branch and is approved, and frozen, only at that merge
  ([`../create-spec/bundled-approval.md`](../create-spec/bundled-approval.md)). Implementing it there
  would mix the definitions with their implementation in one branch. Report it and end, writing
  nothing; the implementation starts from `main` after the merge.
- **If the plan is deferred, do not start.** A plan whose Decision Log has a bullet beginning
  `- deferred: spec/` with no later bullet beginning `- deferred 解除:` is waiting on a promotion
  ([`../create-spec/e2e-interaction.md`](../create-spec/e2e-interaction.md)「Deferring a plan, and
  lifting it」). Report it with that line and end — before the baseline, the readiness gate and the
  comparison, and **without appending a HALT entry**. The finding it waits on is still on `main`, so
  running Step 0b would only find it again and record the same HALT on every resume; the deferral is
  already the record. Lifting it is the human's.
- **Put the work on a branch of its own.** If the current branch is the default branch (`main`),
  create and switch to `feature/{plan name}` (or the pattern the project's CONTEXT.md「branch
  strategy」 sets). A local branch is not an outward action. On any other branch, the
  one-plan-per-branch check above has already decided it is this plan's.
- Load `docs/07_ai_context/CONTEXT.md` and `docs/04_implementation/invariants.md` (where they exist)
  — the development rules and the invariants `check-invariants` holds every AC to.
- Run `run-tests` as a baseline. If baseline is already red, **halt** — do not start a loop
  on a red baseline (you could not attribute failures to your own changes).
  **Expected reds do not count as a red baseline.** When resuming a partly-done plan, the tests
  frozen red by an earlier session (`run-tests` Step 2c: a recorded `AC-NNN red-first:` entry whose
  AC is still `- [ ]`) are the reference signal this run is steering toward, not breakage. Baseline
  is green when everything *else* passes. Any other failure still halts.
- **Run the AC readiness gate** (below) over every unchecked AC.
- **Put every `[E2E]` AC's test in place as a failing test** (Step 0c below).
- **Record the start** (Step 0d below).
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
A row that names something that **cannot be opened** is not `n/a` and gets no fallback: that AC is
NOT READY, and the run halts with (a) — see
[`../create-exec-plan/ac-sources.md`](../create-exec-plan/ac-sources.md)「When a source cannot be
opened」. The same holds for a row that names **background material** — anything
`ac-sources.md`「What counts as a source」 does not class as a source, such as a research note, an
ADR, another plan's Decision Log or a design document — instead of a source (`ac-sources.md`「When
a row names background material」).

While the sources are open, run **complement detection** on every row that names an `E2E-NNN`:
compare the scenario against the **comparison set** that
[`../create-spec/e2e-interaction.md`](../create-spec/e2e-interaction.md) defines (take its scope from
there — it is wider than this row). An outcome the scenario states and the comparison set states
nowhere is a detected requirements gap, and a contradiction is two frozen documents disagreeing —
either one halts with (a) before the loop starts, recorded in that file's HALT format. Refinement
passes. A plan with no `E2E 凍結` record in its Decision Log (it predates the convention, was
hand-written, or was generated by `promote-spec`) is not a halt by itself; the comparison is simply
done here.

| Verdict | Action |
|---------|--------|
| All READY, and complement detection found nothing | Start the loop |
| ⚠️ (R3 / R4 unmet) **and the reason is already in the plan's Decision Log**, and complement detection found nothing | Start the loop |
| Complement detection found a gap or a contradiction (any AC) | **Do not start the loop.** Halt with stop condition (a), in `e2e-interaction.md`'s HALT format |
| The comparison set could not be assembled — a US under `由来ジャーニー` has no goal image, a `満たす AC` entry no US defines (`e2e-interaction.md`「Where this is applied」: no fallback at a gate) | **Do not start the loop.** Halt with (a), naming the missing member |
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
| An `E2E-NNN` scenario | the file the row names — `docs/01-02_e2e/E2E-NNN_*.md`, or in a project not yet migrated, `docs/02_spec/**` の `### E2E-NNN` |
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
| Complement detection (`../create-spec/e2e-interaction.md` — a gap or a contradiction against its comparison set, or a set that cannot be assembled) fires here, missed by Step 0b | **HALT** with (a) — complement detection (`../create-spec/e2e-interaction.md`). Do not transcribe the gap into the test |
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

#### Step 0d: Record the start

Once Step 0b has cleared and Step 0c has placed the `[E2E]` tests, append to the plan's
`## Progress Log` — unless a start record for this branch is already there (`start-feature` ran first,
or this is a resumed run):

```markdown
### YYYY-MM-DD
- Implementation started. Branch: feature/{name}（run-exec-plan）
```

### Step 1: Pick the next AC

- From the plan, take the first `- [ ]` (unchecked) AC in order **that this run has not held, and that
  is not waiting on a held AC** (「Holding an AC」 below). An `[E2E]` AC waits while any AC is held:
  it is not checked this run, even if its test goes green, because the held AC's answer can change
  the flow.
- Step 0b already cleared the whole set for readiness. If implementing it nonetheless reveals that
  the AC is ambiguous or under-specified (e.g. it reads as testable but two incompatible readings
  both satisfy it), **halt** with stop-condition (a). Do not guess the intent.
- If no unchecked AC remains, go to Step 4.
- If unchecked ACs remain but every one is held or waiting, the run cannot go further: halt with
  stop condition (a) and put **every held question together** to the human (「Holding an AC」).
  Step 4 does not run — the independent review waits until every AC is done.

#### Holding an AC (stop condition (a) before any code for it)

A halt in the middle of the loop used to stop everything on the first question, and the human came
back once per question. When the question arises **before any code for the AC exists**, nothing has
been built that the answer could invalidate, so the run can hold that AC, finish the ones the answer
cannot affect, and ask everything at once.

| Holdable | Not holdable — halt the whole run, as before |
|----------|---------------------------------------------|
| Stop condition **(a)** fired at **Step 1b** (reading the sources) or **Step 2a** (drafting the test) for a **functional** AC — before its `red-first` entry and before any implementation code for it | Step 0b / 0c (the whole-plan gates: their questions are already asked together, before the loop); Step 3a (code exists); any `[E2E]` AC (it is the run's reference signal); stop conditions (b), (c), (d), (e), (f) |

**Which ACs wait with it.** An unchecked AC is **related** to the held one, and waits with it, when
its sources name the same US `AC-NNN` section, the same spec section or the same scenario step as the
held AC, or the section the finding is about; when it builds on the held AC's outcome (it comes after
it in the through-flow and uses what it produces); or when the answer to the held question could
change what it must do. **If you cannot tell whether an AC is related, stop the whole run** with (a)
as before — a hold is an optimization, and guessing wrong would build on an answer nobody gave.

**Record each hold** as a Decision Log bullet that begins at the start of the line:

```markdown
- 保留: AC-003（停止条件 (a)、Step 1b）— <決めてほしいこと、製品の言葉で>。関連して待つ AC: AC-004
```

`保留:` is not `deferred:` (a plan waiting for a promotion, which stops the run at Step 0) and not
`reconcile: deferred` — it names one AC in one run. **A hold is not carried to the next run as state.**
A new run re-attempts every held AC from Step 1b, through the same checks: nothing was frozen for it
(the hold comes before its `red-first` entry), so reading its sources and drafting its test again is
not overwriting anything. If the human has decided — the AC rewritten, the document fixed on `main`,
the AC withdrawn — the checks pass and it proceeds; if not, the same finding fires and it is held
again (append a new bullet only if the question changed). No release marker is needed, so none can
be forgotten.

**When the run can go no further**, append the HALT entry naming every hold, and put the questions
to the human together, in through-flow order, each as a decision request
([`decision-requests.md`](decision-requests.md)). If the run ends on another stop condition while
holds exist, the presentation carries both.

### Step 1b: Read the AC's sources (before drafting its test)

The AC line is a **condensation** — `create-requirements` keeps the 2–5 checkable bullets in the US
file, and `create-spec` keeps the behavior in the spec section marked "satisfies AC-NNN". Steering
by the one line means steering by whatever the driver reads into it.

Open the AC's row in the plan's `## Sources` and read what it names. Follow
[`../create-exec-plan/ac-sources.md`](../create-exec-plan/ac-sources.md); do not re-derive the
admissible sources here. **Do not read implementation code for this AC** — nor, for drafting it,
the design and other docs from `docs/03_design/**` down, which that file classes as not read — the
widened source set is frozen spec material only, and reading the code would undo what Step 2a exists
for.

| What you find | Action |
|---------------|--------|
| **Refinement** — the same outcome with concrete preconditions, boundaries or expected values | Use it. Step 2a transcribes at *that* granularity, not the one-liner's |
| **A separate outcome** the AC line does not cover | **HALT** with (a). Either the AC bundles several results (`R1`) or a criterion was never written; both are a human's call |
| **A contradiction** — the same outcome, a different expected value | **HALT** with (a). Do not pick a side, and do not edit the AC or the spec to agree |
| The row names an `E2E-NNN` and complement detection finds a gap or a contradiction against its comparison set, or the set cannot be assembled (Step 0b missed it) | **HALT** with (a), per [`../create-spec/e2e-interaction.md`](../create-spec/e2e-interaction.md) |
| An expected result appears only in **background material** (a research note, an ADR) | Not a source. Drafting it would be deciding it — **HALT** with (a) (`ac-sources.md`「What counts as a source」) |
| The row names a file or section that **cannot be opened** | **HALT** with (a). It is not the `n/a` rows below — do not draft from the AC line alone, and do not guess which file the row meant (`ac-sources.md`「When a source cannot be opened」) |
| **One column** is `n/a（理由）` (typically spec, when `/create-spec` was skipped) | Read the other one. A partial `n/a` is not an exemption — the goal simply lives one layer up |
| **Both columns** are `n/a（理由）` | Nothing to read. The AC line is the whole goal — go to Step 2a |
| The plan has **no** `## Sources` table (it predates the convention) | Continue, and say so in the run's report. Do not reconstruct sources by reading the code — that is the one reading this step forbids |

For a functional AC, a (a) here — before any code for it — **holds** the AC instead of stopping the
run, when the remaining ACs can go on without it (「Holding an AC」, Step 1).

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
Before any code for the AC exists, that (a) holds the AC rather than stopping the run (「Holding an
AC」, Step 1).
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
| **Complement detection fires on the `E2E-NNN` being re-anchored against** — a gap or a contradiction against the comparison set, or a set that cannot be assembled (missed by Step 0b) | **Halt** with (a), per [`../create-spec/e2e-interaction.md`](../create-spec/e2e-interaction.md). Not a measurement gap — adding a test for it would turn an undecided requirement into a frozen one. If the `[E2E]` test frozen at Step 0c already holds the gap, the human's decision may change that expectation — stop condition (c) (that file's「Known gaps」) |
| **起点が開けない** — the row names a file or section that cannot be opened | **Halt** with (a). Not the `n/a` row below |
| **起点なし** — both columns `n/a`, or the plan has no `## Sources` table | Nothing to anchor to. Record `spec 再アンカー: n/a（{理由}）` and go to Step 3b |

**Scope the comparison to this AC.** A spec section — and an `E2E-NNN` scenario in particular —
usually names several ACs (`満たす AC: AC-001, AC-003, AC-005`). Behavior it attributes to an AC
outside this plan, or to one still unchecked, is **not** a gap in the AC being verified: note it and
continue. Without this, the re-anchor of the last `[E2E]` AC would halt at the moment the run
succeeded, because the scenario always describes more than any single criterion.

This step reads documents and compares them with behavior. It never edits the spec: if the spec
looks wrong, that is a spec change — outer gate, stop condition (a).

**Step 3b — on green:**
- **If this AC requires a process walkthrough** (a plan that changes a loop, a gate, a resumable
  run, an exemption, or a rule other rules consume — `create-exec-plan` Q3e placed the AC), walk the
  laps now and record them, per
  [`../create-exec-plan/process-walkthrough.md`](../create-exec-plan/process-walkthrough.md). On
  this path the driver **is** the implementer CLAUDE.md's 措置表 assigns that duty to, and an
  unrecorded walkthrough counts as not performed. A lap finding the plan cannot fix without widening
  its scope is stop condition (e). **If a lap finding was fixed here, return to Step 3** before
  checking the box — a lap fix edits process documents after Step 3's verification already ran, and
  it is the one part of Step 3b that can dirty the tree. That re-entry does **not** count against
  `MAX_REPAIR_ATTEMPTS`: it is a document edit, not a test repair, and counting it would halt with
  (b) on a lap that worked.
- Change the AC's `- [ ]` to `- [x]` in the plan.
- Append a Decision Log entry **including the re-anchor result** (see "Resume-state convention" below).
- Return to Step 1 **without asking the user**.

### Step 4: Finish the loop

When a stop condition fired before every AC was checked, stop the loop and report (see format
below) — Step 4a does not run on this path. `docode-review` remains optional here, same as any
plan a human is implementing (`start-feature` path): the loop did not reach an unattended
completion, so there is nothing for the mandatory gate to guard yet.

When every AC is `- [x]`, the run finishes in this order — **sweep → Step 4a → Step 4b → Step 4c**:

1. **Sweep** (before the review): run the two checks that may rewrite files over the **whole
   branch**, not one AC — `check-invariants` and `check-doc-freshness`, inline (they are `pre-pr` ①
   and ②). Fix what is in scope and re-run `run-tests` after any fix (in-scope fixes count against
   `MAX_REPAIR_ATTEMPTS`, as in Step 3; a fix needing scope expansion is (e)). Per-AC Step 3 already
   ran them, so the sweep usually finds nothing; it exists so the diff `docode-review` judges is the
   diff that is handed off.
2. **Step 4a** — the mandatory independent review, below.
3. **Step 4b** — the pre-PR check, below. It runs after the review and **changes nothing the review
   saw**.
4. **Step 4c** — the draft PR, only when the human asked for it at invocation.

Why this order: `pre-pr` ① and ② can rewrite code and documents. Run after the review, they would
hand off a diff the review never saw; run before it, they are part of what is reviewed.

#### Step 4a: Mandatory independent review (self-implementing completion only)

This is the one point in the loop where the implementer and the verifier are the same agent from
start to finish — every AC, every test, every re-anchor was judged by the driver against its own
work. `docode-review` exists precisely to catch what a self-reviewer cannot: run it now, via the
`Skill` tool (`docode-review` is model-invocable), **before** reporting completion or running the
pre-PR check (Step 4b).

- Collect context exactly as `docode-review`'s own Step 1 describes — read that step rather than
  this summary, which is illustrative and will fall behind it. At minimum it covers the diff, this
  plan's `## Sources` and the sections they name, and — when the plan changed a documented process —
  the **referrers** its dependency-backflow lap needs. Then launch it. Do not skip its
  independent-subagent design by reviewing the diff yourself instead — that would defeat the reason
  this step exists.
- Append the verdict to this plan's `## Decision Log`:
  ```markdown
  ### YYYY-MM-DD
  - docode-review (Step 4a): verdict {✅ Approved | ⚠️ Approved with suggestions | ❌ Changes requested}.
    {one-line summary of the findings, or "no findings"}.
    {for ❌: 分類: 実装の誤り {n} / テストの不足 {n} / 人の判断が要る {n} → 自己修正 {k}/2 回目 | → HALT (f)}
  ```

| Verdict | Action |
|---------|--------|
| ✅ Approved | Go to Step 4b |
| ⚠️ Approved with suggestions | Go to Step 4b. Mention the suggestions in the report (and in the draft PR's body, Step 4c) so the human sees them, even though they do not block |
| ❌ with **any** finding of kind `人の判断が要る` (or a finding with no kind) | **Halt** with stop condition (f). Surface every finding verbatim, and put the `人の判断が要る` ones to the human as decision requests ([`decision-requests.md`](decision-requests.md)). Do not fix the others first: the human's answer can change what they should be |
| ❌ with only `実装の誤り` / `テストの不足`, and this is the 1st or 2nd ❌ in the current window (below) | **Self-repair**, then a **new** review — 「Self-repair after a ❌ review」 below |
| ❌ with only `実装の誤り` / `テストの不足`, and this is the 3rd ❌ in the window | **Halt** with stop condition (f): two rounds of repair did not get the review to pass, so what to do next is a human's call |

#### Self-repair after a ❌ review (at most two rounds)

**The kinds are the reviewer's.** The independent agent classified each finding
([`../docode-review/SKILL.md`](../docode-review/SKILL.md)「Findings」); the driver acts on that
classification and never lowers it. A finding may only move **up** — while fixing a `実装の誤り` or a
`テストの不足`, discovering that the fix would change a frozen test's expectation, widen the scope or
change the spec makes it a human's: stop with (c), (e) or (f) as that discovery says. Nothing moves
down to a kind the driver may fix.

For each finding:

| Kind | Repair |
|------|--------|
| `実装の誤り` | Fix the code. Then re-run Step 3 items 1–4 for the ACs it touches — `run-tests`, `check-invariants`, `check-doc-freshness`, the re-anchor — **without Step 3b**: the boxes are already checked, and no new `AC-NNN done.` entry is written (it would reset the round count below). **Every frozen test stays as it is** (a fix that needs a frozen expectation changed is (c)) |
| `テストの不足` | **Add** a test, transcribed from the AC line and its sources exactly as Step 2a does — never from the code — and run it. Red → implement to green. Green on its first run → the behavior was there and is now measured; record that. Record the red as an `AC-NNN red-first:` entry, as Step 2a does; no new `done` entry (same reason as the row above). A test that mirrors the implementation is answered by the new test, not by editing or removing the old one; if the two cannot both hold, that is (c) |

Record what was done, then go back through the sweep (Step 4, item 1) to a **new** Step 4a:

```markdown
- docode-review 指摘の修正（自己修正 {k}/2）: #1 {何を直したか}、#2 {追加したテスト `<file>::<name>`、赤/初回から緑}。テスト緑（{n} 件）。
```

**Counting the rounds from the files.** The window is everything in the Decision Log after the
latest of: the last `AC-NNN done.` entry, the last `HALT` entry, and the last `- 再オープン:` bullet.
Count the `docode-review (Step 4a):` entries with verdict ❌ inside it. A HALT resets the window: once
a human has looked, the next run has its two rounds again. A resumed run counts the same way, so the
budget survives a broken session.

**Every round gets a fresh review.** Launch a new independent agent each time, as for any resumed
run (below); never reuse a verdict, and never review the repair yourself. The repair budget is
separate from `MAX_REPAIR_ATTEMPTS`, which counts repairs per AC inside the loop.

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

#### Step 4b: Pre-PR check (after a ✅ / ⚠️ review)

Follow [`../pre-pr/SKILL.md`](../pre-pr/SKILL.md) inline (`pre-pr` is not model-invocable, so its
steps are read and executed, as Step 3 does for `check-invariants`), in the mode that skill defines
for this call site: **every step that would rewrite code or documents reports instead of fixing** —
①, ② and a ④ item that "requires fix". The sweep already ran ① and ②; a fix now would be a change
Step 4a did not see. ⑥ still updates the plan's progress log (bookkeeping in `exec-plans/`, not
implementation). Append to the Decision Log:

```markdown
### YYYY-MM-DD
- pre-pr (Step 4b): {✅ No issues | ⚠️ {n} 件（{項目}） | ❌ {n} 件（{項目}）}。
```

| Result | Action |
|--------|--------|
| ✅, or ⚠️ / ℹ️ only | Go to Step 4c |
| ❌ (a blocking finding, or a step that would have needed a fix) | Report it and end — **no draft PR**, even if one was asked for. Fixing it is a change after the review: when the human has it fixed, the next run starts at Step 4a again (a resumed session always reviews fresh) |

#### Step 4c: Draft PR (only when the human asked for it at invocation)

Run this step **only when the human's instruction that started this run** asked for a PR
(「PR まで」, "through to a PR"). That instruction is the authorization stop condition (d) requires,
and it covers exactly two outward actions: pushing this branch, and opening a **draft** PR for it.
Marking it ready for review, requesting reviewers, merging, tagging and anything else outward still
halt with (d).

- **The instruction belongs to the invocation, not to the plan.** It is not written to the plan file,
  and a run started without it — including a resumed run after a HALT, whose earlier invocation did
  say it — does not open a PR: it ends after Step 4b and says that a run started with 「PR まで」
  would. A record of an earlier draft PR is history, not permission.
- Commit the work if it is uncommitted (a push needs a commit; this skill does not commit
  otherwise), push the branch with upstream tracking, and open the PR as a draft against the base
  branch (`main` unless the project says otherwise). If a PR already exists for the branch, push and
  keep it — do not open a second one, and do not change its draft state; replace the confirmation
  sheet in its body with the one this run wrote (the old one describes an older commit).
- The PR body states: the plan and its ACs, the Step 4a verdict and any suggestions, every ⚠️ / ℹ️
  of Step 4b, and what is left to the human — **confirming every AC, then `complete-exec-plan` on this
  branch before the merge** — and carries the confirmation sheet Step 4b wrote (`pre-pr` ⑧), so a
  reviewer confirms from it ([`../complete-exec-plan/confirmation-sheet.md`](../complete-exec-plan/confirmation-sheet.md)).
- Record it in the plan's Decision Log — `- draft PR (Step 4c): <URL>（起動時の指示「PR まで」による）`
  — then commit that record and push it to the same branch (the same authorization: this branch,
  this PR). Marking the PR ready for review is the human's.
- If the push or the PR creation fails (authentication, a protected branch, no remote), stop and
  report — do not retry with other credentials or another remote.

Without the instruction, stop after Step 4b and report. **Do not create a PR.**

**Do not complete the plan either.** Completion is the human confirming every AC, recorded, then
`complete-exec-plan` making the complete commit on this branch before the merge
([`../complete-exec-plan/completion-boundary.md`](../complete-exec-plan/completion-boundary.md)).
The driver's green run and the Step 4a verdict are what that confirmation is added to, not the
confirmation itself — name the step in the handoff, and leave it to the human.

---

## Stop conditions (halt and ask the human)

The driver continues autonomously **except** in these cases. When one fires, stop, write the
current state to the Decision Log, and put the decision to the user as a **decision request**
([`decision-requests.md`](decision-requests.md)): in product words, with every option, what each
changes (the edit as a diff), the routing where one is needed, and a recommendation. The HALT entry
is for the next session; the request is for the human. Once the human decides, the edits that
follow (the document that lost, a repointed row, a deferral bullet) are drafted for their approval
in the conversation — never by the loop itself, which edits neither document.

| ID | Condition | Why it is a human decision |
|----|-----------|----------------------------|
| (a) | An AC is missing, ambiguous, or under-specified. **Fired at Step 1b / 2a for a functional AC, before any code for it, the AC is held and the run goes on with the ACs unrelated to it; the run halts when no AC can go further, with every held question together (「Holding an AC」)**. Detected **before the loop** by the Step 0b readiness gate (any NOT READY criterion); by Step 0c / Step 2a when its test cannot be transcribed without inventing an expected result; by **Step 1b** when a source states a separate outcome or contradicts the AC line; by **Step 3a** when the spec section contradicts the AC; by **Step 0b / 1b / 3a** when a `## Sources` row names something that cannot be opened (not the same as `n/a`); by **Step 0b** when a row names background material instead of a source, and by **Step 1b** when an expected result appears only in background material; by **Step 0b** (backstop **0c / 1b / 3a**) when an `E2E-NNN` states an outcome nowhere in its comparison set, or contradicts it, or the set cannot be assembled (complement detection, `../create-spec/e2e-interaction.md`); and as a backstop during the loop — including a `[E2E]` AC whose test does not exist, so `run-tests` holds | Deciding *what to build* (and what the through-flow is) is outer-gate (spec-first principle). Choosing between two frozen documents that disagree is the same decision |
| (b) | Tests still red after `MAX_REPAIR_ATTEMPTS` self-repair tries — including a red-first test that never reaches **valid red** | Repeated failure signals a real problem the human should see |
| (c) | A test's *expectation* must change to pass — including any change to an expectation frozen by a Step 0c / Step 2a red observation | Test changes must be grounded in a spec change (INV-T01 / INV-T02) |
| (d) | An irreversible / outward-facing action is next (create or push a PR, `promote-spec`, deleting tags) — except the push and the draft PR of Step 4c, when the human asked for them in the instruction that started this run | Outward effects require human authorization. The instruction at invocation is that authorization for exactly those two actions, and only for that invocation |
| (e) | An INV violation cannot be resolved without expanding scope | Scope expansion is a planning decision, not execution |
| (f) | `docode-review` (Step 4a), run mandatorily once every AC is `- [x]`, returns ❌ Changes requested **with a finding the reviewer classified `人の判断が要る`**, or a ❌ remains after two rounds of self-repair (「Self-repair after a ❌ review」) | Deciding what to do about a finding that needs a judgement is the same governance call as rewriting an AC, and the driver that just finished implementing is the one party who cannot make it objectively. Findings the reviewer classified as plain implementation errors or missing tests are execution, so the driver repairs them — under a fresh review each time, and at most twice |

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

- A **hold** — `- 保留: AC-NNN（停止条件 (a)、Step 1b | Step 2a）— <問い>。関連して待つ AC: …` — records an AC
  this run set aside before any code for it (「Holding an AC」). It is a record, not state: the next
  run re-attempts the AC from Step 1b.
- A **self-repair after a ❌ review** — `- docode-review 指摘の修正（自己修正 k/2）: …` — is counted
  with the ❌ entries to find how many rounds are left (「Self-repair after a ❌ review」).
- A **deferral** is decided by a human, never by this skill — `deferred: spec/<label> の昇格まで — <所見>`,
  and later `deferred 解除: <日付・理由>`. The agent may draft the bullet in the conversation once
  the human has decided ([`decision-requests.md`](decision-requests.md)); the loop never writes it
  ([`../create-spec/e2e-interaction.md`](../create-spec/e2e-interaction.md)「Deferring a plan, and
  lifting it」). It is resume state too: a session that finds an unlifted deferral bullet stops at
  Step 0 without writing anything, and the line itself is what the next session reads.

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

- [ ] Target plan selected and baseline confirmed green — expected reds aside (Step 0) — **or** the
      plan was deferred and the run did not start (Step 0), with nothing appended to the plan; the
      remaining criteria then do not apply
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
- [ ] Every AC reached is either `- [x]` (green), held (`- 保留:`, before any code for it, with no
      unclear relation to the ACs that went on), or recorded as a HALT in the Decision Log; a run that
      held ACs halted only when no AC could go further, with every held question put together
- [ ] Every Step 4a ❌ was acted on by the reviewer's kinds: any `人の判断が要る` → HALT (f); otherwise
      self-repair with a new review, at most two rounds, then HALT (f)
- [ ] Decision Log updated per the resume-state convention
- [ ] **If every AC reached `- [x]`**: `docode-review` was run (Step 4a) via the `Skill` tool and its
      verdict recorded in the Decision Log **before** Step 4b; a ❌ verdict halted with stop
      condition (f) instead of going on (a run that stopped early on another stop condition does
      not need this — `docode-review` stays optional there)
- [ ] Step 0 prepared the run — a branch of its own, CONTEXT.md / invariants.md loaded, and a start
      record in the Progress Log (Step 0d) unless one was already there
- [ ] **If Step 4a's verdict was ✅ or ⚠️**: the sweep ran before the review, and `pre-pr` ran after it
      (Step 4b) without changing anything the review saw, with its result in the Decision Log
- [ ] A draft PR was opened only when the human asked for it in the instruction that started **this**
      run and Step 4b had no ❌ (Step 4c); otherwise no PR was created. The plan was not completed by
      this skill (completion needs the human's confirmation)

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
Held      : AC-003 (Step 1b) — 待つ AC: AC-004   |   none
Review fix: 自己修正 {k}/2 — 実装の誤り {n} / テストの不足 {n}   |   none
Tests     : ✅ {n} passing
docode-review (Step 4a): ✅ Approved | ⚠️ Approved with suggestions | ❌ Changes requested → HALT (f)
                         | n/a (loop stopped before every AC was checked — see Stopped at)
pre-pr (Step 4b): ✅ No issues | ⚠️ {n} (does not block) | ❌ {n} → no PR | n/a (did not reach it)
Draft PR (Step 4c): <URL> | ➖ not asked for at invocation (「PR まで」で起動すれば作成) | ➖ pre-pr ❌
確認シート: .claude/views/YYYY-MM-{name}.confirm.md（{commit} 時点。[E2E] は実演を、機能 AC はシートを確認）
Stopped at: {none | AC-NNN, stop condition <id>: <reason> | ⏸ not started — deferred: <the line>}

Next action: {confirm every AC yourself with the confirmation sheet (in the draft PR, or locally), then run
             /complete-exec-plan on this branch before the merge | fix the pre-pr ❌ and run again
             | human decision needed for the HALT (the decision request above)
             | lift the deferral (deferred 解除:) once the promotion it waits for has landed}
```
