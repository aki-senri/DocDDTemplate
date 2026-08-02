---
status: completed
created: 2026-08-02
completed: 2026-08-02
---

# ac-readiness-gate

## Goal & Scope

AC の testability（測定可能性）を、ループ内の主観判断から**ループ前の構造検査**へ前倒しする。
共通の「AC readiness 基準」を単一ソースとして新設し、`create-exec-plan`（起票時）/ `start-feature`（手動パス）/
`run-exec-plan` Step 0b（自走前）の3ゲートで同じ基準を適用する（加えて `doc-review` が同じ基準で助言する）。
GitHub issue #24 (G-C) の解消。
親トラッキングは #28 で、本プランはその Ph2（#27 の次）にあたる。

## Acceptance Criteria

- [x] AC-001: AC readiness 基準を単一ソース `.claude/skills/create-exec-plan/ac-readiness.md` として新設する。5観点（①観測可能な単一結果 ②given-when-then で書ける ③成功指標が具体 ④どの E2E シナリオのどのステップに効くか名指しできる ⑤what であって how でない）、判定（READY / ⚠️ / NOT READY）、`[E2E]` AC への適用差、documentation-only の免除範囲、および呼び出し地点ごとの措置表を定義する
- [x] AC-002: `create-exec-plan` のインタビューに readiness チェック（Q3c）を追加し、Steps・Completion criteria・最終報告書式に「全 AC が READY（⚠️ は理由を Decision Log に記録）でなければプランを確定しない」を組み込む
- [x] AC-003: `run-exec-plan` の Step 0 に "AC readiness gate" を追加し、ループ開始前に全未チェック AC を検査する。NOT READY があれば**ループを開始せず**停止条件 (a) で HALT し、判定結果を Decision Log に記録する。停止条件表・What this skill does・Completion criteria を追従させる
- [x] AC-004: `start-feature` に readiness 確認ステップを追加し、手動パスでも同じ基準で検査する。人が同席するパスのため NOT READY は「提示して人が判断」とし、AC-001 の措置表と一致させる
- [x] AC-005: `doc-review` の「2. Acceptance criteria quality」を `ac-readiness.md` の5観点を参照する形に揃え、レビュー観点が独自定義へドリフトしないようにする（optional スキルのため判定は助言のまま）
- [x] AC-006: `CLAUDE.md` / `SKILL_FLOW.md` / `README.md` / `README.ja.md` / `ONBOARDING.md` / `ONBOARDING.ja.md` のいずれにも、readiness ゲート導入**前**のフロー記述が残っていない（＝AC の測定可能性検査が存在しないフロー図・スキル表・停止条件 (a) の旧文面が1件も無い）状態にする<br>※ 起票時は「各ドキュメントを追従させる」と活動形で書いていたが、AC-007 の dogfooding で R1 違反（活動の記述）と判定されたため、単一の観測可能な終状態に書き直した（Decision Log 参照）
- [x] AC-007: 痩せた AC を含むプラン例で `/create-exec-plan` → `/start-feature` → `/run-exec-plan` の3ゲートを照合した結果が Decision Log に記録され、(a) 同じ AC が3ゲートで同じ判定になること、(b) 措置だけが「書き直し／人に確認／HALT」と分かれること、(c) documentation-only の扱いが3ゲートで一致することを含む全項目が PASS である<br>※ 起票時は `[E2E]` AC として書いていたが、`2026-08-reconcile.md` の AC-003 で「documentation-only プランは `[E2E]` AC を置かない」と規約を変更したため、通常の機能 AC に書き直した（Decision Log 参照）

> 本プランは documentation-only（変更対象は `.claude/skills/**` と `*.md` のみ）のため
> `[E2E]` AC を持たない。Decision Log の `E2E: n/a (documentation-only)` を参照。

## Task Breakdown

- [x] AC-001 — `.claude/skills/create-exec-plan/ac-readiness.md` を新規作成
- [x] AC-002 — `.claude/skills/create-exec-plan/SKILL.md` のインタビュー表・Steps・Completion criteria・報告書式を改修
- [x] AC-003 — `.claude/skills/run-exec-plan/SKILL.md` の Step 0・停止条件表・Completion criteria を改修
- [x] AC-004 — `.claude/skills/start-feature/SKILL.md` に readiness 確認ステップを追加
- [x] AC-005 — `.claude/skills/doc-review/SKILL.md` §2 を単一ソース参照に変更
- [x] AC-006 — `CLAUDE.md` / `SKILL_FLOW.md` / `README*.md` / `ONBOARDING*.md` を追従
- [x] AC-007 — 3ゲート照合を実施し Decision Log に記録
- [x] `/check-doc-invariants` を実行
- [x] `/pre-pr` を実行（PR 作成自体は人間ゲート）

