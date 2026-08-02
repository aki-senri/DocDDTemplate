---
status: active
created: 2026-08-02
completed:
---

# convention-gaps

## Goal & Scope

前サイクルの矛盾チェックで露見した規約の穴を2件塞ぐ。
① reconcile プランの命名（同月内に2本目が必要なときの規約が無い）を、内容が分かるサフィックス方式で
正式化する。② 「規約が状態機械（ループ・再開・ゲート）に触れる変更は、記述の突き合わせだけでなく
**その状態機械を1周辿って**照合する」という検証方法を規約化し、単一ソース化する。
どちらも人（ユーザー）が決定済みの方針を実装するもので、新しい方針判断は含まない。

## Acceptance Criteria

- [x] AC-001: `CLAUDE.md` の reconcile 命名規約に、同月内に複数本必要な場合の命名
      （`YYYY-MM-reconcile-<topic>.md` — 内容が分かる語を使い、連番は最後の手段）と、
      昇格起点の `YYYY-MM-reconcile-<label>.md` との**判別基準**（`<label>` は昇格ラベル＝
      `spec/<label>` ブランチと `spec-target-<label>` タグに一致する語）が書かれた状態にする
- [x] AC-002: 前サイクルで `-2` 連番のまま作られた reconcile プランが新命名規約に沿った内容の分かる
      ファイル名にリネームされ、リポジトリ内にそのファイルを旧名で指す記述が1件も残っていない状態にする
- [x] AC-003: プロセス照合の単一ソース `.claude/skills/create-exec-plan/process-walkthrough.md` が
      存在し、①適用条件（どの変更がこの照合を要するか）②手順（状態機械を1周辿る）③辿る対象の
      既定リスト（正常系・再開・免除・ゲート境界）④記録書式 ⑤呼び出し地点ごとの措置
      ⑥適用外 の6項目すべてを定義した状態にする
- [x] AC-004: `create-exec-plan` が、状態機械に触れるプランに対して「1周辿る照合」の AC を
      置くよう求める状態にする（インタビューの該当質問・Steps・Completion criteria に組み込まれ、
      記述の突き合わせだけの検証 AC を不十分として扱う）
- [x] AC-005: `doc-review` と `docode-review` が、変更されたプロセス記述に対して
      「1周辿ったときに破綻しないか」を観点として持ち、判定に含めた状態にする
- [x] AC-006: `pre-pr` が、プランに状態機械への変更が含まれるとき照合記録の有無を確認し、
      欠落を報告する状態にする（⚠️ 報告であり PR をブロックしない）
- [x] AC-007: `CLAUDE.md` / `SKILL_FLOW.md` に、この照合が既存の検証（AC readiness / red-first /
      E2E カバレッジ）と**どう違うか**が書かれ、4文書（`README.md` / `README.ja.md` /
      `ONBOARDING.md` / `ONBOARDING.ja.md`）のスキル表・フロー記述に規約導入前の記述が
      残っていない状態にする
- [x] AC-008: 本プラン自身の変更（AC-001〜007）を `process-walkthrough.md` の手順で
      **6周**（happy / 2周目 / 再開 / 免除 / ゲート境界 / 成功時）辿った結果が、周回名・所見・修正を
      伴って Decision Log に記録され、修正後に全周 PASS である

> 本プランは documentation-only（変更対象は `.claude/skills/**` と `*.md`、および exec-plan の
> リネームのみ）のため `[E2E]` AC を持たない。Decision Log の `E2E: n/a (documentation-only)` を参照。

## Task Breakdown

- [x] AC-001 — `CLAUDE.md`「仕様バージョンの管理」節の命名規約
- [x] AC-002 — `git mv` とリポジトリ内参照の追従
- [x] AC-003 — `.claude/skills/create-exec-plan/process-walkthrough.md` を新規作成
- [x] AC-004 — `.claude/skills/create-exec-plan/SKILL.md`
- [x] AC-005 — `.claude/skills/doc-review/SKILL.md` と `.claude/skills/docode-review/SKILL.md`
- [x] AC-006 — `.claude/skills/pre-pr/SKILL.md`
- [x] AC-007 — `CLAUDE.md` / `SKILL_FLOW.md` / `README*.md` / `ONBOARDING*.md`
- [x] AC-008 — 自己適用の照合を実施し Decision Log に記録
- [x] `/check-doc-invariants` を実行
- [x] `/pre-pr` を実行（PR 作成自体は人間ゲート）

