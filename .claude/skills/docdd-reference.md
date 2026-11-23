# DocDD 参照 — 必要なときに開く

> `CLAUDE.md` は毎セッション読み込まれるため、どのセッションでも要る規約（仕様ファースト・外側ゲート・
> 停止条件・再開状態・完了の境界・変更のルーティングなど）だけを持つ。このファイルはその外側にあり、
> 特定の作業をするときに開く。中身は2種類ある。
>
> - **索引**（§1・§2）: 各規約の単一ソースがどこにあるか、検証どうしが何を問うか。規約の中身・地点表
>   （どの skill のどの Step で何をするか）は単一ソースの側にだけあり、ここでは繰り返さない。
> - **ここが単一ソースの手順**（§3〜§5）: skill に単一ソースを持たない手順。`CLAUDE.md` から名指される。

## 1. いつ何を開くか

各単一ソースは自分の地点表（`Where this is applied`）を持つ。どの地点で何が起きるかはそこを読む。

| していること | 開くもの |
|-------------|---------|
| AC がテストで合否判定できる形かを判定する（AC readiness） | [`create-exec-plan/ac-readiness.md`](create-exec-plan/ac-readiness.md) |
| テストを AC 行と起点から起草し、赤を観測して凍結する（red-first） | [`run-tests/red-first.md`](run-tests/red-first.md) |
| `## Sources`（AC の起点）を書く・読む・spec へ再アンカーする。文書の3区分（起点／背景／読まない） | [`create-exec-plan/ac-sources.md`](create-exec-plan/ac-sources.md) |
| E2E シナリオの凍結・補完検出・保留（`deferred`）・次版戻し | [`create-spec/e2e-interaction.md`](create-spec/e2e-interaction.md) |
| DocDD 自身の規約を変えるプランの検証（周回） | [`create-exec-plan/process-walkthrough.md`](create-exec-plan/process-walkthrough.md) |
| プランを起草して人に見せる（展開ビュー） | [`create-exec-plan/expanded-view.md`](create-exec-plan/expanded-view.md) |
| 要件から実行計画までを1つの PR で承認する（一括承認） | [`create-spec/bundled-approval.md`](create-spec/bundled-approval.md) |
| HALT や所見を人に出す・人の決定を文書の差分に起草する（決定依頼） | [`run-exec-plan/decision-requests.md`](run-exec-plan/decision-requests.md) |
| 自走の準備・全 AC 完了後の流れ（起動の集約） | [`run-exec-plan/SKILL.md`](run-exec-plan/SKILL.md) Step 0・Step 4 |
| コード前の (a) で AC を保留する・独立レビューの ❌ を自己修正する（停止の束ね方） | [`run-exec-plan/SKILL.md`](run-exec-plan/SKILL.md)「Holding an AC」「Self-repair after a ❌ review」、分類は [`docode-review/SKILL.md`](docode-review/SKILL.md)「Findings」 |
| 停止条件の検出地点の一覧・再開状態の記録書式 | [`run-exec-plan/SKILL.md`](run-exec-plan/SKILL.md)「Stop conditions」「Resume-state convention」 |
| 完了の境界・人の確認記録・complete コミット・再オープン・プランの大きさ | [`complete-exec-plan/completion-boundary.md`](complete-exec-plan/completion-boundary.md) |
| 全 AC の確認に使う確認シート | [`complete-exec-plan/confirmation-sheet.md`](complete-exec-plan/confirmation-sheet.md) |
| ADR を書く／調査ノートを書く・再確認する | [`init-project/adr-format.md`](init-project/adr-format.md)／[`init-project/research-note-format.md`](init-project/research-note-format.md) |
| 検証スキルを Skill ツールで呼ぶか、手順をインラインで辿るか | §3 |
| `main` への不備修正が実装済みの AC を変える（stale・reconcile プラン） | §4 |
| 次バージョンの仕様（`spec/<label>`）を現ターゲットへ取り込む | §5 と `/promote-spec` |

## 2. 検証どうしの違い

検証はどれも別の問いに答える。1つが通っても他が通ったことにはならない。

| 検証 | 問い | 単一ソース |
|------|------|-----------|
| AC readiness | その AC は**測れるか**（テストで合否判定できる形か） | `create-exec-plan/ac-readiness.md` |
| red-first | その測定は**実装から独立か**（一度も赤にならなかったテストは何も測っていない） | `run-tests/red-first.md` |
| AC の起点 | 実装者は**目標を丸ごと受け取ったか**。出来上がりを目標に照らし直したか（起点が AC 行より多くを述べていないか） | `create-exec-plan/ac-sources.md` |
| `[E2E]` カバレッジ | 断片が**利用者の役に立つ形に積み上がるか** | `run-tests/SKILL.md` |
| 補完検出 | E2E が**要件より多くを述べていないか** — 走行が目指す目標は人が決めたものか | `create-spec/e2e-interaction.md` |
| プロセス照合 | その文書が書いているプロセスは、2周目・再開・免除の経路で**実際に走るか**。変更を参照している既存の地点は、増えた判定材料を手元に持っているか | `create-exec-plan/process-walkthrough.md` |
| 完了の境界 | どこまでが AI の作業で、**どこで人が確認したか** | `complete-exec-plan/completion-boundary.md` |