## Progress Log

### 2026-08-02
- Plan created
- AC-001 完了
- AC-002 完了
- AC-003 完了
- AC-004 完了
- AC-005 完了
- AC-006 完了
- AC-007 完了（照合14項目 PASS）
- `/check-doc-invariants` 実行。DOC-INV-004 が 7 件（既知・本テンプレートに docs/01_requirements が
  無いため構造的に充足不能）。他は PASS または N/A
- `/pre-pr` 実行。①②④ は前提ファイル不在で N/A、③ は上記の既知違反のみ、⑤ は test_strategy.md 不在で
  実行不可。E2E カバレッジは「プランに [E2E] AC が無い」＝ ⚠️ 報告のみでブロックしない
  （documentation-only。規約変更前は ❌ 保留だった — Decision Log 参照）。PR 作成は人間ゲートのため保留

- PR #30 作成（reconcile と合同）。マージ後に `/complete-exec-plan` を実行する
- PR #30 のレビュー対応（Copilot 3 件のうち 2 件が本プラン分）
- PR #30 マージ済み（`67d90c6`）。全 AC 充足のため completed へ移行

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

- **AC-006 done.** CLAUDE.md に「AC readiness（自走前の測定可能性ゲート）」節を新設し4地点の措置表を
  記載、停止条件 (a) を「ループ前に検出・ループ中は backstop」に更新、スキル一覧3行を追従。
  `SKILL_FLOW.md` は §1 の PLAN / SF / DRIVER / DR ノード、§2 の共通参照ファイル注記、§3-6 の G-C 行
  （G-F は #27 マージ済みのため ✅ Resolved に更新）、§4 のブロッキング注記を更新。
  README（en/ja）・ONBOARDING（en/ja）のフロー・スキル表・責任分担表・最小セット説明も追従。
- **`pre-pr` には readiness を入れない**。readiness は「実装前に測定可能か」を問うゲートであり、
  実装完了後に回しても是正の余地がない（AC を書き直せば実装もやり直しになる）。PR 前の照合は
  既存の AC カバレッジ／E2E カバレッジが担う。

- **AC-007 done（[E2E]）.** 3地点ウォークスルーを実施。documentation-only プランのため
  （`git diff --name-only` は `.claude/skills/**` と `*.md` のみ）、`create-exec-plan` の
  documentation-only 免除に従い、再現可能な検査項目の実行結果をもって検証とする。検査14項目すべて PASS。

  | # | 検査項目 | 結果 |
  |---|---------|------|
  | 1 | 単一ソース `ac-readiness.md` が存在し、4地点すべてから到達できる（相対リンクの解決先が正しい） | PASS |
  | 2 | どの地点も5観点を再定義していない（定義は単一ソースにのみ存在。各スキルは verdict 名と「⚠️ は R3・R4 のみ」の要約だけを持つ） | PASS |
  | 3 | 痩せた AC 例「エラー処理を改善し、リトライ機構を Repository 層に追加して適切にハンドリングする」が3地点とも NOT READY（R1・R2・R5）になる | PASS |
  | 4 | 判定は同一で措置だけが分岐する（create=書き直し／start=人に確認／run=HALT）。3ファイルの文言が一致 | PASS |
  | 5 | `start-feature` の「このまま進む」は後段を清算せず、`run-exec-plan` は依然 HALT する旨が両側に書かれている | PASS |
  | 6 | documentation-only 免除は R4 のみ・単一ソースにのみ定義され、3地点が独自の免除を作っていない | PASS |
  | 7 | 停止条件 (a) の記述が `run-exec-plan` と CLAUDE.md で一致（ループ前に検出・ループ中は backstop） | PASS |
  | 8 | ループ中の曖昧さ判定（Step 1）が backstop として残っている（事前ゲートで置き換えて消していない） | PASS |
  | 9 | 3スキルの最終報告書式に Readiness 行がある | PASS |
  | 10 | 3スキルの Completion criteria に readiness 項目がある | PASS |
  | 11 | `SKILL_FLOW.md` の PLAN / SF / DRIVER / DR ノードが実際のステップ順と一致する | 修正後 PASS（下記） |
  | 12 | CLAUDE.md の4地点表と `ac-readiness.md` の call-site 表が一致 | **当初 PASS と記録したのは誤り** → FAIL、修正後 PASS（後述の矛盾チェック 1） |
  | 13 | `doc-review` の独立エージェント（セッション文脈なし）に基準本文が届く（Step 2 の `cat` ＋ プロンプト埋め込み） | PASS |
  | 14 | 本プラン自身の AC を新ゲートにかける（dogfooding） | 修正後 PASS（下記） |

