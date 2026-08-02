---
status: active
created: 2026-08-02
completed:
---

# docode-review-required

## Goal & Scope

自走完了時（`run-exec-plan` の全 AC が `- [x]` に達した時点）に、`docode-review`（独立エージェントによる
ゴール照合）を `pre-pr` への handoff 前の**必須**ステップとする。人手実装（`start-feature` 経由、
`run-exec-plan` を使わない場合）の任意性は維持する。GitHub issue #26 (G-E) の解消。
親トラッキング #28 の着手順で最後（Ph5）にあたる。

## Acceptance Criteria

- [x] AC-001: `run-exec-plan` の Step 4（ループが全 AC `- [x]` に達して完了した場合に限る。HALT で
      終わった場合は対象外）が、`pre-pr` への handoff 前に `docode-review` を Skill ツール経由で
      呼び出し、その verdict（✅ Approved / ⚠️ Approved with suggestions / ❌ Changes requested）を
      最終レポートに新しい行として出力する状態にする
- [x] AC-002: `run-exec-plan` の Stop conditions 表に新しい停止条件 (f)（自走完了時の独立レビューで
      `docode-review` が ❌ Changes requested を返した）が追加され、発火時に Decision Log へ verdict と
      レビュー要約を記録して HALT する状態にする（✅ / ⚠️ の場合はそのまま `pre-pr` への handoff を
      継続する）
- [x] AC-003: 人手実装経路（`start-feature` 経由で `run-exec-plan` を使わない場合）では
      `docode-review` の任意性が維持される状態にする（`docode-review/SKILL.md` の実行タイミング記述と
      `SKILL_FLOW.md` のゲート表に、「自走時は必須・手動時は任意」という区別が明記され、両者を
      取り違えられる表現が残っていない）
- [x] AC-004: `pre-pr` が、対象プランが自走（`run-exec-plan`）で完了した痕跡（Decision Log に
      Step 0b のAC readiness記録など run-exec-plan 固有のエントリがある）を持つ場合に、
      `docode-review` の実施記録（verdict）の有無を確認して報告する状態にする（⚠️ 報告のみ・
      ブロックしない — 既存の ⑤b/⑤c と同じ理由：手書き記録の欠落は「未実施」と「記録漏れ」を
      機械的に区別できないため）
- [x] AC-005: [process walkthrough] 新設した docode-review 必須化ゲート（AC-001〜004 が導入する
      Step 4 の呼び出し・停止条件 (f)・pre-pr の確認）を happy / 2周目 / 再開 / 免除 / ゲート境界 /
      成功時の6周で辿り、検出した矛盾を修正した上で、全周 PASS を Decision Log に記録した状態にする
- [x] AC-006: `CLAUDE.md`（検証スキルの呼び出しポリシー表・自律実装ループ節）・`SKILL_FLOW.md`
      （必須/任意ゲート表）・`README.md` / `README.ja.md` / `ONBOARDING.md` / `ONBOARDING.ja.md` の
      `docode-review` に関する記述が「自走時は必須・手動時は任意」という区別で一致し、横断照合の
      結果が Decision Log に記録された状態にする

> このプランは documentation-only（`git diff --name-only` が `.claude/skills/**` /
> `CLAUDE.md` / `SKILL_FLOW.md` / `README*.md` / `ONBOARDING*.md` / `exec-plans/**` のみ）のため
> `[E2E]` AC を持たない。Decision Log の `E2E: n/a (documentation-only)` を参照。

## Sources

| AC | 起点 |
|----|------|
| AC-001〜AC-006 | `n/a（テンプレートリポジトリ自身の規約変更であり、US / spec を持たない。起点は GitHub issue #26 の本文と親トラッキング #28）` |

## Task Breakdown

- [x] AC-001 — `.claude/skills/run-exec-plan/SKILL.md` Step 4・「What this skill does」③・
      Completion criteria・Final report format
- [x] AC-002 — `.claude/skills/run-exec-plan/SKILL.md` Stop conditions 表
- [x] AC-003 — `.claude/skills/docode-review/SKILL.md`（`> When to run` / description）、
      `SKILL_FLOW.md` の必須/任意ゲート表
