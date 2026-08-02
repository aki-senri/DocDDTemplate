---
status: active
created: 2026-08-02
completed:
---

# ac-sources-reanchor

## Goal & Scope

exec-plan の AC 1行に凝縮された目標を、自走 driver に**太いまま**届ける。各 AC が凝縮した起点
（US の検証可能な bullet / spec の該当節 / `E2E-NNN`）をプランに `## Sources` として明示し、
driver がテスト起草前にそれを読み、緑判定の前に spec の該当節へ再アンカーする。
GitHub issue #23 (G-B) と #25 (G-D) の解消。両者は「既にある情報が driver に届かない」という
同一の欠落の入口側と出口側であり、親トラッキング #28 が統合実施を指示している（Ph4）。

## Acceptance Criteria

- [x] AC-001: 単一ソース `.claude/skills/create-exec-plan/ac-sources.md` が存在し、①適用範囲
      （どの AC が起点を持ち、何を起点として認めるか）②exec-plan の `## Sources` 表の書式
      ③起点と AC 行が食い違うときの4分岐（詳細化 / 別の成果 / 矛盾 / 起点なし）と各措置
      ④2つの用途（テスト起草時の参照集合・緑判定時の spec 再アンカー）⑤spec 再アンカーの手順と
      判定 ⑥呼び出し地点ごとの措置表 ⑦適用外 の7項目すべてを定義した状態にする
- [x] AC-002: `create-exec-plan` が起票時に各 AC の起点を聞き取り、生成するプランに `## Sources`
      表として書く状態にする（インタビュー質問・テンプレート・Steps・Completion criteria に
      組み込まれ、起点の無い AC は空欄でなく `n/a（理由）` と書かれることが本文で読める）
- [x] AC-003: `run-exec-plan` が、対象 AC のテストを起草する**前**に `## Sources` の指す US bullet と
      spec 該当節を読む状態にする（Step 1 と Step 2a の間に置かれ、起点が AC 行と矛盾する場合・
      AC が扱っていない別の成果を述べている場合は停止条件 (a) で HALT することが定義されている）
- [x] AC-004: `run-exec-plan` が AC のチェックボックスを `- [x]` にする**前**に spec 該当節との
      照合を行う状態にする（Step 3 の検証項目として、照合 OK / 実装が spec に反する / spec が AC と
      矛盾 / 起点なし の各分岐の措置が定義され、照合結果が `AC-NNN done` の記録に含まれる）
- [x] AC-005: `red-first.md` の起草手順の参照集合が「AC 本文のみ」から「AC 行とその起点
      （`ac-sources.md`）」に変わった状態にする（手順表と「Transcription, not invention」が追従し、
      実装コードを参照しないという制約と、起点にも無い期待結果を発明したら停止する規定が残っている）
- [x] AC-006: `start-feature` の Step 2 が、選択したプランの `## Sources` が指す US / spec を
      読み込み対象に含める状態にする
- [x] AC-007: `pre-pr` が `## Sources` の欠落と spec 再アンカー記録の欠落を確認して報告する
      状態にする（⚠️ 報告であり PR をブロックしない）
- [x] AC-008: `docode-review` の独立エージェントが、差分を AC 行だけでなくプランの `## Sources` が
      指す US bullet と spec 該当節に照らして判定する観点を持った状態にする
- [x] AC-009: `promote-spec` が生成する reconcile プランのテンプレートに `## Sources` 表があり、
      再オープンした AC の起点が新 spec の該当節と `E2E-NNN` を指す状態にする
- [x] AC-010: `check-doc-invariants` の DOC-INV-001 参照方向表で exec-plans が `docs/02_spec/` を
      参照できる状態にする（レイヤ番号・「May reference」列・Step 4 のレイヤ対応表が追従し、
      exec-plan から spec の該当節への参照が違反として報告されない）
- [x] AC-011: `CLAUDE.md` / `SKILL_FLOW.md` / `README.md` / `README.ja.md` / `ONBOARDING.md` /
      `ONBOARDING.ja.md` のいずれにも、driver が exec-plan の AC 1行だけで操舵・緑判定するという
      導入**前**のフロー記述が残っていない状態にする（内側ループの図・表・手順に起点参照と
      spec 再アンカーが反映され、`SKILL_FLOW.md` の G-B / G-D 行が解消として記録されている）
- [x] AC-012: 本プランの変更を `process-walkthrough.md` の手順で **6周**（happy / 2周目 / 再開 /
      免除 / ゲート境界 / 成功時）辿った結果が、周回名・所見・修正を伴って Decision Log に記録され、
      修正後に全周 PASS である

> 本プランは documentation-only（変更対象は `.claude/skills/**` と `*.md` のみ）のため
> `[E2E]` AC を持たない。Decision Log の `E2E: n/a (documentation-only)` を参照。