- **11 で見つかった不整合**。`SKILL_FLOW.md` の SF ノードで readiness を ② に置いたが、
  `start-feature` の実順序は baseline → プラン選択 → readiness（Step 1b）であり、
  「AC を読む前に AC を検査する」図になっていた。② を「Select the exec-plan (AC)」、
  ③ を readiness に修正。

- **14（dogfooding）で見つかった不整合**。本プランの AC-001〜005 / 007 は READY だったが、
  **AC-006 が R1（単一の観測可能な結果）で NOT READY** と判定された。「6つのドキュメントを
  追従させる」は活動の記述であり、どこまでやれば緑かが AC 本文から決まらない。
  `create-exec-plan` が起票時にやるべきだった措置（＝人と書き直す）を事後に適用し、
  「readiness ゲート導入前のフロー記述が1件も残っていない状態」という単一の観測可能な終状態へ
  書き直した。実装内容は変えていない（既に達成済みの状態を、判定可能な言葉で言い直しただけ）。
  この観点は本テンプレートで頻出する「ドキュメント追従 AC」全般に効くため、基準を緩めるのではなく
  書き方を正す側で解決した。

- **reconcile プランの扱い**。`promote-spec` が起こす reconcile プランは `create-exec-plan` の
  インタビューを通らないため Q3c を経ない。この経路は `start-feature` Step 1b と
  `run-exec-plan` Step 0b が受け止める（`start-feature` 本文に「NOT READY がここで出る典型」として明記）。
  `promote-spec` 側に readiness を追加しなかったのは、reconcile の AC が既存 spec の AC-ID の
  再オープンであり、AC 本文の作成地点ではないため。

- **`/check-doc-invariants` の結果（2026-08-02）**。DOC-INV-001 は exec-plan に Markdown リンクが無く PASS。
  002 / 003 は `docs/` 不在で N/A。**DOC-INV-004 は AC-001〜007 の 7 件が違反**（本テンプレートには
  `docs/01_requirements/` が存在せず、`ac_ids:` を持つ US を作れない）。#27 と同じ既知・意図的な逸脱で、
  要件の追跡は GitHub issue #24 / #28 が代替する。005 は AA 図なしで PASS。006 は `[E2E]` の AC-007 が
  存在するため PASS。
- **`/pre-pr` の結果（2026-08-02）**。① invariants: N/A（`docs/04_implementation/invariants.md` 不在）、
  ② doc-freshness: N/A（`tracks:` を持つドキュメント不在）、③ doc-invariants: 上記の既知 7 件のみ、
  ④ review_checklist: N/A（ファイル不在）、⑤ run-tests: 実行不可（`docs/05_quality/test_strategy.md` 不在。
  本リポジトリはスキル定義のドキュメントのみで自動テスト基盤を持たない）。`[E2E]` の AC-007 は
  documentation-only 免除により再現可能なウォークスルー（14 項目 PASS）で検証済み。⑥ exec-plan: 更新済み。
  PR 作成は不可逆・外向き操作のため人間ゲートとして保留。
- **`create-requirements` / `promote-spec` / `pre-pr` に readiness を適用しない理由**を
  `ac-readiness.md` に「Where it is deliberately not applied」として明記した。適用地点の非対称性は
  意図的であり、レビュー時に抜け漏れと誤読されないようにするため。