- [x] AC-004 — `.claude/skills/pre-pr/SKILL.md` に新しい確認項目を追加（番号は既存 ⑤b/⑤c の後）、
      Result report format・Completion criteria も追従
- [x] AC-005 — 6周のウォークスルーを実施し、検出事項を AC-001〜004・AC-006 に反映、Decision Log に記録
- [x] AC-006 — `CLAUDE.md`（検証スキルの呼び出しポリシー表・自律実装ループ節の該当箇所）、
      `SKILL_FLOW.md`、`README.md`、`README.ja.md`、`ONBOARDING.md`、`ONBOARDING.ja.md`

## Progress Log

### 2026-08-02
- Plan created
- Implementation started. Branch: `claude/issue-26-23a9d8`（既存ブランチを継続使用）。
  `start-feature` の Step 0（baseline tests）と Step 2（CONTEXT.md 読み込み）は、先行する
  #23/#24/#25/#27 の各プランと同じ理由（本リポジトリに `docs/` と `test_strategy.md` が存在しない
  テンプレート本体のため）で実行不可。AC を直接編集で実装し、AC-005 の process walkthrough で
  検証する。

### 2026-08-03
- AC-001〜AC-006 完了。全 AC が `- [x]`。次は `/pre-pr`。
- `/pre-pr` 実行。①②④ は前提ファイル不在で N/A、③ は DOC-INV-004 が既知の制約により6件（新規）、
  006 は ℹ️（documentation-only, [E2E] 無し, 矛盾なし）、⑤ は `test_strategy.md` 不在で実行不可、
  ⑤b は AC-005 に6周の記録あり ✅、⑤c は 6/6 AC に起点行・再アンカー記録あり ✅、
  ⑤d は本プラン自体が手動実装のため n/a、⑥ 更新済み。PR 作成は人間ゲートのため保留。
- `/docode-review` 実行（任意だが、この変更自体が中核ゲートに触れるため実施）。
  verdict ⚠️ Approved with suggestions（High 2件・Medium 1件・Low 1件）。4件とも対応済み
  （pre-pr ⑤d の検出マーカーを絞る、docode-review の Prerequisites を Step 4a 経路向けに補足、
  SKILL_FLOW.md §4 diagram 更新、Step 4a の「同一パス」定義を明記）。次は commit → PR 作成。

## Decision Log

- **AC readiness (Q3c, at authoring time)**: 全6 AC を `ac-readiness.md` の R1〜R5 で照合。
  R4 はいずれも documentation-only のため n/a（⚠️ではない）。NOT READY は0件。
  ```
  AC-001  READY
  AC-002  READY
  AC-003  READY
  AC-004  READY
  AC-005  READY
  AC-006  READY
  ```
- **E2E: n/a (documentation-only)** — 変更対象は `.claude/skills/**` と関連ドキュメントのみで、
  機能を実装するファイルを含まない。
- **設計判断（ユーザー確認済み, 2026-08-02）**: docode-review が ❌ を返した場合、driver は
  critical/high 指摘を bounded retry で自動修正しようとせず、新設の停止条件 (f) で HALT する。
  理由: 指摘への対応方針の決定（何を直すか）は governance 判断であり、driver が自己判断で
  直すと G-E がそもそも防ごうとしていた「自己検証バイアス」が形を変えて再発するため。
- **`docs/07_ai_context/CONTEXT.md` の更新はスキップ**。本リポジトリに `docs/` は存在しない
  （`init-project` が生成する側のテンプレート本体のため、先行する #23/#24/#25/#27 の各プランと
  同じ扱い）。追跡は GitHub issue #26 / #28 で行う。

### 2026-08-03

- **AC-001 done.** `.claude/skills/run-exec-plan/SKILL.md` の frontmatter description・
  「What this skill does」③・Step 4 を改修し、全 AC `- [x]` 到達時に新設の Step 4a が
  `docode-review` を Skill ツール経由で呼ぶようにした。Completion criteria と Final report format
  にも verdict 行を追加。spec 再アンカー: n/a（起点なし — 本プランの Sources は issue #26 本文）。
