---
status: active
created: 2026-08-02
completed:
---

# goal-image-e2e

## Goal & Scope

要件と仕様の間に「ゴール像（完成イメージ）＋ E2E シナリオ」の層を新設し、E2E-AC を完了条件に組み込む。
対象は `create-requirements` / `create-spec` / `create-exec-plan` / `run-tests` / `pre-pr` の5スキルとドキュメント追従。
GitHub issue #27 (G-F) の解消。親トラッキングは #28 で、本プランはその Ph1（第1着手）にあたる。

## Acceptance Criteria

- [ ] AC-001: `create-requirements` の Q4 を optional「UI スケッチ」から必須「ゴール／完成イメージ」に変更し、①主要ユーザージャーニー（Mermaid）②完成時に利用者が何をできるようになるか（1〜3文）③非ゴール の3点を必須項目とし、US テンプレートに `## ゴール像` 節を追加する
- [ ] AC-002: `create-spec` の Screen/UX flows を `## E2E シナリオ` 節として必須化（`(if applicable)` を外す）し、`E2E-001 → AC-001, AC-003` 形式の横断 traceability を記録させ、Completion criteria にも追加する
- [ ] AC-003: `create-exec-plan` に E2E-AC を最低1本立てる規約（記法 `- [ ] AC-NNN: [E2E] ...`）を追加し、「全機能 AC が `- [x]` でも E2E-AC が緑でなければ完了ではない」を完了条件に明記する
- [ ] AC-004: `run-tests` Step 3 と `pre-pr` ⑤ の AC カバレッジ確認に「E2E-AC に対応するテストが存在し緑か」を追加し、E2E-AC 未カバー時は `pre-pr` / `complete-exec-plan` を保留させる
- [ ] AC-005: [E2E] `/create-requirements` → `/create-spec` → `/create-exec-plan` → `/pre-pr` を1本ウォークスルーし、ゴール像と E2E シナリオが最後まで痩せずに届くことを確認したうえで、`SKILL_FLOW.md`（§1 フロー図・§3 ギャップ表・§4 必須/任意ゲート表）と `README.md` / `README.ja.md` / `ONBOARDING.md` / `ONBOARDING.ja.md` を追従させる

## Task Breakdown

- [ ] AC-001 — `.claude/skills/create-requirements/SKILL.md` の Q4（L101 付近）と US テンプレート（L189 付近）、Completion criteria を改修
- [ ] AC-002 — `.claude/skills/create-spec/SKILL.md` の Step 2 セクション表（L106 付近）と Completion criteria（L144 付近）を改修
- [ ] AC-003 — `.claude/skills/create-exec-plan/SKILL.md` のインタビュー Q3（L36 付近）、テンプレート（L64 付近）、Completion criteria（L94 付近）を改修
- [ ] AC-004 — `.claude/skills/run-tests/SKILL.md` Step 3（L69 付近）と `.claude/skills/pre-pr/SKILL.md` ⑤（L33 付近）を改修
- [ ] AC-005 — 5スキルを通しでウォークスルー → `SKILL_FLOW.md` / `README.md` / `README.ja.md` / `ONBOARDING.md` / `ONBOARDING.ja.md` を追従
- [ ] `/check-doc-invariants` を実行
- [ ] `/doc-review` を実行（独立エージェントによる検査）
- [ ] `/pre-pr` を実行して PR 作成（PR 作成は人間ゲート）

## Progress Log

### 2026-08-02
- Plan created

## Decision Log

### 2026-08-02

- **E2E-AC の記法を `- [ ] AC-NNN: [E2E] ...` の接頭辞方式に決定**（AC-003）。
  代案は別系列 ID（`AC-E01:`）と独立節（`## E2E Acceptance Criteria`）だったが、前者は
  `.claude/hooks/spec-gate.py` の `AC-(\d{3}):`（L76）とプロンプトゲート `AC-\d{3}`（L137）の
  両方を改修する必要があり、後者は「AC は1つの節にある」前提で書かれた `run-tests` /
  `pre-pr` / `complete-exec-plan` を洗い直す必要がある。接頭辞方式なら hook 無改修・既存
  exec-plan と後方互換で、E2E か否かはマーカーの grep で判定できる。

- **本プランでは `/run-exec-plan` を使わない**（検証戦略）。
  このリポジトリはテンプレート本体であり `docs/` もテストスイートも存在しない。
  `run-tests` が回らないため自走ループの緑判定（Step 3）が成立せず、内側ループを自動化できない。
  検証は `/check-doc-invariants` ＋ `/doc-review`（独立エージェント）＋ AC-005 のウォークスルーで行う。
  AC は「テスト緑」ではなく「文書上で観測可能な条件」として記述してある。

- **変更のルーティング: `main` に直接（`spec/<label>` ブランチではない）**。
  本改修はスキル定義の不備是正（ゴール像の層が欠落しているという現バージョンの欠陥の修正）であり、
  次バージョン向けの新機能・スコープ拡張ではない。CLAUDE.md「変更のルーティング」の判断基準
  「今作っている物が間違っているのか、次に作りたい物なのか」に照らして前者と判断した。
  実装ブランチは `feat/goal-image-e2e-issue27`。

- **`docs/07_ai_context/CONTEXT.md` の更新はスキップ**。
  `create-exec-plan` の Step 5 は CONTEXT.md の優先タスク更新を求めるが、このリポジトリには
  `docs/` が存在しない（`init-project` が生成する側のテンプレート本体のため）。対象ファイルが
  無いため実行不能。追跡は GitHub issue #27 / #28 側で行う。
