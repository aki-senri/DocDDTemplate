---
status: active
created: 2026-08-02
completed:
---

# red-first-tests

## Goal & Scope

受け入れテストを **実装より先に、AC 本文から起草して赤で置く**（red-first）ことを DocDD の規約にし、
「実装者が実装と同時にテストを書く＝自分の答案を自分で採点する」構造を解消する。
INV-T01（実装に合わせたテスト改変の禁止）を**時間軸**で強制する形に拡張し、赤の観測をもって
テストの期待値を凍結する。GitHub issue #22 (G-A) の解消。親トラッキングは #28 で、本プランはその Ph3
（#27 → #24 の次）にあたる。

## Acceptance Criteria

- [x] AC-001: red-first の単一ソース `.claude/skills/run-tests/red-first.md` が存在し、
      ①手順（AC 本文からテストを起草 → 実行して赤を観測 → 記録して凍結 → 実装）②「妥当な赤」と
      「無効な赤」の判別基準 ③Decision Log への記録書式 ④凍結後にテストを変更してよい唯一の経路
      ⑤呼び出し地点ごとの措置表 ⑥適用外（documentation-only 等）の6項目すべてを定義した状態にする
- [x] AC-002: `run-exec-plan` の内側ループが AC ごとに「テストを先に書いて赤を観測してから実装する」
      順序になった状態にする（Step 2 が 2a テスト起草＋赤観測 / 2b 実装に分かれ、AC 本文からテストを
      書けない場合は停止条件 (a) で HALT し、Decision Log に赤の観測が `AC-NNN done` より前に記録される）
- [x] AC-003: `run-exec-plan` が `[E2E]` AC のテストを**ループ開始前**に赤で置いた状態でループを開始する
      （Step 0c）。あわせて「driver は E2E テストを書いてはならない」という現行記述が
      「実装前に AC 本文から転記する場合に限り書いてよい／転記できない場合は HALT (a)」に置き換わり、
      ループ中の「`[E2E]` AC にテストが無い＝ HALT」backstop が残っている
- [x] AC-004: `run-tests` が red-first 検証（赤が期待される実行）を扱えた状態にする。すなわち
      「テストが失敗した」だけでなく「妥当な赤（期待結果に関する失敗）／無効な赤（コンパイル・
      セットアップ・存在しない API による失敗）」を判別して報告し、無効な赤を緑と同じく
      「先へ進んでよい」とは扱わない
- [x] AC-005: `start-feature`（手動パス）の実装順ガイドが red-first を規定した状態にする
      （「安定層から実装する」順序の**前**に「その AC のテストを先に赤で置く」が来ることが本文で読める）
- [x] AC-006: `pre-pr` と `complete-exec-plan` が red-first の証跡（各 AC について、赤の観測が
      `AC-NNN done` より前に Decision Log へ記録されていること）を確認し、欠落を報告する状態にする
      （証跡欠落は ⚠️ 報告であり PR / 完了をブロックしない。ブロックするのは既存の AC カバレッジ・
      E2E カバレッジのまま）
- [x] AC-007: `init-project` が生成する不変条件表に **INV-T02**（テストの期待値は、それを満たす実装より
      先に AC から起草され、赤を観測してから凍結される）が含まれ、`SKILL.md` の共通不変条件・
      `setup-web.md` / `setup-windows.md` の各表・生成ファイル一覧の記述が INV-T02 を含む状態にする
- [x] AC-008: `docode-review` の独立エージェントが「各テストが対応する AC を表現しているか（実装の写しに
      なっていないか）」を観点として持ち、判定に含めた状態にする
- [x] AC-009: `CLAUDE.md` / `SKILL_FLOW.md` / `README.md` / `README.ja.md` / `ONBOARDING.md` /
      `ONBOARDING.ja.md` / `.claude/skills/init-project/setup-*.md` のいずれにも red-first 導入**前**の
      フロー記述が残っていない状態にする（＝内側ループや開発サイクルを「実装 → テスト」の順で書いた
      図・表・手順、および INV-T01 だけを挙げてテストの時間軸に触れない箇所が1件も無い）
- [x] AC-010: red-first を導入した全地点（`run-exec-plan` Step 0c / 2a・`run-tests`・`start-feature`・
      `pre-pr`・`complete-exec-plan`・`docode-review`）の照合結果が Decision Log に記録され、
      (a) 同じ「妥当な赤」の定義が単一ソースにのみ存在すること (b) 措置だけが地点ごとに分かれること
      (c) 既存の停止条件 (a)/(c) と矛盾しないこと を含む全項目が PASS である