- **AC-002 done.** 同ファイルの Stop conditions 表に (f) を追加し、Step 4a の verdict 表
  （✅/⚠️ は継続、❌ は HALT (f)）と対応させた。spec 再アンカー: n/a（起点なし）。
- **AC-003 done.** `.claude/skills/docode-review/SKILL.md` の description と `> When to run` に
  「自走時は必須（run-exec-plan Step 4a）・手動時は任意」の区別を明記。あわせて `SKILL_FLOW.md`・
  `.claude/skills/run-tests/red-first.md`・`.claude/skills/create-exec-plan/ac-sources.md`・
  `.claude/skills/create-exec-plan/process-walkthrough.md` の呼び出し地点表にある docode-review 行
  （いずれも「Optional independent review」とだけ書かれていた）を同じ区別に更新。単一ソースの
  呼び出し地点表を放置すると AC-006 の横断照合で矛盾が出るため、本 AC の一部として先に直した。
  spec 再アンカー: n/a（起点なし）。
- **AC-004 done.** `.claude/skills/pre-pr/SKILL.md` に ⑤d を新設。Decision Log の run-exec-plan
  マーカー（`AC readiness: ... (Step 0b)` 等）の有無で自走完了かを判定し、直近の
  `docode-review (Step 4a): verdict` エントリの有無を ⚠️ 報告のみで確認する。Result report format・
  Completion criteria も追従。spec 再アンカー: n/a（起点なし）。
- **AC-005 done（process walkthrough）。** AC-001〜004 が導入したゲート（Step 4 / Step 4a / 停止条件
  (f) / pre-pr ⑤d）を6周辿った（happy / 2周目 / 再開 / 免除 / ゲート境界 / 成功時）。検出 2 件、
  両方とも修正済み：
  - **再開（lap 3）で検出**: 当初案は「`docode-review (Step 4a):` エントリが既に存在すれば
    再実行しない」としていたが、これだと (i) ❌ で HALT した後に人間が AC を再オープンせず直接
    修正した場合、(ii) reconcile プランが別の AC を再オープンして後日再度全 AC 完了に達した場合、
    のどちらも「diff は変わったのに古い verdict を読んで終わり」になり得た。修正: 「resumed
    session では常に再実行する。記録済み verdict は当時の diff についての証拠であり、今の diff
    についての証拠ではない」に書き換えた（`run-exec-plan/SKILL.md` Step 4a）。
  - **ゲート境界（lap 5）で検出**: `pre-pr` ⑤d の当初案は「記録あり／なし」の2値だったため、
    直近の verdict が ❌ のまま残っている状態（HALT を人間が手動で乗り越えて pre-pr まで来た
    ケース）を「記録あり」として素通りしてしまっていた。修正: ⑤d に3つ目の分岐
    「直近 verdict が ❌ のまま」を追加し、既存の未解決指摘を残したまま進んでいることが分かる
    文言にした（`pre-pr/SKILL.md`）。
  - **happy / 2周目 / 免除 / 成功時**: 検出なし、PASS。
    - happy: 全 AC 完了 → Step 4a → ✅/⚠️ → pre-pr handoff、が単独のパスとして到達可能。
    - 2周目: 上記の再開修正により、2回目の完了（reconcile 等）でも新しい diff に対して
      再実行されることを確認。
    - 免除: documentation-only であっても Step 4a は免除されない（docode-review 自体が
      「AC 無し／spec 無し」でも一般品質レビューとして機能するため、免除の必要が無いことを確認）。
    - 成功時: ✅ verdict は異常系として扱われず、そのまま handoff する分岐のみが存在することを確認
      （process-walkthrough.md が警告する「成功を異常として扱うゲート」のパターンは無い）。
  全周 PASS。
- **AC-006 done.** `CLAUDE.md`（検証スキルの呼び出しポリシー表3箇所・自律実装ループの停止条件表・
  自動化してよい範囲表）、`SKILL_FLOW.md`（§1 メイン図・§2 呼び出し関係表・invocation mode 注記・
  §3-6 ギャップ表・§4 within-skill blocking の補足段落）、`README.md`・`README.ja.md`・
  `ONBOARDING.md`・`ONBOARDING.ja.md` を横断照合し、「自走時は必須・手動時は任意」の表現で統一。
  cross-check 結果: 全13箇所を修正し、取り違えられる「optional」単独表記は残っていない。
