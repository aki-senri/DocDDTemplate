# AC sources — the material an AC condenses, and how it reaches the implementer

> **Single source.** `create-exec-plan` (writing the `## Sources` table), `run-exec-plan`
> (Step 1b and the spec re-anchor in Step 3), `start-feature` (Step 2), `pre-pr` (⑤c),
> `docode-review` and `promote-spec` all apply **this** file. Do not restate the table format, the
> conflict branches or the re-anchor verdicts inline in a skill — reference this file, so the call
> sites cannot drift apart.

## Why this exists

An exec-plan AC is **one line**. That is deliberate: `spec-gate.py` parses `AC-(\d{3}):`, and
`create-requirements` says so outright — "each AC heading is condensed into a single
`- [ ] AC-XXX: <description>` line; the detailed bullet points stay in the US file."

So the verifiable detail exists — it is just somewhere else:

| Where the detail lives | What it holds |
|------------------------|---------------|
| `docs/01_requirements/user_stories/US-XXX_*.md` § `AC-NNN` | the 2–5 checkable bullets the one-liner condenses |
| `docs/02_spec/**` — the feature section marked "satisfies AC-NNN" | the behavior the AC is supposed to produce |
| `docs/02_spec/**` § `E2E-NNN` | the through-flow, and which ACs must add up to it |
| `docs/01_requirements/constraints.md` | the TC / BC / PF / SC rows the result must respect |

Before this file existed, none of it reached the autonomous driver. `run-exec-plan` steered by the
one-liner and judged green by "tests pass + invariants hold", so two things followed:

- **On the way in** (issue #23): the driver interpreted a condensed line on its own, and the US
  bullets that state the actual pass/fail conditions were never consulted.
- **On the way out** (issue #25): the `AC → spec → code` traceability that `create-spec` writes was
  never read back, so a green run could still miss the behavior the spec describes.

Both are the same defect from opposite ends: the plan file names the AC but not **where the AC came
from**. The `## Sources` table closes that, and it must live in the plan file itself — a resumed
session has only the files (CLAUDE.md「再開状態のファイル化規約」).

---

## What counts as a source

A source is **frozen spec material authored by a human**:

| Admissible | Not admissible |
|------------|----------------|
| The US file's `### AC-NNN` section (its bullets) | Existing implementation code |
| The spec section that says "satisfies AC-NNN" | Existing tests |
| The spec's `### E2E-NNN` scenario (for an `[E2E]` AC) | Another plan's Decision Log |
| `constraints.md` rows the AC must respect | The implementer's own inference about intent |
| The US `## ゴール像` (when `/create-spec` was skipped) | An issue comment thread, unless the plan records it as the origin |

The exclusions are the point, not an oversight. Red-first (`../run-tests/red-first.md`) exists so
the measurement is independent of the implementation; if "read the sources" quietly permitted
reading the code, the driver would be back to transcribing what the code does. **Widening the
source set must never widen it toward the implementation.**

---

## The `## Sources` section

Placed in the exec-plan after `## Acceptance Criteria` (and after the `[E2E]` note), before
`## Task Breakdown`:

```markdown
## Sources

| AC | US（検証可能な bullet） | spec（振る舞いの節） |
|----|------------------------|---------------------|
| AC-001 | `docs/01_requirements/user_stories/US-003_tagging.md` § AC-001 | `docs/02_spec/app_spec.md` §「タグの付与」 |
| AC-002 | 同上 § AC-002 | 同上 §「一覧の絞り込み」 |
| AC-005 [E2E] | 同上 § ゴール像／主要ユーザージャーニー | 同上 § E2E-001 |
```

Rules for the table:

- **Every AC in the plan gets a row.** An AC with no source is written `n/a（理由）` — never a blank
  cell. A blank is indistinguishable from a forgotten row, and the whole value of the table is that
  a reader can tell "there is nothing to read" from "nobody looked".
- **Never write a colon directly after `AC-NNN` in this table.** `spec-gate.py` matches
  `AC-(\d{3}):` anywhere in the file and would list a Sources row as if it were an acceptance
  criterion. Write `| AC-001 |`, not `| AC-001: … |`. (Same family of pitfall as the annotation rule
  in `SKILL.md`.)
- Consecutive rows may use `同上`, but only within one column — a reader must be able to resolve a
  row without scanning upward past a different file path.
- Point at a **section**, not just a file. "`app_spec.md`" alone is not a source; the driver would
  have to guess which part applies, which is the guessing this table removes.

Referencing `docs/02_spec/` from an exec-plan is a legal upward reference — see DOC-INV-001 in
`../check-doc-invariants/SKILL.md`, where exec-plans sit at layer 2.5 (below the spec they
implement).

---

## When a source and the AC line disagree

The AC line is the contract; the sources **refine** it. Four cases, and only the first is routine:

| The source, relative to the AC line | What it is | Action |
|-------------------------------------|-----------|--------|
| **Refinement** — the same single outcome, stated with concrete preconditions, boundaries or expected values | The intended case. This is the detail the one-liner condensed | Transcribe the test at *that* granularity. No gate |
| **A separate outcome** — an independent observable result the AC line does not cover | A readiness escape on **R1** (the AC bundles more than one outcome, or the plan is missing an AC) | Do not implement it silently and do not silently drop it. Per the call-site table below — the unattended loop **HALTs** with stop condition (a) |
| **Contradiction** — the same outcome with a different expected value | Which one is correct is a spec judgement | **HALT** with (a). Change neither the AC nor the spec to make them agree |
| **No source** (`n/a`) | The AC line is the whole goal | Transcribe from the line alone; record the re-anchor as `n/a` |

Bullets under the same `AC-NNN` heading in a US file belong to that AC **by construction** — that is
what the heading means. So "a separate outcome" appearing under one is evidence that the AC bundles
several results (R1) or that a criterion was never written down. Either way the fix is a human
rewriting the plan, not the driver picking one reading. This is the same family of failure red-first
catches for R2, detected one step earlier.

---

## The two uses

The table is read at two different moments, for two different reasons.

### Use 1 — drafting the test (before implementing)

The source set for transcription is **the AC line plus its sources**, never the code. See
[`../run-tests/red-first.md`](../run-tests/red-first.md); this file only widens *what may be read*,
it does not relax the prohibition on reading the implementation, nor the rule that an expected
result absent from all of it may not be invented.

### Use 2 — the spec re-anchor (before checking the box)

Passing tests prove the AC's transcribed expectations hold. They do not prove the implementation
does what the spec section describes: the transcription may have condensed something, and the tests
are bounded by what was transcribed. So before an AC's box becomes `- [x]`, read its spec section
again and compare it against the behavior now implemented.

**Procedure**

1. Open the spec section named in the AC's `## Sources` row.
2. Ask **"does the behavior now implemented do what this section describes for this AC?"** — not
   "did the tests pass" (that is already known) and not "does the code look right".
3. Take the verdict from this table:

| Verdict | Meaning | Action |
|---------|---------|--------|
| **一致** | The implemented behavior satisfies the section | Check the box; name the section in the `done` record |
| **spec の振る舞いを満たしていない** | An implementation gap the transcribed tests did not catch | Fix the implementation and re-verify. Counts against `MAX_REPAIR_ATTEMPTS` |
| **spec が述べる振る舞いに対応するテストが無い** | A measurement gap, not a frozen-expectation problem | Add a **new** test for it red-first (never edit a frozen one), then implement to green. Counts against `MAX_REPAIR_ATTEMPTS` |
| **spec が AC 行と矛盾** | A spec judgement | **HALT** with (a). Do not "fix" either side |
| **起点なし（`n/a`）** | Nothing to anchor to | Record `spec 再アンカー: n/a（起点なし）` and proceed |

The third row is the one to read carefully: adding a test is allowed because the frozen expectation
is untouched — `red-first.md` freezes *an expectation*, not *the set of tests*. Weakening or
rewriting the existing test to cover the gap is stop condition (c), not a repair. And if the missing
behavior turns out to be a **separate outcome** rather than part of this AC, it is the second row of
the conflict table above — HALT (a), not an extra test.

**Record format** — append to the AC's `done` entry in the plan's `## Decision Log`:

```markdown
- AC-NNN done. {何を実装したか＋主要ファイル}. Tests green ({n} passing).
  spec 再アンカー: `docs/02_spec/app_spec.md` §「タグの付与」と照合し一致。
```

or, when there is nothing to anchor to:

```markdown
  spec 再アンカー: n/a（起点なし — {理由}）
```

As with every exemption in DocDD, the `n/a` line is the record; silence is not an exemption.

---

## Where this is applied

| Call site | When | Action |
|-----------|------|--------|
| `create-exec-plan` (Q3d) | Before the plan file is finalized | Write the `## Sources` table. Any AC whose source cannot be identified gets `n/a（理由）` — with the user, since "there is no spec for this" is a claim about the spec |
| `run-exec-plan` (Step 1b) | After picking the AC, **before** drafting its test | Read the sources. Refinement → use it. Separate outcome / contradiction → **HALT** (a) |
| `run-exec-plan` (Step 3a) | Before the box becomes `- [x]` | Run the re-anchor above and record the result on the `done` line |
| `start-feature` (Step 2) | Manual implementation path | Load the sources with the other required documents and show the user what the AC condenses. A human resolves a conflict in conversation rather than halting |
| `pre-pr` (⑤c) | Before the PR | ⚠️ Report a plan with no `## Sources` table, and any AC whose `done` entry has no re-anchor line. Does **not** block |
| `docode-review` | Optional independent review | Judge the diff against the sources, not only against the AC line (advisory) |
| `promote-spec` (Step 7) | Generating a reconcile plan | Write the table with the **new** spec's sections and `E2E-NNN` as the sources of the re-opened ACs |

The action differs by site for the same reason as in `ac-readiness.md` and `red-first.md`: whether a
human who can decide *what to build* is present. Reading the sources is execution; resolving a
disagreement between them is governance.

`pre-pr` reports rather than blocks because both artifacts are hand-written prose — a missing
re-anchor line cannot be told apart mechanically from an unrecorded-but-performed check, and
blocking would teach people to add the line afterwards, destroying the evidence. The blocking checks
stay AC coverage and `[E2E]` coverage.

---

## Where it does not apply

| Case | What to record |
|------|----------------|
| **Documentation-only plan** whose subject is the repository's own conventions (no US, no spec) | One row covering the range: `AC-001〜AC-0NN` → `n/a（理由）`. The re-anchor is `n/a` for every AC |
| **A small change where `/create-spec` was skipped** | Fill the US column; write the spec column as `n/a（spec 未作成 — 起点は US の該当節）` |
| **A plan predating this convention** | No table. `pre-pr` reports it (⚠️); do not back-fill sources by inferring them from the code that already exists — that is precisely the reading this file forbids |

---

## Relationship to the other checks

| Check | The question it asks |
|-------|----------------------|
| AC readiness (`ac-readiness.md`, R1–R5) | Can this criterion be measured at all? |
| Red-first (`../run-tests/red-first.md`, INV-T02) | Is the measurement independent of the implementation? |
| `[E2E]` coverage | Do the fragments add up to something the user can do? |
| Process walkthrough (`process-walkthrough.md`) | Does the process these documents describe actually run? |
| **AC sources** (this file) | Does the implementer receive the **whole** goal — and is the finished result still checked against it? |

Readiness `R4` and this file are adjacent but distinct: R4 asks *whether* an AC anchors to an E2E
step (a property of the AC's wording), while `## Sources` records *where to read* what it anchors
to (a path the driver can follow). An AC can pass R4 by naming `E2E-002` and still leave the driver
with no idea which document to open.