> 本プランは documentation-only（変更対象は `.claude/skills/**` と `*.md` のみ）のため
> `[E2E]` AC を持たない。Decision Log の `E2E: n/a (documentation-only)` を参照。

## Task Breakdown

- [x] AC-001 — `.claude/skills/run-tests/red-first.md` を新規作成
- [x] AC-002 — `.claude/skills/run-exec-plan/SKILL.md` の Step 2 を 2a / 2b に分割
- [x] AC-003 — 同 SKILL.md に Step 0c を追加し、E2E テスト起草の禁止規定を書き換え
- [x] AC-004 — `.claude/skills/run-tests/SKILL.md` に red-first 検証モードを追加
- [x] AC-005 — `.claude/skills/start-feature/SKILL.md` の実装順ガイドを改修
- [x] AC-006 — `.claude/skills/pre-pr/SKILL.md` と `.claude/skills/complete-exec-plan/SKILL.md` に証跡確認を追加
- [x] AC-007 — `.claude/skills/init-project/{SKILL.md,setup-web.md,setup-windows.md}` に INV-T02 を追加
- [x] AC-008 — `.claude/skills/docode-review/SKILL.md` に観点を追加
- [x] AC-009 — `CLAUDE.md` / `SKILL_FLOW.md` / `README*.md` / `ONBOARDING*.md` を追従
- [x] AC-010 — 4地点の照合を実施し Decision Log に記録
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
- AC-007 完了
- AC-008 完了
- AC-009 完了
- AC-010 完了（照合16項目、修正後すべて PASS）
- `/check-doc-invariants` 実行。DOC-INV-004 が 10 件（既知・本テンプレートに `docs/01_requirements` が
  無いため構造的に充足不能）。他は PASS または N/A
- `/pre-pr` 実行。①②④ は前提ファイル不在で N/A、③ は上記の既知違反のみ、⑤ は `test_strategy.md` 不在で
  実行不可。E2E カバレッジは「プランに `[E2E]` AC が無い」＝ ⚠️ 報告のみ、red-first 証跡は
  documentation-only のため ➖ n/a。⑥ 更新済み。PR 作成は人間ゲートのため保留

## Decision Log

### 2026-08-02

- **E2E: n/a (documentation-only)**。本プランの変更対象は `.claude/skills/**` と `*.md` のみで、
  機能を実装するファイルを含まない。`create-exec-plan` の規約に従い `[E2E]` AC を置かない。
- **スコープの根拠**。issue #22 の改善方向は3つ。①`run-exec-plan` の内側ループを red-first 化
  ②テスト起草を実装とは別ステップ（または軽量な別エージェント確認）にして実装前に固定
  ③INV-T01 の精神を時間軸で強制。3つとも本プランに入れた。①＝AC-002/003、②＝AC-001（別ステップの
  定義）＋AC-008（軽量な独立確認）、③＝AC-007（INV-T02）。
  ②を「別スキル」ではなく「単一ソース＋ステップ分割」で実現するのは #24 の `ac-readiness.md` と
  同じ構成にするため。スキルを増やすと呼び出し地点ごとの複製が増え、ドリフトの原因になる。
- **単一ソースの置き場所を `run-tests/` にした理由**。red-first は「テストは spec の実行可能表現」の
  時間軸版であり、その概念を所有しているのは `run-tests`（INV-T01 のゲートを持つ側）。
  `ac-readiness.md` が起票地点（`create-exec-plan`）に置かれているのと同じ理屈で、
  概念の持ち主のディレクトリに置き、他地点は参照する。
- **AC readiness（Q3c）の判定**: AC-001〜AC-010 すべて READY。R4 は documentation-only のため n/a。
  - R1: 各 AC は「〜した状態にする」という単一の終状態で書いた。AC-002 のように複数ファイルに
    触れるものも、観測可能な結果は1つ（ループの順序が red-first になっている）。
  - R2: given（現行の記述）/ when（該当スキルを読む・実行する）/ then（本文に何が書かれているか）が
    各 AC から特定できる。
  - R3: 判定語を「6項目すべてを定義」「`AC-NNN done` より前に記録」「1件も無い」など数えられる形にした。
  - R5: どのファイルを触るかは Task Breakdown に置き、AC 本文は結果のみとした（AC-001 と AC-007 は
    ファイルパス自体が成果物の同一性なので本文に残している）。
- **AC-006 を ⚠️ 報告に留めた理由**。red-first の証跡は Decision Log という**人が書くテキスト**に
  依存するため、欠落は「規約違反」と「記録漏れ」を機械的に区別できない。ブロックにすると
  記録漏れで PR が止まり、回避のために証跡を後から書く動機を生む（＝証跡の信頼性が下がる）。
  実効的なブロックは既存の AC カバレッジ／E2E カバレッジが担う。

