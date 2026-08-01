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

- [x] AC-001: `create-requirements` の Q4 を optional「UI スケッチ」から必須「ゴール／完成イメージ」に変更し、①主要ユーザージャーニー（Mermaid）②完成時に利用者が何をできるようになるか（1〜3文）③非ゴール の3点を必須項目とし、US テンプレートに `## ゴール像` 節を追加する
- [x] AC-002: `create-spec` の Screen/UX flows を `## E2E シナリオ` 節として必須化（`(if applicable)` を外す）し、`E2E-001 → AC-001, AC-003` 形式の横断 traceability を記録させ、Completion criteria にも追加する
- [x] AC-003: `create-exec-plan` に E2E-AC を最低1本立てる規約（記法 `- [ ] AC-NNN: [E2E] ...`）を追加し、「全機能 AC が `- [x]` でも E2E-AC が緑でなければ完了ではない」を完了条件に明記する
- [x] AC-004: `run-tests` Step 3 と `pre-pr` ⑤ の AC カバレッジ確認に「E2E-AC に対応するテストが存在し緑か」を追加し、E2E-AC 未カバー時は `pre-pr` / `complete-exec-plan` を保留させる
- [x] AC-005: [E2E] `/create-requirements` → `/create-spec` → `/create-exec-plan` → `/pre-pr` を1本ウォークスルーし、ゴール像と E2E シナリオが最後まで痩せずに届くことを確認したうえで、`SKILL_FLOW.md`（§1 フロー図・§3 ギャップ表・§4 必須/任意ゲート表）と `README.md` / `README.ja.md` / `ONBOARDING.md` / `ONBOARDING.ja.md` を追従させる

## Task Breakdown

- [x] AC-001 — `.claude/skills/create-requirements/SKILL.md` の Q4（L101 付近）と US テンプレート（L189 付近）、Completion criteria を改修
- [x] AC-002 — `.claude/skills/create-spec/SKILL.md` の Step 2 セクション表（L106 付近）と Completion criteria（L144 付近）を改修
- [x] AC-003 — `.claude/skills/create-exec-plan/SKILL.md` のインタビュー Q3（L36 付近）、テンプレート（L64 付近）、Completion criteria（L94 付近）を改修
- [x] AC-004 — `.claude/skills/run-tests/SKILL.md` Step 3（L69 付近）と `.claude/skills/pre-pr/SKILL.md` ⑤（L33 付近）を改修（＋ `complete-exec-plan` Step 2）
- [x] AC-005 — 5スキルを通しでウォークスルー → `SKILL_FLOW.md` / `README.md` / `README.ja.md` / `ONBOARDING.md` / `ONBOARDING.ja.md` を追従
- [x] `/check-doc-invariants` を実行
- [ ] `/doc-review` を実行（独立エージェントによる検査）— 起動直後にユーザーが中断。未実施
- [x] `/pre-pr` を実行（PR 作成自体は人間ゲートのため未実施）

## Progress Log

### 2026-08-02
- Plan created
- AC-001 完了
- AC-002 完了
- AC-003 完了
- AC-004 完了
- AC-005 完了（機能 AC・E2E AC ともすべて `- [x]`）
- `/pre-pr` 実行。①②④ は前提ファイル不在で N/A、③ は DOC-INV-004 が 5 件（既知）、
  ⑤ は `test_strategy.md` 不在で実行不可、⑤-E2E は自動テスト不在で ❌。PR 作成は保留
- Implementation started. Branch: feat/goal-image-e2e-issue27
  （`start-feature` は AC-001 コミット後に事後実行。Step 0 / Step 2 は実行不可 — Decision Log 参照）

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

- **AC-001 done.** `create-requirements` の Q4 を optional「UI スケッチ」から必須「ゴール像」へ変更。
  Q4a（完成時にできること 1〜3文）/ Q4b（主要ユーザージャーニー、Mermaid）/ Q4c（非ゴール）を必須、
  Q4d（UI スケッチ）を optional として存置。3点が答えられない場合は勝手に埋めず停止する規定を追加
  （`/create-spec` が要件欠落時に停止するのと同じ原則）。US テンプレートは `## ゴール像` 節を
  ユーザーストーリーと受け入れ条件の間に新設し、旧 `## UI スケッチ` 節はその配下の
  `### UI スケッチ` に移動。frontmatter description / 冒頭 Purpose / What this skill does /
  Steps / Completion criteria / 最終レポートも追従。主要ファイル:
  `.claude/skills/create-requirements/SKILL.md`。
  検証: このリポジトリにテストは無いため（下記の検証戦略のとおり）DOC-INV チェックのインライン実行で確認。
  変更ファイルは `.claude/skills/**` で `check-doc-invariants` のスコープ（`docs/**` と `exec-plans/**`）外。
  スコープ内の本プランは DOC-INV-001（Markdown リンク 0 件）/ -002（`status: active`）/ -003 / -005（AA ブロック 0 件）を充足。
  他スキル・ドキュメントから旧 `## UI スケッチ` 節への構造的依存が無いことを grep で確認済み。

