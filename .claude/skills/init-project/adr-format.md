# ADR format — recording a decision together with what it was chosen over

> **Single source.** `init-project` (the first ADRs, from Q2), `setup-web.md` / `setup-windows.md`
> (a change to the standard configuration), `create-spec` (Step 2c, the ADR candidates of a drafted
> spec), `promote-spec` (Step 2, an ADR number taken on both sides; Steps 3, 5 and 7, the ADR
> candidates of a promotion), `create-requirements` (Q6, which cites ADRs as material), `doc-review`
> (§6, the rationale check) and `update-context` (which reads the ADRs for tech-stack and rule
> changes) all apply **this** file. Do not restate the template, the candidate test or the procedure
> inline in a skill — reference this file.

## Why this exists

DocDD keeps conclusions well: requirements, spec, ACs, constraints, a plan's Decision Log. The
material a conclusion is reached *from* — the options compared, the one rejected and why — is
consumed in a conversation, and unless something asks for it there, it is lost, with three effects:

- the same investigation is repeated each time the spec moves, because nobody can see how far the
  last one went;
- **a rejected option comes back**, and the same argument is held again, because the rejection was
  never written down;
- routing a fix (CLAUDE.md「変更のルーティング」— is the current target wrong, or is this the next
  thing to build?) becomes a guess, because the premise the spec was decided on is gone.

`docs/00_project/decisions.md` is where decisions accumulate across the life of the project — not
only the technology choices made at initialization, but the requirement and spec decisions made
afterwards. This file defines the format, and the points in the flow that ask for an ADR while the
material is still in hand.

**What an ADR is not.** A plan's `## Decision Log` records how *that plan* was executed — routing,
red-first observations, halts — and is archived with the plan. An ADR records a decision about the
product or the project that outlives any one plan. A Decision Log entry may cite an ADR; it does not
replace one.

---

## The format

`decisions.md` holds every ADR, newest last. Each is a `##` section:

```markdown
## ADR-NNN: {決定の題名}

- 日付: YYYY-MM-DD
- 状態: 採用 | 置換（ADR-MMM により）| 廃止（YYYY-MM-DD、理由）
- 種別: 技術 | 要件 | 仕様 | プロセス
- 根拠資料: `docs/00_project/research/{topic}.md`, {外部 URL・文書名・ヒアリング（YYYY-MM-DD、相手）} | なし（理由）

### 文脈

{何を決める必要があったか。そのときの制約・前提}

### 決定

{何を決めたか。1〜3文}

### 検討した代替案と却下理由

| 案 | 却下理由 |
|----|----------|
| {採らなかった案} | {なぜ採らなかったか} |

### 結果

{この決定で何が変わり、何を引き受けたか。決定が反映された文書と、変えた AC・シナリオの ID（AC-NNN・E2E-NNN）を散文で言及する（リンクしない）}
```