- **本プラン自身の red-first: n/a (documentation-only)**。本プランはテスト基盤を持たない
  documentation-only プランであり、`red-first.md` の「適用外」表の1行目に該当する。
  したがって各 AC に `red-first` の赤観測記録は置かない（これは新規約の最初の自己適用でもある）。

- **AC-001 done.** `.claude/skills/run-tests/red-first.md` を新設。手順（AC を読む→AC 本文だけから
  テストを起草→実行して赤を観測→Decision Log に記録して凍結→実装）、妥当な赤と無効な赤の判別、
  記録書式、凍結後にテストを変更してよい唯一の経路（spec alignment gate / 停止条件 (c)）、
  6呼び出し地点の措置表、適用外3件（documentation-only / preservation AC / ハーネス作業）、
  および `ac-readiness.md` との関係（R2 の経験的版）を収録。
  静的型付け言語では「存在しない API の呼び出し＝コンパイルエラー＝無効な赤」になるため、
  **振る舞いを持たない最小シグネチャだけ先に置いて赤をアサーションに到達させる**ことを明記した
  （ここを書かないと、実務で最初に詰まる箇所がそのまま「red-first は無理」の理由になる）。
- **AC-002 done.** `run-exec-plan` の Step 2 を 2a（テスト起草＋赤の観測）/ 2b（実装）に分割。
  2a には「初回から緑だった場合」の分岐（AC が既に満たされている／テストが AC を検査していない、の
  どちらかであり、テストを弱めるのは解ではない）を含めた。Design principle の表・Retry budget・
  Resume-state convention・Completion criteria・報告書式も追従。
- **AC-003 done.** Step 0c（ループ開始前に `[E2E]` テストを赤で配置）を追加。
  **#27 で入れた「driver は E2E テストを書いてはならない」を全面禁止から時点依存の規則へ変更した**。
  理由: あの禁止の根拠は「E2E テストを書く＝通しフローを決めること」だったが、通しフローは既に
  `[E2E]` AC 本文（と spec の `E2E-NNN`）で人が決めており、readiness を通った AC なら given/when/then は
  本文にある。実装が存在しない時点での起草は**転記**であって決定ではなく、実装の写しにもなり得ない。
  一方、実装後に書くテストは実装に形を合わせられるため、Step 3 の「`[E2E]` AC のテストが無い→HALT」は
  backstop として残した（＝到達したら Step 0c が飛ばされた証拠）。転記できない場合は HALT (a)。
- **ループ中ずっと赤い E2E テストの扱い**。Step 0c で赤を置く以上、ループ中の各 `run-tests` は
  必ず1件以上失敗する。これを「赤いベースライン」と誤認すると自走が止まるため、Step 3 に
  「Step 0c で記録した失敗**のみ**が残っている状態は、その AC にとっては緑と同じ扱い」を明記し、
  失敗理由が変わった場合（コンパイルできなくなった等）は測定が止まった合図として修復させる。
- **AC-004 done.** `run-tests` に Step 2b（red-first 実行の分類）を追加。呼び出し側が
  「これは red-first 実行だ」と告げた場合のみ適用し、valid red / invalid red / green on first run を
  報告する。無効な赤を「期待どおり」と報告しないことを明記（ここを曖昧にすると red-first が
  「とりあえず落ちた」で通ってしまう）。spec alignment gate は実装が存在して初めて意味を持つため
  red-first 実行には適用しないことも書いた。
- **AC-005 done.** `start-feature` の実装順ガイド冒頭に red-first を置いた。安定層順は
  「失敗するテストが置かれた後に何から作るか」の話であり、テストより前には来ない。
- **AC-006 done.** `pre-pr` ⑤ と `complete-exec-plan` Step 2 に証跡確認（`AC-NNN red-first:` が
  `AC-NNN done.` より前にあるか）を追加。⚠️ 報告のみでブロックしない。両方に
  「記録が無い場合に後から書き足さない」を明記した（後から書ける証跡は証跡ではない）。
- **AC-007 done.** INV-T02 を新設し、`init-project` の SKILL.md（全プラットフォーム共通表）・
  `setup-windows.md`・`setup-web.md` の不変条件表と生成ファイル一覧に追加。
  INV-T01 との関係（同じ穴を時間軸で塞ぐ）を共通表に1段落で書き、手順は `red-first.md` を参照させた。