## Progress Log

### 2026-08-02
- Plan created
- AC-001〜007 完了
- AC-008 完了（6周の照合、検出4件を修正して全周 PASS）
- `/check-doc-invariants` 実行。DOC-INV-004 が既知の違反のみ、006 は 3 プランとも ℹ️、001 は Markdown リンク無しで PASS
- `/pre-pr` 実行。①②④ は前提ファイル不在で N/A、③ は既知違反のみ、⑤ は `test_strategy.md` 不在で実行不可（red-first 証跡は documentation-only で ➖）、⑤b は本プランの AC-008 に6周の記録あり ✅、⑥ 更新済み。PR 作成は人間ゲートのため保留

## Decision Log

### 2026-08-02

- **E2E: n/a (documentation-only)**。変更対象はスキル定義・ルート文書・exec-plan のリネームのみで、
  機能を実装するファイルを含まない。
- **起票の経緯**。`2026-08-red-first-tests.md` の矛盾チェックで、(1) 同月2本目の in-version reconcile
  の命名が規約に無いこと (2) 「記述の突き合わせ」型の照合では状態機械の破綻を検出できないこと、の
  2点を「人の判断が必要」として提示し、ユーザーが「1: 正式とする（内容が明確なファイル名にする）」
  「2: 規約化する」と決定した。本プランはその決定の実装であり、方針判断は含まない。
- **AC readiness（Q3c）の判定**: AC-001〜008 すべて READY。R4 は documentation-only のため n/a。
  - R1: 各 AC は単一の終状態（「〜が書かれた状態」「〜が残っていない状態」「〜が PASS である」）。
  - R2: given（現行の記述）/ when（該当ファイルを読む・スキルを実行する）/ then（何が書かれているか）
    が特定できる。
  - R3: 「6項目すべて」「1件も残っていない」「全項目 PASS」など数えられる語にした。
  - R5: 変更するファイルは Task Breakdown 側に置いた（AC-003 は成果物の同一性がパスそのものなので本文に残す）。
- **単一ソースの置き場所を `create-exec-plan/` にした理由**。この照合を要求する主体はプラン起票
  （「検証 AC をどう書くか」の決定）であり、`ac-readiness.md`（プランの AC が測定可能か）と
  同じ層の関心事。`red-first.md` を概念の持ち主である `run-tests/` に置いたのと同じ基準で、
  「プランの十分性」を所有する `create-exec-plan/` に置く。
- **本プラン自身の red-first: n/a (documentation-only)**。テスト基盤を持たない documentation-only
  プランであり、`red-first.md` の適用外1行目に該当する。

- **AC-001 done.** `CLAUDE.md`「現バージョン修正による stale の扱い」の命名規約を表に置き換えた。
  in-version の当月2本目以降は `YYYY-MM-reconcile-<topic>.md`（内容が分かる語。連番は最後の手段）。
  昇格起点 `YYYY-MM-reconcile-<label>.md` との**判別基準**として「`<label>` は `spec/<label>` ブランチと
  `spec-target-<label>` タグに一致する語でなければならない」を明記し、迷う場合はファイル名ではなく
  プランの Goal & Scope とルーティング記録が正であることも書いた。
- **AC-002 done.** `2026-08-reconcile-2.md` → `2026-08-reconcile-promote-spec-e2e.md` にリネームし、
  見出し・他プランからの参照3件を追従。旧名は「その名前にした理由」を述べる履歴1行にのみ残る
  （これは過去の事実の記述であり、ファイルを指す参照ではない）。
- **AC-003 done.** `.claude/skills/create-exec-plan/process-walkthrough.md` を新設。適用条件の表、
  6周（happy / 2周目 / 再開 / 免除 / ゲート境界 / 成功時）、所見の型6種（デッドロック・矛盾する判定・
  成功を異常として扱うゲート・到達不能な規則・自分の出力が自分の入口条件に違反・孤立した免除）、
  記録書式、呼び出し地点の措置、適用外、他の検証との違いを収録。
  **なぜ「記述の一致」では足りないか**を、実際に起きた2例（再開時のベースライン、E2E が緑になった
  瞬間の HALT）で示した。抽象論だけだと、次の実施者が結局また記述照合をやるため。
- **AC-004 done.** `create-exec-plan` に Q3e と「Process changes」節を追加。**記述照合だけの検証 AC を
  明示的に「不十分」と書いた**（これが今回の失敗の直接原因であり、書かなければ同じ AC がまた書かれる）。
