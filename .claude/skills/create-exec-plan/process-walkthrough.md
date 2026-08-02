# Process walkthrough — verifying a process change by walking its laps

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

There is a second way descriptions agree while the process does not run, and it points the other
direction: a change to a **rule other rules consume** alters every gate that consumes it without
editing one character of those gates. The gate and the rule still agree — the gate says "apply
`ac-readiness.md`", and it does — but the gate is now reached at a point where the material the rule
newly requires is not yet in hand. Walking forward from the change never arrives there, because the
gate is not on the path the change created. That is what lap 7 is for.

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
| **Renaming or renumbering a step, question or ID** that other documents point at (`Q3d`, `Step 0b`, `⑤c`) | **Lap 7 only** |
| Wording, formatting, examples — no state transitions and nothing points at them | Not required |

Rule of thumb: if the text does not let you answer **"what happens on the second lap, on resume, and
on the exempt path?"**, the change is in scope. And if anything outside the changed file names what
you changed, lap 7 is in scope even when the rest is not — a rename carries no state transitions and
still leaves every pointer to it wrong.

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
| 7 | **Dependency backflow** — the existing sites that *consume* what the change altered, each walked from the top of its own skill | Sites whose own text did not change but whose required inputs did. See the procedure below — this lap runs in the opposite direction from 1–6 |

For laps 3–7, use the *actual* artifacts (plan file, checkboxes, Decision Log entries, and for lap 7
the referring files themselves), not a summary of them — the point is whether the files alone carry
the state.

Laps 1–6 all start at the change and move forward, walking the path the change created. Lap 7 starts
at each existing consumer and walks in. Both directions are needed: a lap that begins at the change
can only reach what the change touched.

### Lap 7 — dependency backflow

**When it applies.** Whenever the change alters something another site reads: a single source file, a
record format, a stop condition's inputs, or what a step produces for a later gate. Step 2 below is
what decides this — an empty enumeration *is* lap 7's result and is recorded as such. Do **not**
conclude from memory that nothing consumes the change; that judgement is the one this lap replaces.

**Procedure**

1. **Name what the change altered that others consume.** Not the file that was edited — the thing
   inside it that a second site depends on. "The R2 check now judges the AC line *together with its
   sources*" is the unit, not "`ac-readiness.md` changed".
2. **Enumerate the referrers.** Start from the single source's own call-site table — it is the
   curated list and it is usually right — then widen with a grep on **both the file name and the
   rule's ID**, because the table is maintained by hand and a consumer can appear without being
   added to it:

   ```bash
   # 2>/dev/null || true: a range path may not exist in a given repo (no docs/, no
   # exec-plans/active/), and a no-match grep exits 1. Neither is a failure of this
   # lap — "nothing found" is a result. Without both, the command dies under set -e.
   grep -rn "ac-readiness\|R2" .claude/ exec-plans/active/ docs/ *.md 2>/dev/null || true
   ```

   The range is `.claude/**`, `exec-plans/active/**`, `docs/**` and the root `*.md`. Enumeration is the cheap
   net, not the expensive part — **step 3 is where the findings come from.** In the case below all
   three failing sites were already listed in the call-site table; what was missing was walking them.
   Three rules about the range:

   | Rule | Why |
   |------|-----|
   | **Do not** treat the call-site table as complete | It lists *sites*, by hand. A site can consume the rule through something the table does not name — in the case below, `doc-review` was listed, but the context it hands its subagent lives in the prompt template, which no table row covers. Grep finds what the table forgot; it does not replace reading the table |
   | **Do** include `exec-plans/active/**`, `docs/**` and the root `*.md` | A plan's Task Breakdown and Decision Log cite step names and question numbers routinely. A plan still pointing at `Q2b` after the question became `Q3d` is the same drift, in a file nobody thinks of as a "call site". `docs/**` is in range for the same reason: in a project built from this template, `invariants.md`, `review_checklist.md` and the spec cite rule IDs (`INV-TNN`, `DOC-INV-NNN`, `AC-NNN`). This template repo has no `docs/` tree, which is exactly why the command needs `2>/dev/null \|\| true` |
   | **Do not** treat a `## Decision Log` or `## Progress Log` entry **as a finding** | Those sections are append-only history (CLAUDE.md「再開状態のファイル化規約」): they record what was true when written, including values that have since changed. "AC-008 の本文を「1周」→「6周」に修正" must keep saying 1周, and a previous plan's own lap record must keep the lap count it walked, or the record of what was corrected is destroyed. Detection is mechanical; this exclusion is not — a person or the driver decides which hits are history. **Unchecked** (`- [ ]`) AC lines and Task Breakdown entries are *not* history and are in scope |

3. **Walk each referrer from the top of its own skill**, not from the line the grep matched. At the
   point the referring step is reached, ask: **is the newly required material in hand here?** Where
   the site hands work to someone else — a subagent prompt, a handoff to another skill — ask it of
   the receiver too. The material being available in the caller's session is not the same as it
   being passed on.
4. **When the answer is no**, the fix is one of: read it at that site, move the step that reads it
   earlier, or add it to what is handed over. Record which, per site.

