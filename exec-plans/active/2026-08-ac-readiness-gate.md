---
status: active
created: 2026-08-02
completed:
---

# ac-readiness-gate

## Goal & Scope

AC の testability（測定可能性）を、ループ内の主観判断から**ループ前の構造検査**へ前倒しする。
共通の「AC readiness 基準」を単一ソースとして新設し、`create-exec-plan`（起票時）/ `start-feature`（手動パス）/
`run-exec-plan` Step 0（自走前）の3地点で同じ基準を適用する。GitHub issue #24 (G-C) の解消。
親トラッキングは #28 で、本プランはその Ph2（#27 の次）にあたる。

## Acceptance Criteria

- [x] AC-001: AC readiness 基準を単一ソース `.claude/skills/create-exec-plan/ac-readiness.md` として新設する。5観点（①観測可能な単一結果 ②given-when-then で書ける ③成功指標が具体 ④どの E2E シナリオのどのステップに効くか名指しできる ⑤what であって how でない）、判定（READY / ⚠️ / NOT READY）、`[E2E]` AC への適用差、documentation-only の免除範囲、および呼び出し地点ごとの措置表を定義する
- [x] AC-002: `create-exec-plan` のインタビューに readiness チェック（Q3c）を追加し、Steps・Completion criteria・最終報告書式に「全 AC が READY（⚠️ は理由を Decision Log に記録）でなければプランを確定しない」を組み込む
- [x] AC-003: `run-exec-plan` の Step 0 に "AC readiness gate" を追加し、ループ開始前に全未チェック AC を検査する。NOT READY があれば**ループを開始せず**停止条件 (a) で HALT し、判定結果を Decision Log に記録する。停止条件表・What this skill does・Completion criteria を追従させる
- [x] AC-004: `start-feature` に readiness 確認ステップを追加し、手動パスでも同じ基準で検査する。人が同席するパスのため NOT READY は「提示して人が判断」とし、AC-001 の措置表と一致させる
- [x] AC-005: `doc-review` の「2. Acceptance criteria quality」を `ac-readiness.md` の5観点を参照する形に揃え、レビュー観点が独自定義へドリフトしないようにする（optional スキルのため判定は助言のまま）
- [ ] AC-006: CLAUDE.md（停止条件 (a) の記述・スキル一覧）と `SKILL_FLOW.md`（§1 フロー図の PLAN / SF / DRIVER ノード、§2 呼び出し関係、§3-6 G-C 行、§5 改善提案）、`README.md` / `README.ja.md` / `ONBOARDING.md` / `ONBOARDING.ja.md` を追従させる
- [ ] AC-007: [E2E] 痩せた AC を含むプラン例で `/create-exec-plan` → `/start-feature` → `/run-exec-plan` の3地点をウォークスルーし、(a) 同じ AC が3地点で同じ READY 判定になること、(b) 措置だけが「書き直し／人に確認／HALT」と分かれること、(c) documentation-only 免除が3地点で一致することを確認し、結果を Decision Log に記録する

> このプランは、機能 AC がすべて `- [x]` でも `[E2E]` の AC が緑でなければ完了ではない。
> 本プランは documentation-only（変更対象は `.claude/skills/**` と `*.md` のみ）のため、
> AC-007 は `create-exec-plan` の documentation-only 免除に従い、Decision Log に記録した
> **再現可能なウォークスルー**をもって検証する。

## Task Breakdown

- [x] AC-001 — `.claude/skills/create-exec-plan/ac-readiness.md` を新規作成
- [x] AC-002 — `.claude/skills/create-exec-plan/SKILL.md` のインタビュー表・Steps・Completion criteria・報告書式を改修
- [x] AC-003 — `.claude/skills/run-exec-plan/SKILL.md` の Step 0・停止条件表・Completion criteria を改修
- [x] AC-004 — `.claude/skills/start-feature/SKILL.md` に readiness 確認ステップを追加
- [x] AC-005 — `.claude/skills/doc-review/SKILL.md` §2 を単一ソース参照に変更
- [ ] AC-006 — `CLAUDE.md` / `SKILL_FLOW.md` / `README*.md` / `ONBOARDING*.md` を追従
- [ ] AC-007 — 3地点ウォークスルーを実施し Decision Log に記録
- [ ] `/check-doc-invariants` を実行
- [ ] `/pre-pr` を実行（PR 作成自体は人間ゲート）

## Progress Log

### 2026-08-02
- Plan created
- AC-001 完了
- AC-002 完了
- AC-003 完了
- AC-004 完了
- AC-005 完了

## Decision Log

### 2026-08-02

- **スコープの根拠**。issue #24 の改善方向は「①`create-exec-plan` に testability チェックを追加」
  「②または `run-exec-plan` Step 0 に AC readiness ゲート」「③曖昧さ検出をループ前の構造検査へ前倒し」の3案。
  ①②は排他ではなく、①だけでは起票を経ないプラン（`promote-spec` の reconcile プラン等）が素通りし、
  ②だけでは痩せた AC が一度ファイルに書かれてから止まる。両方を入れ、基準は単一ソース化して
  ドリフトを防ぐ（CLAUDE.md「インライン複製のドリフトを避ける」と同じ理由）。
  手動パス（`start-feature`）にも同じ検査を置かないと、自走を選ばないだけでゲートを回避できてしまうため
  AC-004 を含めた。
