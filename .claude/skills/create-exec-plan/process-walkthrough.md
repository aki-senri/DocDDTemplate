# Process walkthrough — verifying a process change by walking one lap

> **Single source.** `create-exec-plan` (the verification AC), the implementer, `doc-review`,
> `docode-review` and `pre-pr` all apply **this** file. Do not restate the laps or the finding
> criteria inline in a skill — reference this file.

## Why this exists

Cross-checking that every call site *describes* a rule the same way is necessary and **not
sufficient**. When the rule describes a **state machine** — a loop, a resumable run, gates that hold
or release — all the descriptions can agree while the process itself cannot run: two rules that are
individually correct contradict each other in some state.

This file exists because of a concrete case. Red-first (INV-T02) was introduced across six call
sites and checked with a 16-item table; every item passed, because every item compared *text to
text*. Walking one lap of the loop afterwards found six states where the process deadlocked — among
them:

- a resumed run: the test frozen red by the previous session tripped "never start on a red baseline",
  so no session could ever continue a partly-done plan;
- the success moment: when the `[E2E]` test finally went green, the "green on the first run" branch
  fired and halted the loop **exactly when the run had succeeded**.

Neither is visible by comparing descriptions. Both are obvious the moment you ask "and then what
state are we in?"

---

## When it applies

| The change touches… | Walkthrough |
|---------------------|:-----------:|
| A loop, an iteration order, a retry budget | **Required** |
| A resumable / interruptible run (state carried in files between sessions) | **Required** |
| A stop / halt condition, or anything that starts or refuses to start a run | **Required** |
| A gate that holds, blocks or releases (`pre-pr`, `complete-exec-plan`, hooks) | **Required** |
| An exemption or an `n/a` path through any of the above | **Required** |
| A rule other rules consume (a single source with call sites) | **Required** |
| Wording, naming, formatting, examples — no state transitions | Not required |

Rule of thumb: if the text does not let you answer **"what happens on the second lap, on resume, and
on the exempt path?"**, the change is in scope.

---

## The procedure

Walk the process **as if executing it**. At each step name (a) the state before, (b) which rule
fires, (c) the state after. One lap is not enough — walk at least these:

| # | Lap | What it catches |
|---|-----|-----------------|
| 1 | **Happy path** — start to completion with a case that exercises the new rule | The rule not being reachable at all |
| 2 | **Second iteration** — the state lap 1 left behind is now the input | Rules that assume a clean start; artifacts of the first pass being read as failures |
| 3 | **Resume** — a fresh session starting from files alone, mid-process | Entry checks that reject the state a halt or a partial run leaves. This is where file-based-handoff conventions break |
| 4 | **Exemption** — the `n/a` path | A downstream gate that never heard about the exemption |
| 5 | **Gate boundary** — the handoff to another skill | The receiving gate misreading the handoff state (e.g. treating in-progress as final) |
| 6 | **Success moment** — the step where the goal is reached | Gates that fire on an "unexpected" transition and stop the run precisely when it worked |

For laps 3–6, use the *actual* artifacts the process leaves behind (plan file, checkboxes, Decision
Log entries), not a summary of them — the point is whether the files alone carry the state.

---

## What counts as a finding

| Finding | Shape |
|---------|-------|
| **Deadlock** | A state the process can enter but not leave (or cannot enter to continue) |
| **Contradictory verdicts** | Two rules give different answers about the same state |
| **Success treated as anomaly** | A gate halts or holds on the state that means the goal was reached |
| **Unreachable rule** | A branch no lap can reach — either dead text or a missing transition |
| **Self-violating entry condition** | The process's own output does not satisfy its own precondition on the next run |
| **Orphan exemption** | An exempt case that a later gate still holds on |

"Reads consistently" is not a finding, and neither is its absence — that is the description check,
which this one is added to, not a substitute for.

---

## Record format

In the plan's `## Decision Log`:

```markdown
- AC-NNN process walkthrough: {対象プロセス} を6周辿った
  (happy / 2周目 / 再開 / 免除 / ゲート境界 / 成功時)。検出 {n} 件:
  - {状態} で {規則 A} と {規則 B} が矛盾 → {修正}
  全周 PASS。
```

Naming the laps is part of the record. "全項目 PASS" with no laps named is the check this file
exists to replace.

---

## Where this is applied

| Call site | When | Action |
|-----------|------|--------|
| `create-exec-plan` | Writing the plan's verification AC | If the change is in scope, the plan **must** carry an AC that requires this walkthrough. A verification AC that only compares descriptions is insufficient on its own |
| The implementer | Before checking that AC's box | Perform the laps and record them; unrecorded is not done |
| `doc-review` | Optional review of a process document | Walk laps 2 / 3 / 4 against the diff; report findings (advisory) |
| `docode-review` | Optional independent review | Same, against the diff — an independent reader is more likely to notice a state the author assumed away |
| `pre-pr` | Before the PR | ⚠️ Report a plan in scope whose Decision Log has no walkthrough record. Does **not** block |
| `complete-exec-plan` | After the merge | **Deliberately not checked here.** Unlike red-first evidence — a claim about *how tests came to exist*, worth one last audit before the plan is archived — the walkthrough's finding is either already fixed in this diff or it is not, and completion happens after the PR merged, where re-reporting changes nothing. `pre-pr` is the gate |

**When a lap finds something the plan cannot fix.** Some contradictions are only resolvable by
changing a rule the plan never scoped. That is a scope decision, not execution: `run-exec-plan` halts
with stop condition (e), and a human decides whether to widen this plan or open another. Record the
finding either way — an unresolved lap finding is still a result.

---

## Where it does not apply

| Case | Why |
|------|-----|
| Changes with no state transitions (wording, naming, examples) | There is no second lap to walk |
| Executable processes covered by tests | Tests are the stronger measurement; walk the laps only for the parts no test exercises (typically the resume and exemption paths) |

The walkthrough AC itself is **exempt from red-first** — its result is the record, with no runtime
behavior to assert (see the exemption table in [`../run-tests/red-first.md`](../run-tests/red-first.md)).
Readiness (`ac-readiness.md`) still applies to it like any other AC.

This check reads documents. It cannot prove a process runs — it can only find the states where the
documents say it cannot.

---

## Relationship to the other checks

| Check | The question it asks |
|-------|----------------------|
| AC readiness (`ac-readiness.md`, R1–R5) | Can this criterion be measured at all? |
| Red-first (`../run-tests/red-first.md`, INV-T02) | Is the measurement independent of the implementation? |
| `[E2E]` coverage | Do the fragments add up to something the user can do? |
| **Process walkthrough** (this file) | Does the process these documents describe actually run — on the second lap, on resume, on the exempt path, at the moment it succeeds? |

The first three are about the *product*. This one is about the *process documents themselves*, which
is why it lives with plan authoring: a plan that changes how DocDD runs is not verified by the same
means as a plan that changes what the software does.