- **AC-008 done.** `docode-review` の独立エージェント観点に 1c「テストは AC を表現しているか、
  実装を写しているか」を追加。観点2（Correctness）より前に置いたのは、これが 1b と同じく
  「実装したエージェント自身には原理的にできない検査」だから。実装の写しの兆候（内部呼び出しの
  アサート、コードから採った期待値、AC にあってコードに無いケースの欠落）を具体的に列挙し、
  Decision Log の red-first 記録の有無も突き合わせ対象にした（記録の欠落だけでは断定せず 🟡）。
- **AC-009 done.** `CLAUDE.md`（内側/外側ゲート表・停止条件 (a)(b)(c)・新節「red-first」・
  再開状態のファイル化規約・テスト変更の禁止節・スキル一覧2行）、`SKILL_FLOW.md`（§1 の DRIVER /
  REDFIRST / RT / SF / PREPR / COMPLETE ノードと辺、§2 の共通参照ファイル注記と呼び出し表、
  §3-6 の G-A 行と G-C 行、§4 のブロッキング注記）、`README`（en/ja: クイックスタート・スキル表2行・
  新節 red-first）、`ONBOARDING`（en/ja: 責任分担表・人視点フロー・全体の流れ・手動ループ・
  新節 red-first・invariants.md サンプルへ INV-T02）を追従。
- **AC-009 の対象ファイルに `init-project/setup-*.md` を追加した**。起票時は6ファイルを列挙していたが、
  両 setup ファイルの「Development cycle」が「3. 実装 → 4. テスト追加」と書いており、AC-009 が述べる
  終状態（red-first 導入前のフロー記述が残っていない）を満たさない。列挙漏れであってスコープ拡張では
  ないため、AC 本文のファイル列挙を拡張し、両ファイルの開発サイクルを red-first 順に修正した。
- **AC-010 done.** red-first を導入した地点の照合を実施。検査16項目のうち、当初 FAIL が4件あり、
  いずれも修正して全項目 PASS。

  | # | 検査項目 | 結果 |
  |---|---------|------|
  | 1 | 単一ソース `run-tests/red-first.md` が存在し、6地点すべてから相対リンクで到達できる | PASS |
  | 2 | 「妥当な赤／無効な赤」の**定義**が単一ソースにのみ存在する（各地点は verdict 名と参照のみ） | 修正後 PASS（下記 A） |
  | 3 | verdict の集合が全地点で一致する（valid red / invalid red / green on first run の3つ） | 修正後 PASS（下記 B） |
  | 4 | 措置だけが地点ごとに分かれる（HALT / 人に確認 / ⚠️ 報告 / 助言）＝ `ac-readiness.md` と同じ構造 | PASS |
  | 5 | 停止条件 (a) の説明が `run-exec-plan` と CLAUDE.md で一致（転記不能＝(a)） | PASS |
  | 6 | 停止条件 (b) の説明が両者で一致（妥当な赤に到達しない＝(b)） | PASS |
  | 7 | 停止条件 (c) が「凍結後の期待値変更」を含む形で両者一致（INV-T01／INV-T02） | PASS |
  | 8 | #27 で入れた「`[E2E]` AC にテストが無い＝ HALT」backstop が残っている | PASS |
  | 9 | E2E テストがループ中ずっと赤である状態の扱いが定義され、赤いベースラインと混同されない | PASS |
  | 10 | preservation AC（refactoring / reconcile）の免除が単一ソースと `run-exec-plan` の両方で一致 | PASS |
  | 11 | documentation-only の免除が `create-exec-plan`（`[E2E]` AC を置かない）と矛盾しない | PASS |
  | 12 | 事後ゲート（pre-pr / complete-exec-plan）が ⚠️ 報告に留まり、両ファイルの文言が一致 | PASS |
  | 13 | 事後ゲートに「記録が無いとき後から書き足さない」が両方に書かれている | PASS |
  | 14 | `ac-readiness.md` R2 と red-first の関係が双方向に書かれている（片方向参照でない） | 修正後 PASS（下記 C） |
  | 15 | INV-T02 が `init-project` の3ファイル（共通表・setup-web・setup-windows）と生成物一覧に入っている | PASS |
  | 16 | 内側ループを「実装 → テスト」と書いた記述がリポジトリに残っていない（`grep` で確認） | 修正後 PASS（下記 D） |

  - **A（項目2）**: `run-tests` Step 2b の表と `run-exec-plan` Step 0c / 2a が「コンパイルエラー・
    セットアップ失敗…」と**定義を再掲**していた。`ac-readiness.md` で確立した規約（定義は単一ソース、
    地点は verdict 名のみ）に反するため、定義を落として参照に置き換えた。CLAUDE.md 停止条件 (b) の
    括弧書きも同じ理由で削除。ONBOARDING / README の例示（`expected 401, actual 500` は妥当な赤、
    「コンパイルが通らない」は無効な赤）は**規範ではなく説明**であり、末尾で単一ソースへ誘導しているため
    そのまま残した（`ac-readiness.md` の R1〜R5 を README が名前だけ挙げているのと同じ扱い）。
  - **B（項目3）**: `run-tests` が `green on first run` という verdict を持つのに、単一ソースの表は
    valid / invalid の2値しか定義しておらず、地点が単一ソースに無い判定を作っていた。
    `red-first.md` に3行目を追加し、call-site 表の Step 2a 行にも「判別できなければ HALT (a)」を追記。
  - **C（項目14）**: `red-first.md` → `ac-readiness.md` の参照はあったが逆が無く、readiness だけを
    読む人に「R2 は実装直前に経験的に再検査される」ことが伝わらなかった。`ac-readiness.md` の R2 行に
    注記を1つ追加（#24 のファイルへの追記だが、規約の相互参照であり内容の変更ではない）。
  - **D（項目16）**: `init-project/setup-web.md` / `setup-windows.md` の Development cycle が
    「実装 → テスト追加」の順だった（AC-009 の対象ファイル拡張として修正済み）。

  なお AC-010 本文は起票時「4地点」と書いていたが、実際の適用先は6地点（`run-exec-plan` の
  Step 0c と 2a を1つと数えても5つ、`docode-review` を含めて6つ）。#24 でも同じ数え違いが起きており、
  「地点を数える AC は実装後に数が合わなくなる」ことがわかったため、本文を列挙形に書き直した。