- **`start-feature` の Step 0 / Step 2 は実行不可（このリポジトリ固有）**。
  AC-001 コミット後に `/start-feature` を事後実行したが、次の理由で2ステップを充足できない。
  - Step 0（ベースラインテスト）: `docs/05_quality/test_strategy.md` が無く `test_command` を
    読めないため `run-tests` が起動できない。上記「本プランでは `/run-exec-plan` を使わない」と同根。
  - Step 2（必須ドキュメント読み込み）: `docs/07_ai_context/CONTEXT.md` /
    `docs/04_implementation/invariants.md` / `patterns.md` がいずれも存在しない。
    同スキルの Prerequisites（`invariants.md` の存在）自体が満たされない。
  したがって「ベースライン緑」を前提にした差分帰属（失敗が自分の変更由来か既存かの切り分け）は
  このリポジトリでは働かない。代替として各 AC のコミットを分け、変更範囲を diff で追えるようにする。
  ブランチ名は標準パターン `feature/{plan-name}` ではなく `feat/goal-image-e2e-issue27` を使用。
  参照すべき CONTEXT.md のブランチ戦略が存在せず、既存リポジトリに `feat/` `feature/` 双方の
  前例があるため、AC-001 コミット済みのブランチを改名せずそのまま継続する。

- **AC-002 done.** `create-spec` の Screen/UX flows 行を `## E2E シナリオ`（required）に置き換え、
  Step 2 に同節の書式を定義（`### E2E-NNN: {name}` ＋ Mermaid ＋ 前提 / 完了条件 / 満たす AC）。
  `E2E-NNN → AC-xxx, AC-yyy` の横断 traceability 表を必須化し、「どの E2E にも属さない AC は
  報告する」規定を追加。Step 1 に US の `## ゴール像` を読む手順と、同節が無い US（必須化前に
  書かれたもの）での停止規定を追加（AC-001 の出力を入力として受け取る接続点）。
  frontmatter description / What this skill does / Completion criteria / 最終レポートも追従。
  主要ファイル: `.claude/skills/create-spec/SKILL.md`。
  検証: 変更ファイルは `check-doc-invariants` のスコープ外。`(if applicable)` の残存が無いことを
  grep で確認（唯一の一致は「never `(if applicable)`」という否定文）。

  設計判断: 機能単位の traceability（feature → satisfies AC-002）は**下向き**で、「これら複数の
  AC が合わさって1つの通しフローになる」ことを表現できない。`E2E-NNN → AC-xxx` を**横断方向**に
  持たせることで、後段（AC-004）の `run-tests` / `pre-pr` が AC 単位のカバレッジではなく
  E2E レベルの充足を検査できるようになる。

- **AC-003 done.** `create-exec-plan` に「E2E acceptance criteria (required)」節を新設し、
  記法 `- [ ] AC-NNN: [E2E] ...`、機能 AC の後ろに配置、番号は連番継続、を規定。
  内容の出所を①仕様の `## E2E シナリオ`（`E2E-NNN` 1本につき E2E-AC 1本）②仕様を省略した
  小さな変更では US のゴール像、③どちらも無ければユーザーに直接尋ねる、の順で定義し、
  「機能 AC だけのプランを作らない」を明記。インタビューに Q3b を追加。テンプレートに
  `- [ ] AC-003: [E2E] ...` と「機能 AC が全て `- [x]` でも `[E2E]` が緑でなければ完了ではない」
  の一文を埋め込み（ファイルだけ読む後続セッションにも伝わるようにするため）。
  frontmatter description / What this skill does / Steps / Completion criteria / 最終レポートも追従。
  主要ファイル: `.claude/skills/create-exec-plan/SKILL.md`。
  検証: スキル内の AC 例文5行に spec-gate の `AC-(\d{3}):` を適用し、全て認識され、
  `[E2E]` の3行がマーカーで判別できることを確認。変更ファイルは `check-doc-invariants` のスコープ外。

- **AC-004 done.** `run-tests` Step 3 を「機能 AC と `[E2E]` AC を分けて報告」に変更し、
  E2E は「テストが存在する」だけでなく「今回パスしたテストに含まれる」ことまで確認する規定に。
  プランに `[E2E]` AC が1本も無い場合は報告のみ行い、ここで AC を作文しない（統治ゲートの維持）。
  `pre-pr` ⑤ に E2E カバレッジ検査を追加し、未カバー／失敗は PR 作成をブロック。結果報告に
  `⑤-E2E` 行を追加。両スキルの Completion criteria も追従。
  主要ファイル: `.claude/skills/run-tests/SKILL.md`, `.claude/skills/pre-pr/SKILL.md`。

  併せて `.claude/skills/complete-exec-plan/SKILL.md` Step 2 にも E2E 検査を追加した
  （AC-004 の文言が「`pre-pr` / `complete-exec-plan` を保留させる」と両方を対象にしているため。
  Task Breakdown には run-tests / pre-pr しか書いていなかったので、ここに追記して差分を明示する）。

  検証: `run-tests` が行う分類（`- [ ] AC-NNN: [E2E] ...` を接頭辞で判定）を本プランに適用し、
  機能 AC-001〜004 と E2E AC-005 に正しく分かれること、E2E 未チェックが検出されることを確認。
  なお最初に書いた検証スクリプトは節の分割を `split('##')` で行ったため AC 本文中の
  `## ゴール像` で切れて誤検出した。行頭見出し（`^## `）で分割して再実行し、上記の結果を得た。
  スキル側は AC 行の走査をエージェントに委ねており、この誤りはスクリプト固有のもの。