**What this lap cannot find.** A grep returns *referrers* — sites that name the rule. A site that
should consume the rule and never mentions it is invisible to step 2, and step 3 never visits it.
That gap is real and this lap does not close it; the call-site table in the single source is what is
supposed to, which is the other reason step 2 starts there rather than replacing it.

**The case this lap comes from.** A change made the readiness check `R2` judge an AC against its line
**plus its sources**. Three existing sites consume `R2`, and all three fell behind while their own
text stayed correct:

| Site | When it reads the sources | Result |
|------|---------------------------|--------|
| `run-exec-plan` Step 0b (readiness) | Step 1b — per AC, **after** | Checked every AC on its one line → NOT READY → the loop could never start |
| `start-feature` Step 1b (readiness) | Step 2 — **after** | Same misjudgement (a human is present, so no halt — but the verdict is wrong) |
| `doc-review` §2 | never — the sources were not in the subagent prompt | Claims to return a verdict matching the other three gates, while structurally stricter than all of them |

Six laps were walked and all three were missed, because Step 0b is an unchanged section of an
unchanged file: no forward lap starts there. Lap 5 (gate boundary) asks whether the receiving gate
misreads the handoff *state*; it does not ask whether the receiving gate's own *input requirements*
grew.

Note what would have been enough: all three sites were **already listed** in `ac-readiness.md`'s
call-site table. Nobody needed a wider net — they needed to open those three files at the top and
ask one question. That is why step 3 is the lap and step 2 is only how you get a list to walk.

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
| **Unfed consumer** | A site that decides using material the change made necessary, reached at a point where that material is not in hand — including a receiver that is never handed it (lap 7) |
| **Stale pointer** | A reference to a step name, question number or ID (`Q3d`, `Step 0b`, `⑤c`, `INV-TNN`, `DOC-INV-NNN`) that no longer exists at the target (lap 7) |

"Reads consistently" is not a finding, and neither is its absence — that is the description check,
which this one is added to, not a substitute for.

The last two are the ones a walkthrough that starts at the change cannot produce, since the site
they name was never edited. If lap 7 reports neither, the record must still say which referrers were
enumerated — see the record format below.

---

## Record format

In the plan's `## Decision Log`:

```markdown
- AC-NNN process walkthrough: {対象プロセス} を7周辿った
  (happy / 2周目 / 再開 / 免除 / ゲート境界 / 成功時 / 依存の逆流)。検出 {n} 件:
  - {状態} で {規則 A} と {規則 B} が矛盾 → {修正}
  - 依存の逆流: {参照元 file:line} は {新しい判定材料} を持たない地点で判定 → {修正}
  依存の逆流の列挙: 呼び出し地点表 {n} 件 ＋ `grep -rn "{パターン}" .claude/ exec-plans/active/ docs/ *.md`
  で {n} 件 → {参照元を列挙}（うち履歴 {n} 件は対象外）。
  全周 PASS。
```

Naming the laps is part of the record. "全項目 PASS" with no laps named is the check this file
exists to replace.

Lap 7 additionally records **the grep and the referrers it returned**, even when it found nothing.
The other six laps are falsifiable from the record alone — a reader can re-walk them. "依存の逆流:
PASS" is not: without the enumeration there is no way to tell a lap that found nothing from a lap
that looked nowhere.

**When only lap 7 applies** — a rename or renumbering, per the scope table — the record says so
outright rather than claiming a count:

```markdown
- AC-NNN process walkthrough: 依存の逆流のみ（{変更}は状態遷移を伴わない改称のため
  1〜6周は適用外）。列挙: 呼び出し地点表 ＋ `grep -rn "{旧ラベル}" .claude/ exec-plans/active/ docs/ *.md`
  → {参照元}（うち履歴 {n} 件は対象外）。検出 {n} 件: {…} → {修正}。PASS。
```

Writing "1周辿った" for this case would be indistinguishable from the under-specified record this
file exists to replace. Name the lap, and name why the others do not apply.

---

## Where this is applied

| Call site | When | Action |
|-----------|------|--------|
| `create-exec-plan` | Writing the plan's verification AC | If the change is in scope, the plan **must** carry an AC that requires this walkthrough. A verification AC that only compares descriptions is insufficient on its own |
| The implementer | Before checking that AC's box | Perform the laps and record them; unrecorded is not done |
| `doc-review` | Optional review of a process document | Walk laps 2 / 3 / 4 / **7** against the diff; report findings (advisory) |
| `docode-review` | Mandatory on autonomous completion (`run-exec-plan` Step 4a); optional independent review on the manual path | Same laps, against the diff — an independent reader is more likely to notice a state the author assumed away, and lap 7 is where that matters most: the author knows which sites they *meant* to change, which is exactly the knowledge that hides the sites they did not |
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
| **Process walkthrough** (this file) | Does the process these documents describe actually run — on the second lap, on resume, on the exempt path, at the moment it succeeds, and at every site that consumes what changed? |

The first three are about the *product*. This one is about the *process documents themselves*, which
is why it lives with plan authoring: a plan that changes how DocDD runs is not verified by the same
means as a plan that changes what the software does.
