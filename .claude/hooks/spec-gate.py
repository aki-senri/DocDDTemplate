#!/usr/bin/env python3
"""DocDD Spec Gate - UserPromptSubmit hook

Detects implementation intent in the user prompt and verifies that
an exec-plan with AC (acceptance criteria) exists before allowing
Claude to proceed with implementation.
"""
import sys
import json
import os
import glob
import re


def output_context(message: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": message
        }
    }))


IMPL_PATTERNS = [
    r'実装',
    r'コード(を|で|し)',
    r'機能.{0,10}(追加|作成|実装)',
    r'(追加|作成|修正|変更|作って|書いて).{0,20}(機能|関数|クラス|モジュール|コンポーネント|メソッド|API|エンドポイント)',
    r'テスト.{0,10}(書|作)',
    r'バグ.{0,10}(修正|直)',
    r'(?i)implement',
    r'(?i)add.{0,10}feature',
    r'(?i)write.{0,10}(code|test|function|class)',
    r'(?i)create.{0,10}(function|class|module|component|api|endpoint)',
    r'(?i)fix.{0,10}bug',
    r'(?i)develop\s+(a|the)',
    r'(?i)build.{0,10}(feature|function|api)',
    r'(?i)code\s+the',
]

DOC_ONLY_PATTERNS = [
    r'^(説明して|解説して|教えて|調べて|確認して)',
    r'(説明して|解説して|教えてください|とは何)',
    r'(?i)^(what|how|why|when|where|explain|describe|review|check|show)\s',
    r'ドキュメント.{0,10}(読|確認|説明)',
]


def has_implementation_intent(prompt: str) -> bool:
    for pattern in IMPL_PATTERNS:
        if re.search(pattern, prompt):
            return True
    return False


def is_doc_only(prompt: str) -> bool:
    for pattern in DOC_ONLY_PATTERNS:
        if re.search(pattern, prompt):
            return True
    return False


def get_active_plans(cwd: str) -> list[str]:
    active_dir = os.path.join(cwd, "exec-plans", "active")
    if not os.path.isdir(active_dir):
        return []
    return sorted(glob.glob(os.path.join(active_dir, "*.md")))


def get_acs(plan_files: list[str]) -> list[str]:
    acs = []
    for path in plan_files:
        try:
            with open(path, encoding="utf-8") as f:
                content = f.read()
            for num, desc in re.findall(r"AC-(\d{3}):\s*(.+)", content):
                acs.append(f"  AC-{num}: {desc.strip()}")
        except Exception:
            pass
    return acs


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    prompt = data.get("prompt", "")
    cwd = (
        os.environ.get("CLAUDE_PROJECT_DIR")
        or data.get("cwd")
        or os.getcwd()
    )

    if not has_implementation_intent(prompt):
        sys.exit(0)

    if is_doc_only(prompt):
        sys.exit(0)

    # User explicitly confirmed exception — let it through
    if os.path.exists(os.path.join(cwd, "exec-plans", ".spec-override")):
        sys.exit(0)

    plan_files = get_active_plans(cwd)

    # Case 1: No active exec-plan
    if not plan_files:
        output_context(
            "[DocDD 仕様ゲート] 実装の意図を検知しましたが、exec-plans/active/ に実行計画がありません。\n\n"
            "■ 必要なアクション\n"
            "  /create-exec-plan を実行して受け入れ基準（AC-001〜）を定義してください。\n"
            "  AC を定義してから改めて実装を指示してください。\n\n"
            "■ 例外として仕様なしで進める場合\n"
            "  ユーザーに「仕様なしで進めることを確認します」と明示的に確認を求めてください。"
        )
        sys.exit(0)

    acs = get_acs(plan_files)
    plan_names = [os.path.basename(f) for f in plan_files]

    # Case 2: Plans exist but no ACs defined
    if not acs:
        output_context(
            "[DocDD 仕様ゲート] 実装の意図を検知しましたが、exec-plan に AC（受け入れ基準）が定義されていません。\n\n"
            f"■ 現在の exec-plan: {', '.join(plan_names)}\n\n"
            "■ 必要なアクション\n"
            "  exec-plan に AC-001〜 形式で受け入れ基準を追加してください。\n"
            "  例: - [ ] AC-001: ログインに成功したとき、ダッシュボードに遷移する\n\n"
            "■ 例外として仕様なしで進める場合\n"
            "  ユーザーに「仕様なしで進めることを確認します」と明示的に確認を求めてください。"
        )
        sys.exit(0)

    # Case 3: ACs exist but no AC number referenced in the prompt
    if not re.search(r"AC-\d{3}", prompt):
        ac_lines = "\n".join(acs[:5])
        if len(acs) > 5:
            ac_lines += f"\n  ...他 {len(acs) - 5} 件（exec-plan を参照）"
        output_context(
            "[DocDD 仕様ゲート] 実装の意図を検知しました。どの受け入れ基準（AC）を実装しますか？\n\n"
            f"■ 実行計画: {', '.join(plan_names)}\n"
            f"■ 受け入れ基準一覧:\n{ac_lines}\n\n"
            "実装指示には AC 番号を含めてください（例: \"AC-001 を実装してください\"）。"
        )
        sys.exit(0)

    # All checks passed
    sys.exit(0)


if __name__ == "__main__":
    main()