- **AC-005 done.** `doc-review` に §2c、`docode-review` に観点 1d を追加。どちらも
  「2周目・再開・免除」の3周を最低限とした（レビューは差分が対象で、実施者ほど文脈を持たないため
  6周すべてを求めない）。`doc-review` は独立エージェントに単一ソースを渡す必要があるため、
  Step 2 の context 収集と Step 3 のプロンプトにも追加した。
- **AC-006 done.** `pre-pr` に ⑤b を追加。⚠️ 報告のみ・ブロックしない。
  **「後からウォークスルーを再構成しない」**を明記した（事後に「一貫して見える」と判断するのは、
  この検査が置き換えようとしている判断そのもの）。
- **AC-007 done.** `CLAUDE.md` に「プロセス照合」節（4地点の措置表＋他の検証との違い）、
  `SKILL_FLOW.md` に共通参照ファイル注記・PLAN / DR / DCR / PREPR ノード、
  `README`（en/ja）のスキル表、`ONBOARDING`（en/ja）の全体の流れを追従。

- **AC-008 done（自己適用）.** 本プランの変更（AC-001〜007）を `process-walkthrough.md` の手順で
  6周辿った。**新規約自身に4件の破綻**が見つかり、いずれも修正した。

  | 周 | 検出 | 修正 |
  |----|------|------|
  | 1. happy | **Q3e が Q3c（readiness）の後ろにあり、Q3e で追加した AC だけが readiness を通らない**。「起票時に全 AC を検査する」という #24 のゲートに穴を開けていた | Q3e を Q3c の**前**に置き、Q3c の対象を「プランが最終的に持つ全 AC」に変更。「Q3c の後に AC を追加・変更したら Q3c を再実行」も明記。Steps の番号重複（3 が2つ）も修正 |
  | 2. 2周目 | 破綻なし（2本目のプランでも Q3e は独立に発火し、1本目の記録は completed 側にあるため干渉しない） | — |
  | 3. 再開 | 破綻なし（walkthrough AC の状態はチェックボックスと Decision Log 記録だけで判定でき、会話履歴に依存しない） | — |
  | 4. 免除 | 破綻なし（プロセスを変えないプランでは Q3e が発火せず、`pre-pr` ⑤b は ➖ n/a、レビュー2種は skip と明記済み） | — |
  | 5. ゲート境界 | **walkthrough AC が red-first に引っかかる**。documentation-only でないプラン（コードも含むプラン）が規約変更を含む場合、`run-exec-plan` Step 2a が「この AC のテストを先に赤で置け」と要求するが、成果物が記録そのものであるためテストを書きようがなく、ループが進めない | `red-first.md` の適用外に「記録が成果物の AC」を追加（振る舞いを変える AC が**ついでに**記録も書く場合には使えない、と限定）。`process-walkthrough.md` 側にも相互参照を書いた |
  | 5. ゲート境界（続） | `complete-exec-plan` が ⑤b 相当を持たない＝ red-first 証跡との非対称が**無言**だった | 非対称を単一ソースの call-site 表に明記（理由: red-first 証跡は「テストがどう生まれたか」の主張でアーカイブ前の最終監査に値するが、walkthrough の所見はこの差分で直っているかいないかで、マージ後に再報告しても何も変わらない） |
  | 6. 成功時 | **周回で見つけた矛盾の修正がプランの AC の外に出る場合の扱いが未定義**。自走 driver が規約を独断で書き換えうる | 「プランがスコープしていない規則の変更が必要なら停止条件 (e) で HALT。未解決の所見も結果として記録する」を単一ソースに追加 |

  4件のうち3件（1・5・6）は**この規約を導入したことで新たに生まれた矛盾**であり、規約を書いた直後に
  同じ規約を適用しなければ検出できなかった。AC-008 を「自己適用」にした狙いがそのまま効いた形。
- **AC-008 の本文を「1周」→「6周（周回名を列挙）」に修正**。起票時は「1周辿った結果が記録され全項目
  PASS」と書いていたが、`process-walkthrough.md` は最低6周と記録書式（周回名を挙げる）を定めており、
  AC 本文のままだと1周でも満たせてしまう。単一ソースより緩い検証 AC は、この規約が防ごうとしている
  ものそのもの。実施内容は変えず、判定できる言葉に書き直した（#24 の AC-006 と同種の修正）。