## Sources

| AC | 起点 |
|----|------|
| AC-001〜AC-012 | `n/a（テンプレートリポジトリ自身の規約変更であり、US / spec を持たない。起点は GitHub issue #23 / #25 と親トラッキング #28）` |

## Task Breakdown

- [x] AC-001 — `.claude/skills/create-exec-plan/ac-sources.md` を新規作成
- [x] AC-002 — `.claude/skills/create-exec-plan/SKILL.md`（Q2b・テンプレート・Steps・完了条件）
- [x] AC-003 — `.claude/skills/run-exec-plan/SKILL.md` に Step 1b を追加
- [x] AC-004 — 同 SKILL.md の Step 3 に spec 再アンカーを追加
- [x] AC-005 — `.claude/skills/run-tests/red-first.md` の参照集合を更新
- [x] AC-006 — `.claude/skills/start-feature/SKILL.md` の Step 2
- [x] AC-007 — `.claude/skills/pre-pr/SKILL.md` に ⑤c を追加
- [x] AC-008 — `.claude/skills/docode-review/SKILL.md` の観点 1e
- [x] AC-009 — `.claude/skills/promote-spec/SKILL.md` Step 7 のテンプレート
- [x] AC-010 — `.claude/skills/check-doc-invariants/SKILL.md` の DOC-INV-001
- [x] AC-011 — `CLAUDE.md` / `SKILL_FLOW.md` / `README*.md` / `ONBOARDING*.md`
- [x] AC-012 — 6周の照合を実施し Decision Log に記録
- [x] `/check-doc-invariants` を実行
- [x] `/pre-pr` を実行（PR 作成自体は人間ゲート）

## Progress Log

### 2026-08-02
- Plan created
- AC-001〜AC-012 完了
- `/check-doc-invariants` を実行

## Decision Log

### 2026-08-02

- **E2E: n/a (documentation-only)**。変更対象はスキル定義とルート直下の `*.md` のみで、機能を
  実装するファイルを含まない（`git diff --name-only` で確認できる）。
- **AC readiness: all 12 ACs READY**（`create-exec-plan` Q3c 相当）。R4 は documentation-only の
  ため n/a（`ac-readiness.md`「Documentation-only plans」）。R1/R2/R3/R5 は全 AC で充足。
- **red-first: n/a (documentation-only)**。テストハーネスが無く、`[E2E]` AC も持たない
  （`red-first.md`「Where it does not apply」）。AC-012 は record-producing AC としても免除に該当する。
- **process walkthrough が必要**（`process-walkthrough.md` の適用範囲）。本プランは内側ループ・
  停止条件・ゲート・単一ソースに触れるため、記述照合ではなく6周辿る AC-012 を置いた。
- **#23 と #25 を1プランに統合した理由**: 親トラッキング #28 が Ph4 として「統合して実施」を
  指示している。両者は driver が exec-plan の AC 1行しか読まないという同一の欠落の入口側
  （起草時に痩せた目標を受け取る）と出口側（緑判定を spec に照らさない）であり、片方だけを
  直すと `## Sources` 表を作って誰も読まない／読む先が無いのに照合を求める、のどちらかになる。

- **単一ソースの置き場所を `create-exec-plan/ac-sources.md` にした理由**: 表を書くのは起票時であり、
  `ac-readiness.md` / `process-walkthrough.md` と同じディレクトリに並ぶ。読む側が
  `run-exec-plan` に寄っている点は `red-first.md`（`run-tests/` にあって6地点が参照する）と同じ形。

- **AC-001 done.** `.claude/skills/create-exec-plan/ac-sources.md` を新規作成。7項目（適用範囲 /
  表の書式 / 食い違いの4分岐 / 2つの用途 / 再アンカーの手順と判定 / 呼び出し地点 / 適用外）を定義。
  spec 再アンカー: n/a（このリポジトリ自身の規約変更で spec を持たない）。
- **AC-002 done.** `create-exec-plan/SKILL.md` に Q3d・`## AC sources` 節・テンプレートの
  `## Sources`・Steps 2b・完了条件・報告書式を追加。Q3d は Q3c（readiness）より**前**に置いた
  — R4 の E2E アンカー判定は、どの `E2E-NNN` を凝縮したか分かっていないと推測になるため。
  spec 再アンカー: n/a（起点なし）。
- **AC-003 done.** `run-exec-plan/SKILL.md` に Step 1b（起点を読む）を Step 1 と Step 2a の間に追加。
  詳細化／別の成果／矛盾／`n/a`／表が無い の5分岐を定義し、別の成果と矛盾を HALT (a) に接続。
  Step 0c（`[E2E]`）にも起点読み取りと矛盾時の HALT 行を追加。spec 再アンカー: n/a（起点なし）。
