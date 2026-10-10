# AC sources — the material an AC condenses, and how it reaches the implementer

> **Single source.** `create-exec-plan` (writing the `## Sources` table), `run-exec-plan`
> (the readiness gate in Step 0b, Step 1b and the spec re-anchor in Step 3), `start-feature` (Step 1b
> and Step 2), `pre-pr` (⑤c), `check-doc-invariants` (DOC-INV-012), `doc-review` (§2),
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

A source is **frozen spec material authored by a human**. Two questions are kept apart here, because
answering one is not answering the other: *may this document be read?* and *may a test's expected
result be drafted from it?* Every document falls in one of three classes:

| Class | Documents | May be read | May supply given / when / then or an expected value |
|-------|-----------|:-----------:|:---------------------------------------------------:|
| **Source（起点にしてよい）** | The US file's `### AC-NNN` section (its bullets)・the spec section that says "satisfies AC-NNN"・the `E2E-NNN` scenario (for an `[E2E]` AC — frozen per [`../create-spec/e2e-interaction.md`](../create-spec/e2e-interaction.md))・`constraints.md` rows the AC must respect・the US `## ゴール像` (when `/create-spec` was skipped) | ✅ | ✅ — this is what `## Sources` names |
| **Background（背景として読んでよい）** | Research and investigation notes・`docs/00_project/**` (overview, glossary, `decisions.md` — the ADRs)・another plan's Decision Log・an issue or discussion thread (a plan may still cite one as the *origin* inside an `n/a（理由）`) | ✅ — to understand *why* the spec says what it does, and to route a fix (current version or next) | ❌ — never |
| **Not read（読まない）** | Existing implementation code・existing tests | ❌ — not for this purpose | ❌ |

The implementer's own inference about intent is in none of the classes: it is not a document, and an
expected result that rests on it is invented, not transcribed.

**Why background is separate from source.** Background is the material a decision was made *from* —
the comparison that was run, the option that was rejected, the business flow it was checked against.
It is worth reading: without it nobody can tell why the spec is the way it is, and the routing
question in CLAUDE.md (「今作っている物が間違っている」のか「次に作りたい物」なのか) becomes a guess. But
it is not the decision. A research note can describe three options; the spec froze one. Drafting a
test from the note would let the implementer re-decide what the human already decided — the same
hole red-first closed, reopened from the other side.

So the rules for background are:

- **An expected result found only in background material is one that neither the AC nor its sources
  state.** Drafting it is deciding it — outer gate (CLAUDE.md「自律実装ループ」). Unattended, that is
  **HALT (a)**; where a human is present, they rewrite the AC or promote the detail into the US / spec.
- **Background never overrides a source.** If it seems to disagree with one, the source is still what
  is transcribed. Note the disagreement for the human (it may be an in-version defect to route); it is
  not a stop condition by itself.
- **Background never appears in `## Sources`.** See「When a row names background material」below.

The exclusion of code and tests is the point, not an oversight. Red-first
(`../run-tests/red-first.md`) exists so the measurement is independent of the implementation; if
"read the sources" quietly permitted reading the code, the driver would be back to transcribing what
the code does. **Widening what may be read must never widen it toward the implementation — nor turn
material that informed a decision into the decision itself.**

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
- Write each source as `` `path` § section ``, with the path from the repository root in backticks.
  A reference names a path only when it **starts** with that backticked path; backticks anywhere
  else in a cell are prose.
  A section is an ID (`§ AC-001`, `§ E2E-001`, `§ TC-001` — defined by a heading, a table row's first
  cell, or a line `ID:`), a heading name (`§「タグの付与」`, or bare: `§ ゴール像`), or nested headings
  joined by `／` (`§ ゴール像／主要ユーザージャーニー`). Inside 「…」 a `/` is part of the name, not a
  nesting separator. A backticked token after the `§` is part of the section name
  (`` §「設定（`config.yaml`）」 ``), not a second path; a URL is a link, not a path. A section
  name that contains `、`, `,` or `;` is wrapped in 「…」, or it is read as two references.
- Point at a **section**, not just a file. "`app_spec.md`" alone is not a source; the driver would
  have to guess which part applies, which is the guessing this table removes.
- A cell may name more than one source — the US bullets and a `constraints.md` row, say — separated
  by `、`. Each must resolve on its own.
- `同上` works within one column, so a reader can resolve a row without scanning upward past a
  different file path. It has two forms. `同上 § X` takes the first file of the row above, with
  section X. A bare `同上` repeats the whole cell above — every source and section it names; under
  `n/a（理由）` it is `n/a` with the same reason. Either form with no row above it is an error:
  there is nothing to repeat.
- In active plans these forms are resolved mechanically by DOC-INV-012
  (`../check-doc-invariants/SKILL.md`): a missing file blocks the PR, an unmatched section warns.

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