前の五つはプロダクトについての検証、プロセス照合はプロセス文書自身についての検証、完了の境界は
誰が何を確かめたかの記録である。

## 3. 検証スキルの呼び出しポリシー

`/run-exec-plan` は検証スキルを AC ごとに自動で回す。ただし呼び出し方式はスキルの副作用の有無で分ける。

| スキル | `disable-model-invocation` | 呼び出し方式 | 理由 |
|--------|:--:|--------------|------|
| `run-tests` | **false** | Skill ツールで起動（単一ソース） | テスト実行は read-only・非破壊。driver が AC ごとに確実に呼ぶ必要があり、モデル起動可にして Skill ツールで呼ぶ方がインライン複製のドリフトを避けられる |
| `check-invariants` / `check-doc-freshness` | **true** | 手順をインライン実行（Skill ツールは使わない） | コード/ドキュメントを書き換える副作用があるため、文脈任せの自動起動（ambient invocation）は統治ゲートを崩す。driver や pre-pr が手順を辿る形でのみ実行する |

`true` のスキルは「モデルが文脈次第で勝手に起動するのを防ぎつつ、driver や pre-pr が手順を辿る形での実行は可能」という仕組みをそのまま使う。
人間判断スキル（`create-requirements` の対話、`promote-spec`、PR 作成）はゲートを維持する。

上の表は AC **ごと**に回る検証スキルの呼び出し方式を扱う。`docode-review`（`disable-model-invocation: false`）は
これとは別枠で、ループ全体が完了した**一度きり**の地点（Step 4a）で呼ばれる。副作用が無い
（独立エージェントは診断のみでコードを書き換えない）点は `run-tests` と同じ理由で Skill ツール起動を
選んでおり、かつ ✅/⚠️ か ❌ かで PR 前チェック（Step 4b）へ進めるかが決まる（詳細は `CLAUDE.md`「自律実装ループ」と
`run-exec-plan/SKILL.md` Step 4a）。`pre-pr`（`disable-model-invocation: true`）は Step 4b で
手順をインライン実行する。書き換えを伴う ①② はレビュー前の掃き出しで済ませ、Step 4b では報告だけにする。

## 4. 現バージョン修正による stale の扱い

`main` への不備修正（`CLAUDE.md`「変更のルーティング」）が **既に実装済み** の AC の仕様を変える場合、その実装は新しい仕様に対して stale になる。
「なぜ stale にしたか」（履歴）と「reconcile すべき未処理作業」を別チャネルで管理する。

| 対象 AC の状態 | 対応 |
|----------------|------|
| **実装中**（`exec-plans/active/` にある。マージ前のブランチで complete 済みのプランも含む） | そのプランの Decision Log に変更理由を記録する。作業は既に開いているため追加のプランは不要。マージ前のブランチで complete 済みなら、そのブランチで再オープンする（人の確認は変わる前の目標に対するものだったため。`CLAUDE.md`「完了の境界」） |
| **完了済み**（`main` の `exec-plans/completed/` にある） | ① reconcile プランに同じ AC-ID を再オープンする（`active/` 内の最新の `*-reconcile.md` に追記、なければ — または最新のものが実装に着手済みなら（下記）— 当月の `exec-plans/active/YYYY-MM-reconcile.md` を作成）。② その **reconcile プラン側** の Decision Log に「AC-XXX は `<commit>` の不備修正で stale」と記録する（完了済みプランは archive 済みで参照されないため、そこには書かない） |