- **`/pre-pr` の結果（2026-08-03）**。① invariants: N/A（`docs/04_implementation/invariants.md` 不在）、
  ② doc-freshness: N/A（`tracks:` を持つドキュメント不在）、③ doc-invariants:
  DOC-INV-004 が本プランの AC-001〜006 分（6件）追加（既知の構造的制約 — 本テンプレートに
  `docs/01_requirements` が無いため US 側の `ac_ids:` と照合できない。先行プラン群と同根）。
  DOC-INV-006 は `[E2E]` AC 無し＋`E2E: n/a` 記録あり＝ ℹ️（矛盾なし）。DOC-INV-005 は本プランの
  変更ファイルに ASCII art 無し、対象外。他は PASS または N/A。④ review_checklist: N/A（ファイル
  不在）。⑤ run-tests: 実行不可（`docs/05_quality/test_strategy.md` 不在。本リポジトリはスキル
  定義ドキュメントのみで自動テスト基盤を持たない）。E2E カバレッジ: プランに `[E2E]` AC が無い
  （documentation-only）ため ⚠️ 報告のみ。red-first 証跡: ➖ n/a（documentation-only、テスト
  ハーネス無し）。⑤b process walkthrough: ✅ AC-005 に6周の記録あり（検出2件、修正済み）。
  ⑤c AC sources: ✅ 6/6 AC に起点行あり（`n/a（理由）`）。spec 再アンカー: ✅ 6/6 AC に
  `n/a（起点なし）` の記録あり。⑤d docode-review evidence: ➖ n/a — 本プラン自体は
  `run-exec-plan` を実際には起動していない手動実装（先行プランと同じ理由。Decision Log に
  Step 0b 等のマーカー無し）。⑥ exec-plan: 更新済み（本エントリ）。
  PR 作成は人間ゲートのため保留。
- **`/docode-review`（任意・本プランは手動実装のため必須ではないが、`run-exec-plan` の中核ゲート
  自体を変更する変更のため実施, 2026-08-03）**。verdict: ⚠️ Approved with suggestions
  （🟠High 2件・🟡Medium 1件・🔵Low 1件、Critical/High の破壊的指摘なし）。全4件を対応：
  1. 🟠 `pre-pr` ⑤d の検出マーカーが `red-first:` / `spec 再アンカー:` も含むと書いていたが、
     これらは手書き Decision Log の一般的な語彙であり、**本プラン自身が手動実装なのに
     同じ語彙を使っている**ことで誤検知の実例になっていた（レビューア指摘）。修正:
     マーカーを `AC readiness: ... (Step 0b)` のみに絞った（`run-exec-plan` の Step 0b でしか
     出力されない語句のため）。
  2. 🟠 `docode-review` の Prerequisites（「作業ツリーがクリーン」「コミット済み」）が、
     Step 4a の実際の呼び出し文脈（全 AC 完了時点ではコミットされているとは限らない —
     DocDD は明示的な指示があるときのみ commit する）と矛盾していた。修正:
     Prerequisites を「手動経路向け」と明記し、Step 4a 経路はこれに従わず Step 1 の
     「作業ツリーが汚れている場合」分岐（`git diff --cached` / `git diff` を含める）に従う旨を追記。
  3. 🟡 `SKILL_FLOW.md` §4 の diagram（"Mandatory Gates vs. Optional Gates"）が
     `docode-review (optional)` のまま未更新だった（直後の補足段落だけ追加し、diagram 自体を
     見落としていた）。修正: diagram に自走完了時の必須パス（`L ==>|Step 4a| DCR`）を追加。
  4. 🔵 `run-exec-plan` Step 4a の「同一パス内では2度呼ばない」の境界が曖昧だった。修正:
     「同一パス」の定義（新しいツール呼び出し境界・新しいユーザーメッセージ・人間が repo を
     変更しうる隙間が無いこと）を明記。
  4件とも修正済み。再レビューは実施しない（verdict が ❌ でないため、AC-002/Step 4a の
  「❌ のときのみ再実行」の対象外。⚠️ 指摘への対応は人間の裁量）。
