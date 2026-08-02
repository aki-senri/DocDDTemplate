# AC Readiness — the testability check applied before implementation starts

> **Single source.** `create-exec-plan`, `start-feature`, `run-exec-plan` and `doc-review` all apply
> **these** criteria. Do not restate them inline in a skill — reference this file, so the four call
> sites cannot drift apart.

## Why this exists

An acceptance criterion is the reference signal the implementation steers toward. A criterion that
cannot be turned into a pass/fail check gives the implementer nothing to steer by, and the failure
shows up late — as an implementation that satisfies the words and misses the point.

DocDD previously detected this **inside** the loop: `run-exec-plan` stop condition (a) fires when the
next AC is "ambiguous or under-specified". That is a subjective judgement made after implementation
has begun. Readiness moves the same detection **before** the loop and makes it a structural check:
five questions with a stated failing condition, asked of every AC while it is still cheap to rewrite.

**Scope of the check.** Readiness asks whether an AC *can be verified*, not whether it is the
*right thing to build*. A perfectly READY AC can still describe something nobody wanted — that is
what the goal image (`create-requirements`), the human spec approval, and `doc-review` are for.

---

## The five checks

Apply all five to each AC. Each check states what makes it **fail** — judge against that sentence,
not against a general impression of quality.

| # | Check | The question | Fails when |
|---|-------|--------------|------------|
| **R1** | 単一の観測可能な結果 | Does the AC name **one** outcome an observer can see? | It bundles several independent outcomes ("…し、かつ…も"), or names an activity rather than a result ("〜を検討する", "〜を改善する", "〜に対応する") |
| **R2** | given-when-then に落とせる | Can 前提 / 操作 / 期待結果 each be identified from the AC text? | Any of the three is absent — most often the expected result ("適切にハンドリングする", "正しく動作する"). If a test cannot be written from the text alone, R2 fails |

> **R2 is checked again, empirically, before implementation.** Red-first
> ([`../run-tests/red-first.md`](../run-tests/red-first.md), INV-T02) has someone actually write the
> test from the AC text and observe it fail. An AC that passed readiness here but cannot be
> transcribed there is a readiness escape, and the response is the same as a NOT READY verdict:
> rewrite it with a human, or halt.
| **R3** | 成功指標が具体 | Is the pass/fail signal concrete — a threshold, a value, a named output shape? | The decision rests on a subjective word: 速い / 使いやすい / 十分に / きれいに / 適切に |
| **R4** | E2E ステップへのアンカー | Can you name which `E2E-NNN` — and which step of it — this AC makes work? | No through-flow step depends on it. That means either the E2E scenario is missing a path, or the AC is not needed for the finished thing. (Source order: the spec's `## E2E シナリオ` → the US `## ゴール像` の主要ユーザージャーニー → this plan's own `[E2E]` AC) |
| **R5** | what であって how でない | Does it state the result to be achieved rather than the mechanism? | It prescribes the implementation (class names, library choice, function split). A how-AC goes green when the mechanism exists, whether or not the result does — and it makes any equally valid alternative look like a violation |

### Applying the checks to a `[E2E]` AC

A `[E2E]` AC is judged by the same five, read as follows:

| # | For an E2E AC |
|---|---------------|
| R1 | Is 完了条件 a single observable **end state**, not a restatement of the steps? |
| R2 | Are 前提 (given) and 完了条件 (then) both in the text? The journey itself is the *when* |
| R3 | Is the end state observable without a judgement call? |
| R4 | **n/a** — the E2E AC is what the functional ACs anchor *to* |
| R5 | Same as for functional ACs |

---

## Verdict

| Verdict | When | Meaning |
|---------|:----:|---------|
| **READY** | R1–R5 all pass | The AC can be implemented and verified as written |
| **⚠️ READY with a recorded reason** | Only **R3** or **R4** fails, and there is a stated legitimate reason | Proceed, but write the reason in the plan's `## Decision Log` |
| **NOT READY** | **R1**, **R2** or **R5** fails — or R3/R4 fails with no reason to give | The AC must be rewritten before implementation |

R1 / R2 / R5 decide whether a test can exist at all, so they have no exemption. R3 and R4 can be
legitimately unmet — e.g. the threshold lives in a spec that deliberately leaves it qualitative
this cycle, or the plan is documentation-only and has no through-flow.

**Who may state the ⚠️ reason.** A reason is a claim about the spec, so it comes from a human or
from a record a human left. `create-exec-plan` and `start-feature` may obtain one in conversation;
**`run-exec-plan` may not author one** — for the unattended loop, ⚠️ counts as passing only when the
reason is already written in the plan's `## Decision Log`. An unmet R3/R4 with no recorded reason is
NOT READY, and the loop halts. (Same principle as not rewriting the AC itself.)