## When a source cannot be opened

A row can be well-formed and still name something that is not there: the file was moved or renamed,
the section was retitled, or the path was mistyped. **That is not `n/a`.** `n/a（理由）` is a recorded
judgement that there is nothing to read. An unopenable row is the opposite claim — there *is*
something to read, and nobody can now read it. Falling back to the AC line, as the `n/a` row does,
would mean drafting the test from an interpretation of the one-liner: the path this file exists to
close, reopened by a typo.

**What "cannot be opened" means to a reader.** The file does not exist, or the reader cannot identify
the section the row names. A reader — the driver or a human — can tell a reworded heading from a
missing one by reading it, so a heading that is merely reworded *can* be opened (say which heading
was read in the record). The mechanical check cannot make that call, which is why DOC-INV-012 in
[`../check-doc-invariants/SKILL.md`](../check-doc-invariants/SKILL.md) blocks only on a missing
file and merely warns on a section it cannot match.

| Call site | Action |
|-----------|--------|
| `run-exec-plan` Step 0b (readiness) | The AC is **NOT READY**: `R2` cannot be judged against sources nobody can read, and the `n/a` fallback does not apply. **HALT** with stop condition (a) before the loop starts |
| `run-exec-plan` Step 1b (drafting the test) | **HALT** with (a). Do not draft from the AC line alone |
| `run-exec-plan` Step 3a (re-anchor) | **HALT** with (a). Do not check the box against nothing |
| `start-feature` Step 1b (readiness) and Step 2 | Present the row to the user — at Step 1b already, so one row does not get two verdicts two steps apart. Fixing it is theirs: point it at the moved file or section, or replace it with `n/a（理由）` if there is genuinely nothing to read |
| `doc-review` §2 (advisory) | Report the row. `R2` for that AC is NOT READY, not judged on the line alone |
| `docode-review` (advisory) | Hand the row to the reviewer as "cannot be opened", never as `n/a`; the reviewer reports it as a finding |

Repairing the row is a plan edit about *what the AC condenses* — a human's call, like every other
disagreement between a plan and its sources. The driver does not repair it, even when the move looks
obvious: guessing which file a row "meant" is the inference the `## Sources` table exists to replace.

**Moving a source breaks rows elsewhere.** A change that moves or renames a file a row names, or
retitles a section, breaks that row although no AC changed. The rows are updated **in the same
commit as the move** (at least before it is pushed), and by a human. That holds for every way a
source moves: a promotion (`promote-spec` Step 4 lists the rows, Step 5 shows them, Step 6 has them
repointed right after the merge and before the push), a fix made directly on `main`, and a plan whose
own work moves a file its `## Sources` names — which would otherwise trip DOC-INV-012 on its own PR
at the moment it succeeds. A moved or renamed file left behind is a DOC-INV-012 ❌ that blocks every
PR after it; a retitled section is a ⚠️ there, and a HALT (a) at run time if the reader cannot
identify it.

---

## When a row names background material

A row can resolve — the file exists, the section is there — and still name something that is **not a
source**: a research note, an ADR in `docs/00_project/decisions.md`, another plan's Decision Log. That
is neither `n/a` nor a source. The row claims the detail lives somewhere a test may be drafted from,
and it does not; falling back to the AC line would mean drafting from an interpretation again, and
reading the named material as a source would mean drafting from background.

If the detail the AC needs is genuinely only in background material, it has not been decided yet in
any frozen document. The fix is to put it there — promote it into the US or spec — or to write the
row as `n/a（理由）` and let the AC line carry the whole goal.

| Call site | Action |
|-----------|--------|
| `create-exec-plan` (Q3d) | **Do not write the row.** Promote the detail into the US / spec with the user, or write `n/a（理由）` |
| `run-exec-plan` Step 0b (readiness) | The AC is **NOT READY**: `R2` cannot be judged against material that is not a source, and the `n/a` fallback does not apply. **HALT** with (a) before the loop starts |
| `start-feature` Step 1b and Step 2 | Present the row to the user — at Step 1b already, as for a row that cannot be opened. Fixing it is theirs: promote the detail into the US / spec and repoint the row, or replace it with `n/a（理由）` |
| `doc-review` §2 (advisory) | Report the row. `R2` for that AC is NOT READY, not judged on the line alone |
| `docode-review` (advisory) | Hand the row to the reviewer as "names background material, not a source"; the reviewer reports it as a finding |

`run-exec-plan` Step 1b and Step 3a are not listed: a row of this kind stops the run at Step 0b, and
a resumed run passes through Step 0b again before it reaches them. No mechanical check flags these
rows yet — DOC-INV-012 resolves paths, it does not classify them.

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

