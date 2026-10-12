# Research note format — an observation of the outside world, and when to look again

> **Single source.** `init-project` (「Document frontmatter」), `create-requirements` (Q6, which
> drafts notes — and through it `create-spec` Step 2b), `gc` (④, the research-note backstop),
> `doc-review` (§1 and §6) and `adr-format.md` (an ADR's 根拠資料) all apply **this** file. Do not
> restate the frontmatter, the recheck record or the backstop's rules inline in a skill — reference
> this file.

## What a research note is

A research note under `docs/00_project/research/{topic}.md` records **what the outside world looked
like when it was examined**: an investigation, the options compared, the one rejected and why, an
external specification, a regulation, a business flow, an interview. It is the material a decision is
made *from* — layer 0, background, never a source for a test (`../create-exec-plan/ac-sources.md`
「What counts as a source」).

**A note is not converted into an ADR.** The two record different things:

| | Records | Changes when… |
|-|---------|---------------|
| Research note | What was observed, as of `collected` | Never — an observation dated 2026-10 stays true of 2026-10 |
| ADR ([`adr-format.md`](adr-format.md)) | What was chosen over what, and why | Never rewritten either; a later decision supersedes it |

One note can inform several ADRs, and some notes inform none. An ADR names the notes it rests on
under 根拠資料; the note does not move into it.

**A note is never rewritten.** Its body is the observation, and an observation does not become
outdated — the world moves past it. So what goes stale is not the note but the **premise** a current
decision took from it: "Y was unmaintained in 2026, so we chose X" stays a true record of 2026, while
whether X should still be the choice depends on Y today. That premise is what a recheck looks at.

---

## Frontmatter

```yaml
---
status: active
collected: YYYY-MM-DD      # when the material was gathered
references:                # where it came from (URL, document, interview with date and person)
  - https://example.com/...
recheck_by: YYYY-MM-DD     # when to look at the outside world again — or: n/a（理由）
rechecked: YYYY-MM-DD      # the last recheck (omit until the first one)
---
```

| Field | Rule |
|-------|------|
| `collected` | The date the material was gathered — not the date the note was written, if they differ |
| `references` | Where each piece came from. An interview names its date and the person |
| `recheck_by` | Decided **by the human** when the note is written, from how quickly the material can change: a regulation or a competitor's product sooner, a stable standard later. The suggestion to offer is `collected` + 180 days. Information that cannot change — a comparison that is over, a historical fact, a measurement of a fixed artifact — gets `n/a（理由）`, and is never rechecked. Never written empty: when the human gives no answer, the field is left out |
| `rechecked` | Updated by the recheck record below |

A note with no `recheck_by` (the human gave no answer, or the note was written without the field) is
treated as due at `collected` + 180 days by the backstop, which says so in its report so the human can
set the field. A new note written by a recheck (below) follows these same rules — its `recheck_by` is
the human's call again.

**How a note is named.** Every document that names a note — a US's or spec's `## 関連`, an ADR's
根拠資料, a scenario's `満たす業務要求`, another note — names it by its path in backticks, not as a
Markdown link. A path is what the backstop searches for; and a link would put a deprecated note under
DOC-INV-003, whose mechanical fix (repointing the link to the successor) would silently change which
observation a decision rests on. A note names a US, a spec or an ADR the same way — in backticks —
since layer 0 links nothing below it (DOC-INV-001).

---

## Rechecking

What is rechecked is the **outside world the note describes**, not the note and not the decision.
The `gc` backstop (below) only reports that a recheck is due; looking again, and deciding what follows
from it, is the human's work. Nothing is updated automatically.

| The recheck finds… | Do |
|--------------------|----|
| **No change** | Append to the end of the note `- 再確認 YYYY-MM-DD: 変化なし（{何を確かめたか}）`, set `rechecked:` to that date, and move `recheck_by` forward. The decisions resting on it are untouched |
| **A change** | Write a **new** note for what is observed now, and on the old one set `status: deprecated` and `rechecked:` to the date, and append `- 再確認 YYYY-MM-DD: 変化あり → {new note's path}`. The old note is kept: the ADRs decided from it still name it. Then, **separately**, decide whether each decision resting on it should change — that is a routing decision like any other (CLAUDE.md「変更のルーティング」: a correction of the current target on `main`, or the next version on `spec/<label>`); a changed decision is a new ADR that supersedes the old one. Record the outcome on the old note for every current decision that rests on it (「The `gc` backstop」 step 4 — including one that reached it through an earlier `維持`), one line each, naming the document by ID or by its path in backticks: `- 影響 YYYY-MM-DD: {ADR-NNN \| path} — 維持（理由）\| 変更（{ADR-MMM \| main \| spec/<label>}）\| 未決`. A decision kept (`維持`) now rests on the new note — the backstop follows the `→` to it (step 4); a US or spec may also repoint its `## 関連` to the new note, while an ADR keeps naming the old one |
| **No time to look now** | Move `recheck_by` forward and append `- 再確認 YYYY-MM-DD: 延期（理由）`. The backstop is not a gate |

**What may change in a note** is exactly what this table writes: the `- 再確認` and `- 影響` lines
appended at the end, and `status`, `rechecked` and `recheck_by` in the frontmatter — plus one
mechanical repair: turning a Markdown link into the same path in backticks (DOC-INV-001's fix for
layer 0, which changes no meaning). Repointing a reference to a different document is never a repair.
Anything else is a rewrite of the observation.

**A note is deprecated only by a recheck that found a change** — the `変化あり` record. The general
lifecycle trigger "a successor document becomes `active`" (`gc` ④) does not apply to research notes:
whether the outside world changed is decided by a human looking at it, not by a newer file existing.

**A deprecated note is never deleted.** The general lifecycle rule lets a `deprecated` document be
deleted after 30 days (`gc` ④); a research note is exempt, for the same reason an ADR is never
deleted — the superseded decisions still name it, and their reasons are what the next reader needs.

**Citations of a deprecated note.** A US's or spec's `## 関連` that still names a deprecated note is
worth a finding (`doc-review` §6, and the backstop's step 6): the document may rest on an observation
that no longer holds, until the human records what it means for it.

---

## The `gc` backstop

`gc` ④ reports, as **candidates for a human**, the research notes whose recheck is due **and** that a
current decision rests on. A note no current decision cites is not reported however old it is: there
is no premise of a live decision to lose.

1. **Collect the notes**: `docs/00_project/research/*.md` with `status: active`. Skip `draft`
   (not approved yet), `deprecated` (handled in step 6), and `recheck_by: n/a（理由）`.
2. **Their due date**: `recheck_by`; with no `recheck_by`, `collected` + 180 days, marked
   `再確認日なし`; with neither, `判定不能`.
3. **Due** when the due date is on or before the day of the run. A `判定不能` note counts as due —
   never assumed fresh.
4. **Cited by a current decision.** A *current decision* is a `status: active` US or spec (through
   its `## 関連`), an ADR in `docs/00_project/decisions.md` whose 状態 is `採用` (through its
   根拠資料), or a `status: active` scenario (through its `満たす業務要求`). A current decision
   **rests on** a note when:
   - it names the note; or
   - it rests on a deprecated note whose `- 影響` line records it as `維持`, and that deprecated note's
     `変化あり →` points to this one. A kept decision rests on the successor now, so its recheck cycle
     continues there. The chain goes one link at a time and only through `維持`: when the successor is
     superseded in turn, the decision moves on only if the successor's own `- 影響` line records it as
     `維持` too — otherwise step 6 asks.

   A note is cited when a current decision rests on it.

   ```bash
   grep -rln "research/<topic>.md" docs/ 2>/dev/null || true   # hits that name the note; a hit on another note's
                                                               # 変化あり → line leads to the decisions resting on it through the chain
   ```
5. **Report** each due, cited note with its due date and every document that cites it, so the human
   can see which decisions a changed premise would reach.
6. **A superseded premise still in use.** A deprecated note is skipped by step 1, but a current
   decision may still rest on it (step 4 — by naming it, or through a `維持` chain from an earlier
   note). For each such decision, look for an `- 影響` line on this note that names it with `維持` or
   `変更` — the human has decided. Report each
   one that has no such line, or only `未決`, as **a decision resting on a superseded observation
   (candidate)**. This applies to every deprecated note, whether or not it carries a `変化あり` line —
   one deprecated by hand still leaves its citers resting on it. Without this step a change found by a
   recheck would leave the decisions it reaches unreported from then on, since the note that would
   have raised them is no longer active.

**The backstop does not edit** a note, its frontmatter, or any citing document — not even to move a date (`gc` ③'s link → same backticked path repair is the only edit `gc` makes, and it is not this backstop's). Rechecking
is the human's.

The report is weekly and advisory. `pre-pr` does not run it: a due recheck is unrelated to the PR at
hand, and a ⚠️ on every PR would teach people to move dates without looking.

---

## Where this is applied

| Call site | When | Action |
|-----------|------|--------|
| `init-project`「Document frontmatter」 | Documenting the frontmatter | Points here for the research-note fields |
| `create-requirements` (Q6) — and `create-spec` (Step 2b), which applies Q6's rules | Drafting a note from material found outside the repository | Ask the user for `recheck_by` (suggest `collected` + 180 days; `n/a（理由）` for information that cannot change) |
| `gc` (③, ④) | Weekly | ④: the backstop above (steps 1–6) — candidates only, nothing edited; research notes are exempt from the lifecycle's successor trigger and from the deletion of `deprecated` documents. ③: a DOC-INV-001 or DOC-INV-003 hit involving a research note is fixed only by turning the link into the same path in backticks — never repointed |
| `doc-review` (§1, §6) | Optional review | Reports a note without `recheck_by`, and a `## 関連` pointing at a deprecated note with no recorded outcome (`維持` / `変更`) (advisory) |
| `adr-format.md` | An ADR's 根拠資料 | Names notes in backticks; a superseded ADR keeps naming its old note |