**Documentation-only plans** (`E2E: n/a (documentation-only)` recorded in the Decision Log — see
`SKILL.md`) score **R4 as n/a**, not as ⚠️ — there is no through-flow to anchor to, and such a plan
carries no `[E2E]` AC of its own to anchor to either. The other four checks always apply: a
documentation change can state observably what must be true when it is done.

---

## Where this is applied, and what happens on a failure

The criteria are identical at every call site. Only the **action** differs, and it differs for one
reason: whether a human who can rewrite the AC is present. Rewriting an AC decides *what to build* —
an outer-gate decision no skill may make on the human's behalf (CLAUDE.md「自律実装ループ」). Where a
human is there, the fix is a conversation; where none is, the only correct move is to stop.

| Call site | When it runs | READY | ⚠️ | NOT READY |
|-----------|--------------|-------|----|-----------|
| `create-exec-plan` (Q3c) | Before the plan file is finalized | Write the plan | Write the plan; record the reason in the Decision Log | Rewrite the AC with the user. **Do not finalize the plan** with a NOT READY criterion |
| `start-feature` (Step 1b) | Before manual implementation | Proceed | Report and proceed | Present the failing checks and ask the user to rewrite or to proceed anyway; record the decision in the Progress Log |
| `run-exec-plan` (Step 0b) | Before the autonomous loop starts | Start the loop | Start the loop **only if the reason is already recorded** (see below) | **Do not start the loop** — HALT with stop condition (a) and record it in the Decision Log |
| `doc-review` (§2) | Optional independent review | ✅ | ⚠️ | ❌ in the findings table — advisory only; the reviewing agent changes no files |

### Where it is deliberately not applied

| Skill | Why not |
|-------|---------|
| `create-requirements` | Its AC 条件 are requirement-level statements, not yet implementation targets. They are checked when they become plan ACs (`create-exec-plan` Q3c), and advisorily by `doc-review` if the US is reviewed |
| `promote-spec` | A reconcile plan re-opens existing AC-IDs rather than authoring AC text. Those plans are gated at `start-feature` / `run-exec-plan` instead |
| `pre-pr`, `complete-exec-plan` | Readiness asks whether an AC *can be verified*, which is only actionable before implementation. After the fact, rewriting an AC means redoing the work; the post-implementation gates are AC coverage and E2E coverage |

This is **not** a severity mismatch between gates: the same AC receives the same verdict everywhere.
A plan that a human waved through at `start-feature` will still halt `run-exec-plan`, and that is the
intended behavior — the human's "proceed anyway" was a decision about *their own* next step, not a
licence for an unattended loop to guess.

---

## Report format

Every call site reports readiness in this shape (the surrounding report differs per skill):

```
=== AC readiness ===

AC-001  READY
AC-002  ⚠️  R3 — 閾値が今サイクルの spec で定性のまま（Decision Log に記録済み）
AC-003  NOT READY  R2 — 期待結果が本文から特定できない（「適切にハンドリングする」）
                   R5 — 実装手段（Repository を新設する）を指定している

Verdict: 1 NOT READY → {rewrite with the user | ask the user | HALT (stop condition (a))}
```

Name **every** failing check by its own ID — `R1` … `R5`, one line each, as AC-003 shows above — and
quote the phrase that fails it. Do not collapse them onto one representative check: an AC that fails
R1 and R5 needs both rewritten. "AC-003 is vague" is the judgement this file exists to replace.

---

## Worked example

**NOT READY**

```markdown
- [ ] AC-003: エラー処理を改善し、リトライ機構を Repository 層に追加して適切にハンドリングする
```

- R1 — 「改善」＋「追加」＋「ハンドリング」で結果が1つに定まらない（活動の記述）
- R2 — 期待結果が「適切に」しか書かれておらず、テストの then が起こせない
- R5 — 「Repository 層に」は実装手段の指定

**READY** (same intent, rewritten)

```markdown
- [ ] AC-003: 保存 API が 5xx を返したとき、最大3回まで指数バックオフで再試行し、
      3回とも失敗した場合は入力内容を保持したまま「保存できませんでした」を表示する
      （E2E-002 の「保存する」ステップ）
```

- R1 — 観測可能な結果（再試行回数と、失敗時の画面状態）
- R2 — given: 5xx が返る / when: 保存する / then: 3回再試行 → メッセージ表示・入力保持
- R3 — 「最大3回」「指数バックオフ」「入力内容を保持」で判定できる
- R4 — E2E-002 の該当ステップを名指ししている
- R5 — どこにリトライを実装するかは述べていない