1. Open what the AC's `## Sources` row names, taking the **most specific** entry available:

   | The row has… | Re-anchor against |
   |--------------|-------------------|
   | A spec section | that section |
   | `n/a` for spec but a US section — `/create-spec` was skipped | the US `AC-NNN` bullets (and, for a `[E2E]` AC, the `## ゴール像` 主要ユーザージャーニー). They are the frozen goal for such a plan |
   | `n/a` in **both** columns, or no `## Sources` table | nothing — record the `n/a` line and proceed |

   Skipping `/create-spec` is a documented path for small changes (`SKILL.md`), so "no spec section"
   must not mean "no re-anchor". It means the goal lives one layer up.
2. Ask **"does the behavior now implemented do what this material describes for this AC?"** — not
   "did the tests pass" (that is already known) and not "does the code look right".
3. Take the verdict from this table (read "spec" as "whichever source step 1 selected"):

| Verdict | Meaning | Action |
|---------|---------|--------|
| **一致** | The implemented behavior satisfies the section | Check the box; name the section in the `done` record |
| **spec の振る舞いを満たしていない** | An implementation gap the transcribed tests did not catch | Fix the implementation and re-verify. Counts against `MAX_REPAIR_ATTEMPTS` |
| **spec が述べる振る舞いに対応するテストが無い** | A measurement gap, not a frozen-expectation problem | Add a **new** test for it red-first (never edit a frozen one), then implement to green. Counts against `MAX_REPAIR_ATTEMPTS` |
| **spec が AC 行と矛盾** | A spec judgement | **HALT** with (a). Do not "fix" either side |
| **起点が開けない** | The row names a file or section that cannot be opened (「When a source cannot be opened」 above) | **HALT** with (a). Not the row below — `n/a` is a recorded judgement, this is a broken pointer |
| **起点なし（両列とも `n/a`、または表が無い）** | Nothing to anchor to | Record `spec 再アンカー: n/a（起点なし）` and proceed |

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
| `create-exec-plan` (Q3d) | Before the plan file is finalized | Write the `## Sources` table. Any AC whose source cannot be identified gets `n/a（理由）` — with the user, since "there is no spec for this" is a claim about the spec. Never name background material in a row (「When a row names background material」). A row naming an `E2E-NNN` freezes it — run complement detection first, and again for a row the readiness rewrite changes (`../create-spec/e2e-interaction.md`) |
| `run-exec-plan` (Step 0b) | Before the loop, for every unchecked AC | Open what each row names so `R2` is judged against the sources. A row that cannot be opened, or that names background material → that AC is NOT READY → **HALT** (a). A row naming an `E2E-NNN` also gets complement detection (`../create-spec/e2e-interaction.md`) |
| `run-exec-plan` (Step 1b) | After picking the AC, **before** drafting its test | Read the sources. Refinement → use it. Separate outcome / contradiction / cannot be opened → **HALT** (a) |
| `run-exec-plan` (Step 3a) | Before the box becomes `- [x]` | Run the re-anchor above and record the result on the `done` line |
| `start-feature` (Step 1b / Step 2) | Manual implementation path | Load the sources with the other required documents and show the user what the AC condenses. A human resolves a conflict — or a row that cannot be opened or names background material — in conversation rather than halting |
| `doc-review` (§2) | Optional review | Load every section the rows name so `R2` is judged as the other gates judge it; a row that cannot be opened or names background material is reported, not judged on the line alone (advisory) |
| `pre-pr` (⑤c) | Before the PR | ⚠️ Report a plan with no `## Sources` table, and any AC whose `done` entry has no re-anchor line. Does **not** block |
| `promote-spec` (Step 4–6) | Promoting a spec that moves or retitles a source | List the active plans' rows it breaks (Step 4), show them in the decision report (Step 5), and have the human repoint them right after the merge, before the push (Step 6) — see「Moving a source」above |
| `check-doc-invariants` (DOC-INV-012) | Before the PR (via `pre-pr` ③) and in `gc` | ❌ a file an **active** plan's row names does not exist; ⚠️ the named section cannot be matched, or the row names a file without a section. Completed plans are out of range |
| `docode-review` | Mandatory on autonomous completion (`run-exec-plan` Step 4a); optional independent review on the manual path | Judge the diff against the sources, not only against the AC line (advisory). A row that cannot be opened or names background material is handed over as such, never as `n/a` |
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
| Process walkthrough (`process-walkthrough.md`) | Does the process these documents describe actually run — including at the sites that consume what changed? |
| **AC sources** (this file) | Does the implementer receive the **whole** goal — and is the finished result still checked against it? |

Readiness `R4` and this file are adjacent but distinct: R4 asks *whether* an AC anchors to an E2E
step (a property of the AC's wording), while `## Sources` records *where to read* what it anchors
to (a path the driver can follow). An AC can pass R4 by naming `E2E-002` and still leave the driver
with no idea which document to open.