- **AC-004 done.** 同 SKILL.md の Step 3 に検証項目4を、Step 3a として spec 再アンカーを追加
  （5判定 ＋ 「この AC の寄与に限定する」注記）。Step 3b の Decision Log 記録に
  `spec 再アンカー:` 行を必須化し、Retry budget・停止条件 (a)・Completion criteria・
  Design principle の内側/外側表・報告書式を追従。spec 再アンカー: n/a（起点なし）。
- **AC-005 done.** `run-tests/red-first.md` の手順表 step 1/2 と「Transcription, not invention」を
  「AC 行とその起点」に更新し、**実装コードへは広げない**ことを明記。記録書式・R2 との関係・
  Step 2a の呼び出し地点行も追従。spec 再アンカー: n/a（起点なし）。
- **AC-006 done.** `start-feature/SKILL.md` Step 2 の読み込み表に `## Sources` の指す文書を追加し、
  食い違い時は人に提示（HALT ではない）ことを明記。実装順ガイド・完了条件・報告も追従。
  spec 再アンカー: n/a（起点なし）。
- **AC-007 done.** `pre-pr/SKILL.md` に ⑤c（`## Sources` の有無 ＋ 再アンカー記録の有無、⚠️ のみ）を
  追加。「ここで表を埋めない」＝事後の補完はコードからの推測になる、を明記。
  spec 再アンカー: n/a（起点なし）。
- **AC-008 done.** `docode-review/SKILL.md` の観点1に「起点に照らして判定する」を追加し、
  Step 1 で起点の本文をプロンプトに貼ること（subagent は文脈を継承しないため）、Step 2 の
  スコープ表、description を追従。spec 再アンカー: n/a（起点なし）。
- **AC-009 done.** `promote-spec/SKILL.md` Step 7 の reconcile テンプレートに `## Sources` を追加し、
  **昇格後**の spec 節を指すこと（旧節を指すと Step 3a の再アンカーが置き換わった振る舞いを
  「正しい」と追認してしまう）を明記。完了条件も追従。spec 再アンカー: n/a（起点なし）。
- **AC-010 done.** `check-doc-invariants/SKILL.md` の DOC-INV-001 で exec-plans を **1.5 → 2.5** に
  移し、参照可能範囲を「Layers 1–2」に変更。Step 2 のレイヤ対応表も追従。
  1.5 のままでは、規約が要求する `## Sources`（spec 節への参照）が DOC-INV-001 違反になっていた。
  spec 再アンカー: n/a（起点なし）。
- **AC-011 done.** `CLAUDE.md`（内側/外側表・停止条件 (a)・red-first 節・新設「AC の起点」節・
  再開状態の記録書式・テスト作成順・スキル一覧）、`SKILL_FLOW.md`（フロー図に SOURCES /
  REANCHOR ノード、pre-pr ⑤c、呼び出し関係表、共有参照ファイル注記、§4 のブロック方針、
  G-B / G-D 行）、`README.md` / `README.ja.md`（クイックスタート・スキル表・新節）、
  `ONBOARDING.md` / `ONBOARDING.ja.md`（責任分担表・全体フロー・手動ループ・red-first 節・
  新節・INV-T02 文面）を追従。spec 再アンカー: n/a（起点なし）。