- **措置を地点ごとに変えた理由**。基準は3地点で同一だが、NOT READY 時の措置は「その場に人がいるか」で分かれる
  （create-exec-plan＝対話で書き直す／start-feature＝人に提示して判断を仰ぐ／run-exec-plan＝HALT）。
  厳しさの不一致ではなく「AC を書き直すのは統治判断であり、人がいなければ止めるしかない」という
  DocDD の原則の帰結。#27 のレビューで指摘された「ゲート間の重大度不整合」を再発させないよう、
  この差の理由を `ac-readiness.md` の措置表に明記する。
- **④（E2E ステップへの紐付け）を観点に含めた根拠**。#28 の着手順表で G-C は
  「その AC が E2E のどのステップに効くかも検査項目に含める」と定義されている。#27 で
  `E2E-NNN → AC-xxx` の traceability は spec 側に入ったが、spec を省略したプランでは検査されない。
- **DOC-INV は新設しない**。readiness は AC 本文の質であり、`check-doc-invariants` が扱う構造ルール
  （節の存在・ID の被覆）では判定できない。構造検査で代替すると「READY と書いてあるか」を見るだけの
  形骸化した INV になるため置かない。
- **`docs/07_ai_context/CONTEXT.md` の更新はスキップ**。本リポジトリに `docs/` は存在しない
  （`init-project` が生成する側のテンプレート本体のため）。追跡は GitHub issue #24 / #28 で行う。

- **AC-001 done.** `.claude/skills/create-exec-plan/ac-readiness.md` を新設。5観点（R1 単一の観測可能な
  結果 / R2 given-when-then / R3 具体的な成功指標 / R4 E2E ステップへのアンカー / R5 what-not-how）に
  「失敗する条件」を1文ずつ付け、主観的な良し悪しではなくその1文で判定させる形にした。
  判定は READY / ⚠️（R3・R4 のみ理由付きで許容）/ NOT READY（R1・R2・R5 は免除なし）。
  `[E2E]` AC への読み替え表、documentation-only での R4 = n/a、4呼び出し地点の措置表、報告書式、
  NOT READY → READY の書き換え例を収録。
- **AC-002 done.** `create-exec-plan` に Q3c（エージェントが実行する readiness チェック）と
  `## AC readiness` 節を追加し、Steps 2 / Completion criteria / 最終報告書式に組み込んだ。
  NOT READY を含むプランは確定しない。ユーザーが書き換えを拒んだ場合は理由を Decision Log に残し、
  後続の `run-exec-plan` は依然として HALT する（意図どおり）ことを明記。
- **Q3d → Q3c に変更**。プラン起票時は Q3d と書いたが、既存のインタビューは Q1/Q2/Q3/Q3b/Q4 で
  Q3c が空いており、Q3d では番号が飛ぶ。AC-002 の本文も合わせて修正（実装着手前の表記修正であり
  スコープ変更ではない）。

- **AC-003 done.** `run-exec-plan` に Step 0b（AC readiness gate）を追加。**未チェックの全 AC** を
  ループ開始前に検査し、NOT READY が1つでもあればループを開始せず停止条件 (a) で HALT する。
  「次の AC だけでなく全部を見る」理由（人の注意を一度で使う／READY は実装しても unready にならない）と
  「driver 自身が書き換えてはならない」理由（AC の書き換えは統治判断）を明記。停止条件 (a) の記述を
  「ループ前に Step 0b で検出、ループ中は backstop」に更新し、Step 1 は事前検査後に露見した曖昧さを
  拾う位置づけへ書き換え。Completion criteria と報告書式に Readiness 行を追加。
- **AC-004 done.** `start-feature` に Step 1b を追加。基準は同一・措置のみ「人に提示して判断を仰ぐ」。
  「このまま進む」は人自身の次手についての判断であって AC を清算するものではなく、後続の
  `run-exec-plan` は依然 HALT する（意図どおり）と明記。NOT READY がここで出る典型は
  `promote-spec` の reconcile プランなど起票を経ないプランであることも記載。
- **AC-005 done.** `doc-review` の §2 を `ac-readiness.md` の5観点参照に置換。独立エージェントは
  セッション文脈を持たないため、Step 2 の context 収集に `cat .claude/skills/create-exec-plan/ac-readiness.md`
  を追加し、プロンプトへ全文を埋め込む形にした（参照だけでは届かない）。出力表を
  「Verdict / Failing checks」に変更し、判定は advisory（ファイル変更なし）である点を明示。
  §2 に残した独自観点は readiness では測れない集合レベルの観点（正常系/異常系/境界の被覆、AC 間の重複・矛盾）のみ。
