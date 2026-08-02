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

- [ ] AC-001: AC readiness 基準を単一ソース `.claude/skills/create-exec-plan/ac-readiness.md` として新設する。5観点（①観測可能な単一結果 ②given-when-then で書ける ③成功指標が具体 ④どの E2E シナリオのどのステップに効くか名指しできる ⑤what であって how でない）、判定（READY / ⚠️ / NOT READY）、`[E2E]` AC への適用差、documentation-only の免除範囲、および呼び出し地点ごとの措置表を定義する
- [ ] AC-002: `create-exec-plan` のインタビューに readiness チェック（Q3d）を追加し、Steps・Completion criteria・最終報告書式に「全 AC が READY（⚠️ は理由を Decision Log に記録）でなければプランを確定しない」を組み込む
- [ ] AC-003: `run-exec-plan` の Step 0 に "AC readiness gate" を追加し、ループ開始前に全未チェック AC を検査する。NOT READY があれば**ループを開始せず**停止条件 (a) で HALT し、判定結果を Decision Log に記録する。停止条件表・What this skill does・Completion criteria を追従させる
- [ ] AC-004: `start-feature` に readiness 確認ステップを追加し、手動パスでも同じ基準で検査する。人が同席するパスのため NOT READY は「提示して人が判断」とし、AC-001 の措置表と一致させる
- [ ] AC-005: `doc-review` の「2. Acceptance criteria quality」を `ac-readiness.md` の5観点を参照する形に揃え、レビュー観点が独自定義へドリフトしないようにする（optional スキルのため判定は助言のまま）
- [ ] AC-006: CLAUDE.md（停止条件 (a) の記述・スキル一覧）と `SKILL_FLOW.md`（§1 フロー図の PLAN / SF / DRIVER ノード、§2 呼び出し関係、§3-6 G-C 行、§5 改善提案）、`README.md` / `README.ja.md` / `ONBOARDING.md` / `ONBOARDING.ja.md` を追従させる
- [ ] AC-007: [E2E] 痩せた AC を含むプラン例で `/create-exec-plan` → `/start-feature` → `/run-exec-plan` の3地点をウォークスルーし、(a) 同じ AC が3地点で同じ READY 判定になること、(b) 措置だけが「書き直し／人に確認／HALT」と分かれること、(c) documentation-only 免除が3地点で一致することを確認し、結果を Decision Log に記録する

> このプランは、機能 AC がすべて `- [x]` でも `[E2E]` の AC が緑でなければ完了ではない。
> 本プランは documentation-only（変更対象は `.claude/skills/**` と `*.md` のみ）のため、
> AC-007 は `create-exec-plan` の documentation-only 免除に従い、Decision Log に記録した
> **再現可能なウォークスルー**をもって検証する。

## Task Breakdown

- [ ] AC-001 — `.claude/skills/create-exec-plan/ac-readiness.md` を新規作成
- [ ] AC-002 — `.claude/skills/create-exec-plan/SKILL.md` のインタビュー表・Steps・Completion criteria・報告書式を改修
- [ ] AC-003 — `.claude/skills/run-exec-plan/SKILL.md` の Step 0・停止条件表・Completion criteria を改修
- [ ] AC-004 — `.claude/skills/start-feature/SKILL.md` に readiness 確認ステップを追加
- [ ] AC-005 — `.claude/skills/doc-review/SKILL.md` §2 を単一ソース参照に変更
- [ ] AC-006 — `CLAUDE.md` / `SKILL_FLOW.md` / `README*.md` / `ONBOARDING*.md` を追従
- [ ] AC-007 — 3地点ウォークスルーを実施し Decision Log に記録
- [ ] `/check-doc-invariants` を実行
- [ ] `/pre-pr` を実行（PR 作成自体は人間ゲート）

## Progress Log

### 2026-08-02
- Plan created

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