- **AC-012 process walkthrough**: 本プランが変更した内側ループ・停止条件・ゲート・単一ソースを
  `process-walkthrough.md` の手順で6周辿った（happy / 2周目 / 再開 / 免除 / ゲート境界 / 成功時）。
  検出 5 件、いずれも修正済み:
  - **happy（Step 3 内の順序）**: Step 3 の検証項目1（`run-tests`）は緑の分岐で
    「continue to Step 3b」と書いており、新設した項目4（Step 3a 再アンカー）を**飛び越えて**
    チェックボックスに到達できた（contradictory verdicts: 項目4 は「3b の前に必ず走る」と述べる）
    → 分岐の行き先を「item 2」に直し、「4項目は順に走り、Step 3b へは項目4 を通ってのみ到達する」
    を Step 3 冒頭に明記。
  - **2周目**: Step 3a で「測定の穴」を埋めるために追加したテストは、処理中の AC に対する
    red-first 記録を持ちその AC は未チェックのままなので、`run-tests` Step 2c の定義上
    **expected red** に分類される。その結果 Step 3 の「expected red だけなら緑扱い」経路が発火し、
    **赤いテストを抱えたまま Step 3b がチェックボックスを付ける**（success treated as anomaly の逆・
    穴の見逃し）→ Step 3 の該当箇所に「いま処理中の AC に属する expected red は緑扱いにしない」
    を明記して修正。
  - **再開**: functional AC の red-first 記録があり未実装のまま中断したプランを再開すると、
    Step 2a には Step 0c にある「前のセッションが既に置いた場合」分岐が無く、driver は
    凍結済みテストを書き直すことになる（self-violating entry condition）→ Step 2a に
    「再実行して同じ赤を確認、書き直さない」分岐を追加。
  - **成功時**: 最後の `[E2E]` AC が緑になった瞬間の Step 3a で、`E2E-NNN` 節は常に複数の AC
    （`満たす AC: AC-001, AC-003, AC-005`）を述べるため、その節が語る振る舞いのうち他 AC 由来の
    部分を「spec の振る舞いを満たしていない」と読み、**成功した瞬間に HALT** し得た
    （success treated as anomaly）→ Step 3a に「照合はこの AC の寄与に限定する」注記を追加。
  - **happy（起票→自走のゲート境界）**: `ac-readiness.md` R2 は「AC 本文だけからテストを書けるか」
    を問うのに対し、Step 2a は「AC 行と起点から」転記するようになり、**同じ AC に対して
    Q3c と Step 2a が違う判定を出す**（contradictory verdicts）。起点に詳細が正しく記録された
    痩せた1行が Q3c で NOT READY になる → R2 の判定材料を「AC 行とその起点」に揃え、
    起点が `n/a`／表が無い場合は従来どおり AC 行のみで判定する、と明記。
  - 免除周回（全行 `n/a` の documentation-only）とゲート境界（`spec-gate.py` の `AC-(\d{3}):`、
    DOC-INV-004 の `- [ ] AC-NNN:`、DOC-INV-006 の `[E2E]` 検出、`promote-spec` → reconcile →
    `start-feature`）は所見なし。表の中で `AC-NNN` の直後にコロンを置かない規約により、
    `## Sources` が AC として誤検出されないことを本プラン自身の12件で確認済み。
  - 修正後、全6周 PASS。
  spec 再アンカー: n/a（起点なし）。

- **red-first 免除の再確認**: AC-012 は `red-first.md`「record-producing AC」（成果物が記録そのもの）
  にも該当するため、documentation-only 免除と二重に適用外。

- **AC-012 追加照合（PR #32 push 後・全文横断）**: このテンプレート自身をレビューするスキルが無い
  ため、単一ソースと呼び出し地点の突き合わせを手作業で1周した。6周照合で見落としていた
  矛盾 6 件を検出し、すべて修正:
  1. **単一ソースの自己矛盾**: `ac-sources.md` の呼び出し地点表が `create-exec-plan (Q2b)` と
     書いており、実際のスキル・CLAUDE.md・SKILL_FLOW（いずれも **Q3d**）と食い違っていた。
     同表の `Step 3, verification` も実体名 `Step 3a` に統一。
     （`2026-08-ac-readiness-gate.md` で一度起きたのと同型の drift）
  2. **readiness ゲートが起点より先に走る（`run-exec-plan` Step 0b）**: R2 の判定材料を
     「AC 行＋起点」に変えたのに、起点を読むのは Step 1b（AC ごと・後）。Step 0b は全 AC を
     まとめて検査するため、1行だけで NOT READY を出して**ループが始まらない**。
     → Step 0b に「表を先に読む」を明記（`n/a`／表なしは AC 行のみで判定）。
  3. **同じ問題が `start-feature`**: Step 1b（readiness）が Step 2（起点の読み込み）より前。
     → Step 1b に同じ but 人間パス向けの注記を追加。
  4. **`doc-review` が他ゲートと違う判定を返す**: §2 は「他の3地点と一致する判定を出す」と
     述べつつ、Step 2 で US を推測的にしか読まず spec は読まない。R2 を1行だけで判定するため
     構造的に厳しい verdict になる → Step 2 の収集コマンド・プロンプトの
     `### AC sources` ブロック・§2 本文に、起点を渡して R2 をそれに対して判定する旨を追加。
  5. **`red-first.md` と新ルールの衝突**: expected red 表の「Per-AC verification inside the loop」
     行が「処理中の AC にとっての緑の代替」と読めたが、Step 3 に追加した規則は
     「処理中の AC 自身の expected red は緑扱いにしない」。単一ソース側を修正し、
     「他の AC に属する赤のみ」と明記。
  6. **`create-exec-plan` 内の順序不一致**: 「What this skill does」が sources→readiness→process、
     「Steps」が process→sources→readiness の順で書かれていた → Steps 側（正しい順序）に統一。
  あわせて、インタビュー表が Q3c 行と Q4 行の間に置かれた引用注記でテーブルとして分断されて
  いた（Q4 が表の外にレンダリングされる）ため、Q4 を表内に戻し注記を表の後ろへ移動。
  これは本 PR 以前からの書式不具合。
  検証: 全 md の相対リンク解決（0 件の破損）、run-exec-plan の Step 名参照の突き合わせ、
  表分断の機械検出（0 件）、13 項目の存在確認。