- **red-first を新スキルにしなかった判断（再確認）**。AC-010 の照合中、`/draft-tests` のような
  独立スキルにすれば「テストを書くのは別の担い手」という独立性がより強く出る、という選択肢を再検討した。
  採らなかった理由は2つ。① スキルは呼ばれなければ効かない。DocDD の必須ゲートは現状ゼロ（SKILL_FLOW §4）で、
  新スキルは「飛ばせるゲート」を1つ増やすだけになる。ループの**手順**に埋め込めば、driver が回る限り必ず通る。
  ② 独立性の実体は「担い手が別か」ではなく「実装が存在しない時点で書かれたか」にある。同じエージェントでも、
  実装前に AC 本文だけを見て書いたテストは実装を写せない。担い手の分離が要るのは事後の判定であり、
  そこは `docode-review`（実装文脈を持たない独立エージェント）が担う。

- **`/check-doc-invariants` の結果（2026-08-02）**。DOC-INV-001 は本プランに Markdown リンクが無く PASS。
  002 / 003 は `docs/` 不在で N/A。**DOC-INV-004 は AC-001〜010 の 10 件が違反**（本テンプレートには
  `docs/01_requirements/` が存在せず `ac_ids:` を持つ US を作れない。#27 / #24 と同じ既知・意図的な逸脱で、
  要件の追跡は GitHub issue #22 / #28 が代替する）。005 は新規に追加した AA 図が無く PASS
  （`red-first.md` は表と Mermaid 不要の箇条書きのみ）。006 は `[E2E]` AC 無し ＋ `E2E: n/a` 記録あり＝ ℹ️。
- **`/pre-pr` の結果（2026-08-02）**。① invariants: N/A（`docs/04_implementation/invariants.md` 不在）、
  ② doc-freshness: N/A（`tracks:` を持つドキュメント不在）、③ doc-invariants: 上記の既知 10 件のみ、
  ④ review_checklist: N/A（ファイル不在）、⑤ run-tests: 実行不可（`docs/05_quality/test_strategy.md` 不在。
  本リポジトリはスキル定義のドキュメントのみで自動テスト基盤を持たない）。E2E カバレッジは
  「プランに `[E2E]` AC が無い」＝ ⚠️ 報告のみ、**red-first 証跡は ➖ n/a（documentation-only）**。
  ⑥ exec-plan: 更新済み。PR 作成は不可逆・外向き操作のため人間ゲートとして保留。
- **G-C 行の状態も更新**。`SKILL_FLOW.md` §3-6 の G-C が「🔄 pending merge of #24」のままだったが、
  #24 は PR #30 でマージ済み。✅ Resolved に更新した（本プランの AC には属さないが、同じ表の
  隣接行を書き換える作業中に気づいた事実誤り。CLAUDE.md「現バージョンの不備修正は main へ直接」に該当）。
