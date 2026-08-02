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
- commit → push → PR #34 作成。
- ユーザー依頼によりテンプレート全体の横断矛盾チェックを実施。3件検出（うち1件は
  docode-review 自身の Step 4 が ❌ 時に「直して再実行」と書いており run-exec-plan Step 4a の
  「HALT (f)、直して再実行しない」と矛盾——3段階のレビューを通り抜けていた）。全件修正し
  追加 commit → push 済み。
- PR #34 の Copilot レビュー（2回）を確認・対応。4件（実質3種、英日重複含む）修正し追加 commit → push。

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
- **横断矛盾チェック（ユーザー依頼, 2026-08-03, PR #34 作成後）**。「テンプレート自体をレビューする
  skill が無い」という前提で、`docode-review` 関連の全13箇所に加え、停止条件・スキル数など他の
  横断整合性を手動で照合した。検出3件、全件修正済み：
  1. 🟠 **`docode-review/SKILL.md` 自身の Step 4「Present findings to the user」と
     「Result report format」が、❌ のときの対応を「指摘を直して再実行」とだけ書いており、
     `run-exec-plan` Step 4a が定めた「❌ なら HALT (f)。driver は直して再実行してはならない」と
     直接矛盾していた**。両方とも自走中に読まれうる同一スキルの本文でありながら、手動経路の
     既定動作しか書いていなかった（当初実装・process walkthrough・`/docode-review` 独立レビュー
     の3段階すべてが見落とした）。修正: Step 4 の表と Result report format を「手動経路」と
     「run-exec-plan Step 4a から呼ばれた場合」の2列に分け、後者は「HALT (f)。指摘を直して
     再実行してはならない」と明記。
  2. 🟡 `ONBOARDING.md` / `ONBOARDING.ja.md` に「停止条件 a〜e」という表記が計6箇所
     （mermaid 図2箇所・ASCII フロー2箇所・責任分担の説明文2箇所）残っており、新設の (f) が
     反映されていなかった。修正: 全6箇所を「a〜f」に更新（英語版の説明文にも
     "review findings" の例を追加）。
  3. ℹ️ `run-exec-plan/SKILL.md` の「Design principle」表（inner-loop / outer-gate の対比）に
     `docode-review` の呼び出しと ❌ 対応判断が入っていなかった。`CLAUDE.md` の対応する表
     （「自動化してよい範囲 / 残す範囲」）には AC-002 実装時に追加済みだったため、
     単一ソースであるはずのスキル本体側が要約側より古い状態になっていた。修正:
     同じ2項目を Design principle 表にも追加。
  他に確認し矛盾なしと判断した項目: スキル総数（17、変更なし）、`.claude/hooks/*.py` に
  docode-review への参照なし、`SKILL_FLOW.md` §2 の共有参照ファイル解説（red-first.md /
  ac-sources.md / process-walkthrough.md の要約段落）は docode-review を中立的に言及するのみで
  必須/任意の主張を含まないため対象外、既存 `exec-plans/active/*.md`（他プラン）の docode-review
  言及はすべて過去の Decision Log 記録であり現在の規約を主張するものではないため対象外。
- **PR #34 の Copilot レビュー対応（2026-08-03、commit `3f5a5de` に対する2回のレビュー）**。
  計4件（うち1件は英日で重複）。全件修正済み：
  1. `SKILL_FLOW.md`（§1 diagram, PREPR ノード）が ⑤d（新設した docode-review evidence 確認）を
     列挙しておらず、`pre-pr/SKILL.md` の実体と diagram が食い違っていた。修正: PREPR ノードに
     `⑤d docode-review verdict recorded? for autonomous completions (⚠️ only)` を追加。
  2. `ONBOARDING.md:310` / `ONBOARDING.ja.md:310` の「これ以外に init-project と doc-review が
     あり」という列挙が `docode-review`（下表の外にあるスキルの1つ）を含んでおらず、
     直後の段落の説明（docode-review は経路によって両方の段にまたがる）と噛み合っていなかった。
     修正: 列挙に `docode-review` を明記。
  3. `README.md:129` / `README.ja.md:129`（「model-invocable なのは run-tests と docode-review
     のみ」という記述）が、同じ独立レビュー節に並ぶ `doc-review`
     （`disable-model-invocation: false`、docode-review と同じ理由で model-invocable）を除外して
     しまっていた——独立レビュー2スキルを1つの節にまとめた際に見落とした一般化ミス。
     修正: `doc-review` を列挙に追加。
  4番目の指摘（AC-006 の cross-check で「全13箇所」と記録していたが、実際は本レビューで
  さらに複数箇所検出された）は数を数える形の記録がまた合わなくなる例（#22 の Decision Log で
  既知の失敗パターン）。今後同種のプランでは箇所数を明記せず「網羅した」という結果だけを
  記録する方が安全、という教訓を残す。
