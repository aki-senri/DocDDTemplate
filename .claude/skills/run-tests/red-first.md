# Red-first — the acceptance test is written before the implementation it measures

> **Single source.** `run-exec-plan` (Step 0c / Step 2a), `run-tests` (red-first verification),
> `start-feature` (implementation order), `pre-pr` / `complete-exec-plan` (evidence check) and
> `docode-review` all apply **this** file. Do not restate the procedure or the valid/invalid red
> criteria inline in a skill — reference this file, so the call sites cannot drift apart.

## Why this exists

A measurement is only worth acting on if it is independent of the thing measured. When one pass
writes the implementation and its test, the test records **what the code does**, not what the AC
demands — the run is green and the AC may still be unmet.

`INV-T01` forbids changing a test to match implementation behavior, but it only binds tests that
already exist: a test born *after* the implementation never has to be changed, because it was a
mirror from the start. Red-first closes that hole on the **time axis** — the test is authored from
the AC text while no implementation of it exists, and is **observed failing** before any is written.
That observation is what makes the later green mean something.

**INV-T02** states the rule; this file is how it is carried out.

---

## The procedure (per AC)

| # | Step | What must be true when it is done |
|---|------|-----------------------------------|
| 1 | Read the AC and its E2E anchor. **Do not read or write implementation code for it yet** | The intended given / when / then come from the AC text, not from existing code |
| 2 | Write the test **from the AC text alone**, tagged with the AC-ID | Its assertion is the AC's expected result, transcribed |
| 3 | Run it and observe **valid red** (below) | The failure is attributable to the missing behavior |
| 4 | Record the observation in the plan's `## Decision Log` | The expectation is now **frozen** (see below) |
| 5 | Implement until green | The test was not edited to get there |

**Transcription, not invention.** If the test cannot be written without inventing an expected result
the AC does not state, stop — that is a defect in the AC (readiness `R2` / `R3`), not a
test-writing problem. Deciding the expected result is *what to build*: an outer-gate decision
(CLAUDE.md「自律実装ループ」). See the call-site table for the action at each site.

---

## Valid red vs invalid red

A failing run is not automatically evidence. Classify it:

| | The failure is… | What it means | Next |
|---|---|---|---|
| **Valid red** | an assertion about the AC's expected result that did not hold — `expected 401, actual 500`, `expected the input to be preserved, actual empty` | The test measured the AC, and the AC is not satisfied yet | Record it, then implement |
| **Invalid red** | a compile error, an unresolved symbol/import, a fixture / harness / setup failure, a wrong test command, a syntax error | The test measured **nothing** — it never reached its assertion | Fix the test or the harness and re-run until valid red. **Do not start implementing** |

The rule in one sentence: **the red must be attributable to the missing behavior.** A test that
fails because it cannot run has observed nothing about the AC, and treating it as evidence
reintroduces exactly the gap red-first exists to close.

**Statically compiled languages** (C#, TypeScript with type-checked tests, …): calling an API that
does not exist yet is a *compile* error — an invalid red. Introduce the **minimal signature** the
test names (type / method / route) with no behavior — `throw new NotImplementedException()`,
`return default`, an empty handler — so the test compiles and fails on its assertion. That stub is
part of this step, not part of the implementation: it must contain no logic that could satisfy the
assertion.

---

## Record format (this is the freeze)

Append to the plan's `## Decision Log`, before implementing:

```markdown
- AC-NNN red-first: `tests/AuthServiceTest.cs::Login_WithInvalidPassword_Returns401` を AC 本文から
  起草し、実行して赤を観測（expected: 401 / actual: 500）。以降この期待値は凍結。
```

and after the implementation is green, the usual entry:

```markdown
- AC-NNN done. {何を実装したか＋主要ファイル}. Tests green ({n} passing).
```

**The order of the two entries is the evidence.** For each AC, the `red-first` entry must precede
the `done` entry — this is what `pre-pr` and `complete-exec-plan` check, and what a later session
reads to know the test was not written to fit the code.

---

## After the freeze: the only way a test may change

| Change to a frozen test | Allowed? |
|-------------------------|----------|
| Renaming, extracting helpers, deduplicating setup — **given / when / then unchanged** | Yes, no gate |
| Changing the expected value, threshold, or assertion shape | **Only through the spec alignment gate** (`run-tests` Step 4 option B): the spec must have changed, and the reason is recorded in the Decision Log against the AC-ID. In `run-exec-plan` this is stop condition (c) — the loop halts |
| Deleting the test, or weakening it so it passes | Never. This is the INV-T01 violation in its most direct form |

---

## Where this is applied, and what happens when red-first is not possible

The procedure and the valid/invalid red criteria are identical at every call site. Only the
**action** differs, on the same principle as `ac-readiness.md`: whether a human who can decide *what
to build* is present.

| Call site | When it runs | Action when the test cannot be written / red cannot be observed |
|-----------|--------------|------------------------------------------------------------------|
| `run-exec-plan` (Step 0c) | Before the loop, for every `[E2E]` AC | **HALT** with stop condition (a) — the through-flow cannot be transcribed from the AC |
| `run-exec-plan` (Step 2a) | Before implementing each functional AC | Not transcribable → **HALT** (a). Invalid red → fix the test/harness within `MAX_REPAIR_ATTEMPTS`, then **HALT** (b) |
| `run-tests` | Whenever it is invoked for a red-first run | Classify and report valid / invalid red. Never report an invalid red as "expected red" |
| `start-feature` (implementation order) | Manual implementation path | Present the situation to the user; the human decides (rewrite the AC, or proceed) |
| `pre-pr` / `complete-exec-plan` | After implementation | ⚠️ Report the missing evidence per AC. Does **not** block — the blocking checks remain AC coverage and E2E coverage |
| `docode-review` | Optional independent review | Report a test that mirrors the implementation rather than the AC as a finding (advisory) |

---

## Where it does not apply

| Case | Why, and what to record |
|------|-------------------------|
| **Documentation-only plan** | There is no test harness to be red in, and such a plan carries no `[E2E]` AC either. The evidence check reports `n/a (documentation-only)` |
| **A preservation AC** — refactoring, or a reconcile plan whose AC re-opens behavior that already has a passing test | The test predates the change, so independence holds by construction: it was not written to fit the new code. Red-first would require breaking working behavior on purpose. Record `AC-NNN red-first: n/a（既存テスト <name> が AC を表現し、変更前から緑）`. **This exemption does not apply if the AC changes the expected behavior** — then the new expectation is authored fresh and must be red first |
| **Harness / tooling work** with no AC of its own (adding a runner, CI wiring) | Nothing about a product AC is being asserted. Such work belongs to a task, not an AC |

An exemption is a recorded judgement, never a silence: writing the `n/a` line with its reason is
what distinguishes it from a skipped step.

---

## Relationship to AC readiness

`ac-readiness.md` `R2` asks whether a test *could* be written from the AC text.
Red-first is the same question asked **empirically**, at the last moment before implementation:
someone actually writes it.

- A NOT READY AC never gets here — `run-exec-plan` Step 0b stops the loop first.
- An AC that passed readiness but cannot be transcribed is a **readiness escape**. The correct move
  is the readiness move (HALT / ask the human to rewrite), not to loosen the test until it compiles.