| Field | Rule |
|-------|------|
| `ADR-NNN` | The next free number in `decisions.md`. Never reused, and never renumbered once it is on `main` — other documents cite it (`create-requirements` Q6, a spec's `## 関連`, a Decision Log). An ADR still on another branch (a feature branch, `spec/<label>`) whose number `main` took in the meantime has not taken effect: renumber it on its own branch, with its citations there, before it merges. `promote-spec` Step 2 is one instance of this |
| 状態 | Written `採用` when drafted; there is no draft state. Where the ADR **is** says whether it is in effect: on a branch, it is a proposal; it takes effect when it reaches `main` — through the human merging that branch, which is approval as for every document (CLAUDE.md「E2E の凍結と補完検出」), or, for an ADR drafted on `main` (`promote-spec` Step 7), when the human reviews the commit before pushing it. An ADR on `spec/<label>` takes effect when that label is promoted. An ADR on `main` is **never deleted or rewritten**: a later decision that reverses it is a new ADR, and the old one becomes `置換（ADR-MMM により）` — the old reasons are exactly what the next reader needs |
| 種別 | `技術` (technology and configuration — what `update-context` reads as the tech stack), `要件` (what to build, scope, non-goals), `仕様` (how the app behaves), `プロセス` (development rules — what `update-context` reads as rule changes) |
| 根拠資料 | Where the material is: a research note under `docs/00_project/research/` (format: [`research-note-format.md`](research-note-format.md)), an external URL, a document name, an interview with its date. `なし（理由）` when there is none — never blank (a blank cannot be told apart from "nobody looked"). Name a note in backticks, as in the template. When a recheck supersedes a note, an ADR keeps naming the old one — it is what that decision was made from; a decision that changes because of the recheck is a new ADR naming the new note |
| **検討した代替案と却下理由** | **Required.** When no alternative was considered, replace the table with `なし（理由）` — the section itself stays. This is the section the format exists for: a conclusion without it is the state described in「Why this exists」 |

**The ADR is layer 0.** `decisions.md` links to nothing below `docs/00_project/` (DOC-INV-001 in
`../check-doc-invariants/SKILL.md`): where an ADR needs to say where a decision landed — the spec
section, the US — it names the path in prose or backticks, not as a Markdown link. It may link a
research note (same layer) and external URLs. Every layer may cite it.

**The ADR is background, never a source.** It explains why the spec says what it says; a test's
expected result is never drafted from it, and a plan's `## Sources` never names it
(`../create-exec-plan/ac-sources.md`「What counts as a source」). If what an ADR decided is needed to
write a test, it belongs in the US or the spec as well.

**An ADR with no 種別 or no 却下理由 section** stays valid. Nothing rewrites it on that account;
`doc-review` reports the missing section as a suggestion, to be filled when the ADR is next touched.

---

## When a decision is an ADR candidate

A decision is a candidate when **both** hold:

1. **It is a choice, not a restatement.** It picked one option where another was evident or was
   raised (a behavior rule the requirements left open, a technology, a scope line), narrowed what a
   reader would otherwise assume (a non-goal, a removed AC), or reversed an earlier decision (a
   CHANGED or REMOVED item, an ADR it would supersede). A spec section that only restates what its
   AC already says is not a decision.
2. **What it was chosen over is not already recorded.** No ADR covers it, and no research note
   (normally reached from the document's `## 関連`) names the option not taken and why. A `## 関連`
   entry that only names a source — a URL, a regulation, an interview — records what the decision was
   informed by, not what it was chosen over, so it does not end the candidacy. This is narrower than
   `doc-review` §6's question (is *any* basis recorded?): a decision can have a basis and still be a
   candidate.

The candidate test decides what the skill **asks about**, not what is recorded: whether a candidate
becomes an ADR is the human's answer.

---

## The procedure at a call site

1. **List the candidates** the call site finds (its own section says where it looks), each with the
   decision in one line and where it appears.
2. **Ask the human, per candidate**: record it as an ADR — yes or no. Ask once, as a list; do not
   ask again for a candidate already answered in this run.
3. **For each yes, draft the ADR** in `decisions.md` in the format above, with the next free number.
   Fill 文脈 and 決定 from the documents and the session. **Take 検討した代替案と却下理由 and 根拠資料
   from the human** — ask for them; never invent a rejected option or a reason. If the human
   considered no alternative, write `なし（理由）` with the reason they give.
4. **A no is final for this run and does not stop it.** Nothing here is a gate: the call site
   continues exactly as it would have without this step. Recording is kept going by being asked at
   the moment the material is still in hand, not by being enforced — enforcement would only produce
   rationale written after the fact (the same reason red-first evidence is reported, not blocked).
5. **Report** the result on the call site's `ADR 候補` line: `{n} 件 — ADR-NNN 追記 {n} / 見送り {n}`,
   or `none`.

**Which branch the ADR goes on.** The same branch as the document change the decision produced: a
spec drafted for the current target → the branch that merges to `main`; a next-version spec →
`spec/<label>`; a promotion → see `promote-spec`. An ADR must not take effect before the change it
explains.

---

## Where this is applied

| Call site | When | Action |
|-----------|------|--------|
| `init-project` (Q2) | Initialization | Write an ADR (種別 `技術`) for each technology with a clear reason. Ask Q2's "main reasons" question for the rejected alternatives too |
| `setup-web.md` / `setup-windows.md` | The standard configuration is changed | Write an ADR (種別 `技術`); the standard configuration is the alternative it was chosen over |
| `create-requirements` (Q6) | Writing a US | Cites existing ADRs as the material the requirement was decided from (`## 関連`). A choice between alternatives the user describes there is asked about with the procedure above — the only point that asks about a requirement-level choice |
| `create-spec` (Step 2c) | The spec has been drafted, before the report | Candidates from the drafted spec; the procedure above |
| `promote-spec` (Steps 2, 3, 5, 7) | Promoting `spec/<label>` | An ADR number drafted on both sides is renumbered on the branch (Step 2). CHANGED / REMOVED items with no ADR added in the same diff are candidates (Step 3), shown in the impact report (Step 5); a yes is drafted on `spec/<label>` before the merge, or on `main` in Step 7 |
| `doc-review` (§6) | Optional review | Reports a decision with no recorded basis, and an ADR without the required section (advisory) |
| `update-context` | Updating `CONTEXT.md` | Reads the ADRs of 種別 `技術` for tech-stack changes and `プロセス` for rule changes; an ADR without 種別 is read as `技術` |