- **矛盾チェック（テンプレート全体の自己照合、2026-08-02）**。レビュー用スキルが無いため、
  #24 の変更と #27 で入った E2E ゲート群を手作業で突き合わせた。検出4件のうち自分で入れた3件を修正。

  1. **AC-007 の検査項目 12 は誤って PASS と記録していた（訂正）**。`ac-readiness.md` の call-site 表は
     `create-exec-plan` を **Q3d**、`run-exec-plan` を **Step 0** と書いており、実際のスキル
     （Q3c / Step 0b）および CLAUDE.md・SKILL_FLOW の表と食い違っていた。Q3d→Q3c の変更を
     `SKILL.md` 側にだけ適用し、単一ソース側に反映し忘れたのが原因。単一ソースが参照先の
     ラベルを誤っていたため、実害は「読者が節を探せない」だが、**単一ソース化の目的そのものを
     損なう種類の誤り**なので重く扱う。修正済み。項目 12 の判定は PASS → FAIL→修正後 PASS に訂正。
  2. **`ac-readiness.md` 内の自己矛盾**。判定節は「documentation-only は R4 を n/a とし ⚠️ にしない」と
     書いているのに、報告書式の例が `⚠️ R4 — E2E 未定義（documentation-only）` になっていた。
     例を R3 のケースに差し替え、あわせて「documentation-only プランが `[E2E]` AC を定義している場合は
     n/a ではなくその AC にアンカーする」を明記（本プラン自身がその状態であり、dogfooding の判定と
     規則が食い違っていた）。
  3. **⚠️ の理由を誰が言えるかが未定義だった**。⚠️ は「正当な理由が述べられている場合」に通すが、
     自走ループにはその理由を作る資格がない（AC を書き換えられないのと同じ理由）。
     `ac-readiness.md` に「run-exec-plan は理由を著述できない。Decision Log に既に記録されている
     場合のみ ⚠️ を通過とする」を追加し、`run-exec-plan` Step 0b の表も4行に分けた。
  4. 本プランの Goal & Scope が「3地点」と書いていたが、実装した適用先は4つ（うち doc-review は
     助言）。「3ゲート＋doc-review（助言）」に修正。

- **未解決の矛盾（#27 由来・人の判断が必要）**: `create-exec-plan` は documentation-only プランの
  `[E2E]` AC を「Decision Log に記録した再現可能なウォークスルー」で検証してよいとしているが、
  `run-tests` / `pre-pr` / `complete-exec-plan` / `run-exec-plan` Step 3 は「`[E2E]` AC があるのに
  テストが無い＝ ❌ 保留/ブロック」としており、ウォークスルーの逃げ道を認めていない。
  本プランと #27 のプランはどちらも実際にこの状態にあり、`/pre-pr` が ⑤ で ❌ になった。
  修正方向は2つあり（①4ゲート側に documentation-only 限定のウォークスルー免除を入れる／
  ②`create-exec-plan` の免除を削り、doc-only プランには `[E2E]` AC を置かない運用にする）、
  どちらもゲートの意味を変える仕様判断のため人間ゲート。#27 の AC-004 が stale になるため、
  着手する場合は CLAUDE.md の規約どおり reconcile プランで同 AC-ID を再オープンする必要がある。

- **E2E: n/a (documentation-only)**。`2026-08-reconcile.md` の AC-003 で `create-exec-plan` から
  「documentation-only プランの `[E2E]` AC をウォークスルーで検証してよい」という免除を削除したため、
  本プランも新規約に従い `[E2E]` AC を持たない形へ是正した。
  - AC-007 の `[E2E]` マーカーを外し、通常の機能 AC（観測可能な結果＝「照合結果が Decision Log に
    記録され全項目 PASS」）として書き直した。実施内容・検証結果は変えていない。
  - プラン冒頭の「`[E2E]` の AC が緑でなければ完了ではない」注記を documentation-only の注記に差し替え。
  - これにより `/pre-pr` ⑤ の E2E カバレッジは「プランに `[E2E]` AC が無い」＝ ⚠️ 報告のみ（ブロックしない）
    に変わり、前回 ❌ で保留していた状態が規約どおりに解消される。
- **AC-007 の書き直しは readiness 観点でも改善**。旧文面「…ウォークスルーし、…を確認し、記録する」は
  R1（活動の記述）に触れる形だった。新文面は「記録され、全項目が PASS である」という単一の終状態。
  AC-006 と同じ種類の修正で、dogfooding が2件目を拾った形になる。

- **PR #30 レビュー対応（Copilot、本プラン分 2 件）**。いずれも妥当と判断し反映した。

  1. **`create-exec-plan` / `start-feature` の NOT READY 措置が失敗観点を `R2` に決め打ちしていた**。
     NOT READY は R1・R2・R5（および理由を示せない R3・R4）のいずれでも成立するのに、措置欄が
     「failing check (`R2`) を挙げる」と書いており、R1 や R5 で落ちた AC に誤った案内をしうる。
     単一ソース（`ac-readiness.md`）の判定規則と矛盾する記述でもあった。両ファイルとも
     「**すべての**失敗観点をそれぞれの ID で挙げる」に修正。
  2. あわせて `ac-readiness.md` の報告書式の指示文も同じ決め打ちだったため、
     「1観点1行で全部挙げる。代表1つに畳まない（R1 と R5 で落ちた AC は両方直す必要がある）」に修正。
     指摘は2スキルのみだったが、同じ誤りが単一ソース側にもあったため揃えた。