- 未処理の reconcile は必ず `exec-plans/active/` に置く（spec-gate・pre-pr・gc が走査する唯一の場所）。
- **起点のファイル・節を動かす修正**（ファイルの移動・改名・節の改題）は、AC を変えなくても、それを名指す active プランの `## Sources` を壊す。該当プランを洗い出し、**動かす修正と同じコミット（少なくとも同じ push）で、人が行を更新する**。ファイルの移動・改名を放置すると、そのプランの PR は DOC-INV-012 の ❌ で止まり（プランが `active/` にある間。complete するときは `/complete-exec-plan` が移動の前にその行を検査し、complete 後に `main` の取り込みで動いたものは `/pre-pr` ⑦ が ⚠️ で報告する）、他の PR の `/pre-pr` ③ には「他のプラン」の ❌ として（ブロックせずに）出続け、`/gc` も ❌ として報告し続ける。移動を PR で行えば、その PR 自身が移動したファイルを名指す行の ❌ で止まるが、`main` への直接修正と昇格は `/pre-pr` を通らないため、その時点では何も止めない。節の改題は DOC-INV-012 では ⚠️ にとどまるが、読み手が節を特定できなければ実行時に HALT (a) になる。`/promote-spec` の昇格では Step 4 で洗い出し、Step 5 で報告し、Step 6 のマージ直後・push 前に人が更新する。
- 専用の「Spec Drift Log」節は作らない（走査されず archive されて陳腐化するため）。
- reconcile プランは無限に追記せず、サイクルごとに閉じて新規を起こす（全 AC が `- [x]` にならず complete できなくなるのを防ぐ）。**実装に着手された reconcile プラン（ブランチで作業中、または complete 済みでマージ待ち）には追記しない** — 確認の単位は plan 全体なので、追記のたびにそのブランチで再オープンと確認のやり直しが起きる。着手済みかが `main` から分からないときはプランの担当者に確かめ、分からなければ新しい reconcile プランを起こす。両者は `active/` に併存し、扱い（同 AC-ID 再オープン＋Decision Log 記録）は同一。命名は次のとおり。

  | 起点 | 命名 | 例 |
  |------|------|----|
  | in-version（不備修正）・当月1本目 | `YYYY-MM-reconcile.md` | `2026-08-reconcile.md` |
  | in-version・**当月2本目以降** | `YYYY-MM-reconcile-<topic>.md` — `<topic>` は**内容が分かる語**（何を reconcile するのか）。連番（`-2`）は適切な語が無いときの最後の手段 | `2026-08-reconcile-promote-spec-e2e.md` |
  | 昇格起点（`/promote-spec`） | `YYYY-MM-reconcile-<label>.md` | `2026-08-reconcile-sprint-12.md` |

  当月2本目以降が要るのは、同じ月に前サイクルの reconcile が完了・archive 済みの場合と、当月の reconcile が実装に着手済みで追記できない場合。前者は完了時に `completed/` で同名衝突するため、同名で起こしてはならない。

  **サフィックスが `<topic>` か `<label>` かの判別**: `<label>` は昇格ラベルであり、`spec/<label>` ブランチと `spec-target-<label>` タグに一致する語**でなければならない**。一致するものが無ければそれは in-version の `<topic>`。ファイル名だけで迷う場合は、そのプランの Goal & Scope とルーティング記録（`main` の不備修正か昇格追従か）が正であり、ファイル名は目印にすぎない。
- 当面 reconcile しないと判断した場合は、その active プランの Decision Log に `reconcile: deferred`（または `reconcile: n/a`）と記録する（E2E シナリオについては `reconcile: deferred — E2E-NNN` のように ID を添える。`/gc` の E2E backstop はその変更以後の記録だけを認める）。これにより `/gc` backstop の再フラグを抑止する。
- 起票漏れは `/gc` の spec-drift backstop（AC-ID が鍵）と E2E backstop（`E2E-NNN` が鍵。AC 行を変えずに凍結済みシナリオが変わった場合）が週次で検出する（結果は確認候補であり確定ではない）。

## 5. 昇格（promotion）

次バージョン仕様を現ターゲットに取り込む操作は **`/promote-spec`** で行う。
昇格は開発ターゲットを変える判断のため、**マージするか・いつするかは人が決める**（スキルは差分・影響解析と後処理を支援するのみ）。
各ターゲットのスナップショットは、それぞれ固有の `spec-target-<label>` タグで保存される（ラベルはターゲットごとに異なり、同名タグを使い回さない）。昇格後の新版には新しいラベルのタグを付け、昇格前の現行版は前回の昇格で付いたタグで既に保存済み（初回昇格のみ baseline を seed）。これにより旧バージョンはいつでも復元・差分比較できる。タグは共有リモートへ push して初めて全員が復元できる点に注意。

**`spec-target-*` タグは昇格（＝開発ターゲットの変更）ごとに作る。個人や機能ごとには作らない。**
`<label>` は共有のバージョン/昇格ラベルであり、個人名・機能名は使わない。開発者の機能実装は通常の PR で現ターゲット（`main`）にマージするだけで、タグは付かない（タグが付くのは `/promote-spec` の中だけ）。したがってタグ数は「昇格回数 ＝ 開発ターゲットを切り替えた回数」に等しく、開発者数や機能数には比例しない。
復元の正は昇格の `--no-ff` マージコミット（`main` 上に必ず残る）であり、`spec-target-*` タグは名前付き diff のための便宜にすぎない。古いタグは履歴を失わずに剪定できる（`git tag -d` ＋ `git push origin --delete`）。