- **AC-005 done（[E2E]）.** ウォークスルーで 9 項目を検査し全て PASS。
  ①ゴール像3点が必須で書かれる ②`create-spec` が同じ節名を読み、無ければ停止する
  ③E2E シナリオ節と横断 traceability が必須 ④`create-exec-plan` が spec の E2E を `[E2E]` AC にする
  ⑤記法が spec-gate の `AC-(\d{3}):` で認識される ⑥`run-tests` がマーカーで分類し「存在＋緑」まで確認する
  ⑦`pre-pr` が未カバーで PR をブロックする ⑧`complete-exec-plan` が未緑で完了を保留する
  ⑨どの段でも AC を勝手に作文しない（統治ゲート維持）。
  節名（`## ゴール像` / `## E2E シナリオ`）とマーカー（`[E2E]`、全43箇所）の表記ゆれが無いことも確認。
  ドキュメント追従: `SKILL_FLOW.md`（§1 の REQ/SPEC/PLAN/PREPR/COMPLETE ノード、§3-6 を新設して
  G-F を Resolved として記録、§4 に「スキル内でのブロッキング」の注記）、`README.md` / `README.ja.md`
  （フロー図・スキル一覧表）、`ONBOARDING.md` / `ONBOARDING.ja.md`（全体の流れ・スキル使い分け表）。

  **この [E2E] AC は自動テストではなくウォークスルーで検証した**。AC-004 で「E2E AC はテストが
  存在し緑であること」を規定した直後の逸脱にあたるため明示しておく。理由はテンプレート本体に
  テストスイートが無いこと（本プラン冒頭の検証戦略のとおり）。検証は上記9項目の機械的検査として
  再実行可能な形にしてある。テンプレートを適用した実プロジェクト側では、この逸脱は発生しない。

  ウォークスルーの過程で確認した副次的事実: `run-exec-plan` は `[E2E]` AC を特別扱いしないが、
  E2E AC を機能 AC の後ろに置く規約により最後に処理され、かつ Step 3 で呼ぶ `run-tests` が
  E2E 未カバーを保留するため、driver が E2E AC を実テスト無しにチェックすることはできない。
  よって Ph1 の範囲で `run-exec-plan` の改修は不要（driver へのゴール伝達自体は #23/#25 の担当）。

- **`/pre-pr` 結果: ⑤-E2E が ❌ で、規定どおりなら PR 作成はブロックされる。**
  AC-004 で「`[E2E]` AC はテストが存在し緑であること。未カバーは PR をブロック」と定めた当の
  ゲートに、本ブランチ自身が抵触している。理由は AC-005 の記録どおり、テンプレート本体に
  テストスイート（`docs/05_quality/test_strategy.md` および実テスト）が存在しないため。
  自動テストの代わりに 9 項目のウォークスルー検査を実施し PASS しているが、これは規定が要求する
  「テストが存在し緑」ではない。**この例外を認めて PR に進むかは人間の判断**であり、pre-pr が
  自動で通してよいものではない（統治ゲートを自分で緩めない）。
  なお、この矛盾はテンプレート本体に固有のもので、テンプレートを適用した実プロジェクトでは
  `test_strategy.md` と実テストが存在するため発生しない。

- **DOC-INV-004（AC traceability）はこのリポジトリでは構造的に充足できない**。
  同 INV は「exec-plan の各 AC-NNN が、`ac_ids:` にその ID を含む US ファイルに対応すること」を
  求めるが、テンプレート本体には `docs/01_requirements/` が存在しない（`init-project` が生成する側のため）。
  本プランの AC-001〜005 に US の裏付けは付けられない。要件の追跡は GitHub issue #27 / #28 で代替する。
  `/pre-pr` 実行時にも同じ違反が出る見込みであり、これは既知・意図的な逸脱として扱う。

- **`docs/07_ai_context/CONTEXT.md` の更新はスキップ**。
  `create-exec-plan` の Step 5 は CONTEXT.md の優先タスク更新を求めるが、このリポジトリには
  `docs/` が存在しない（`init-project` が生成する側のテンプレート本体のため）。対象ファイルが
  無いため実行不能。追跡は GitHub issue #27 / #28 側で行う。
