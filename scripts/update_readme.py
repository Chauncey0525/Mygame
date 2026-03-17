import datetime as _dt
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README_PATH = ROOT / "README.md"

START = "<!-- AUTO-UPDATE-START -->"
END = "<!-- AUTO-UPDATE-END -->"


def _run(cmd):
    # Windows 上 git 输出可能包含非 GBK 字符，统一用 UTF-8 容错解码
    return (
        subprocess.check_output(
            cmd,
            cwd=str(ROOT),
            stderr=subprocess.STDOUT,
        )
        .decode("utf-8", errors="replace")
        .strip()
    )


def _git_log(n=12):
    # format: shortsha | date | subject
    out = _run(["git", "log", f"-n{n}", "--date=short", "--pretty=format:%h|%ad|%s"])
    if not out:
        return []
    return out.splitlines()


def _render_block(lines):
    now = _dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    if not lines:
        body = "- （暂无提交记录）"
    else:
        items = []
        for line in lines:
            parts = [p.strip() for p in line.split("|", 2)]
            if len(parts) != 3:
                continue
            sha, date, subject = parts
            # README 里用 SHA 做锚点信息（不强依赖远端链接，避免 repo/分支变化）
            items.append(f"- `{sha}` ({date}) {subject}")
        body = "\n".join(items) if items else "- （暂无可解析的提交记录）"

    return "\n".join(
        [
            START,
            f"_最后生成时间：{now}_",
            "",
            body,
            END,
        ]
    )


def _update_readme(content, new_block):
    pattern = re.compile(re.escape(START) + r"[\s\S]*?" + re.escape(END))
    if not pattern.search(content):
        raise SystemExit(f"README 中未找到标记区块：{START} ... {END}")
    return pattern.sub(new_block, content, count=1)


def main() -> int:
    if not README_PATH.exists():
        print(f"README 不存在：{README_PATH}", file=sys.stderr)
        return 2

    content = README_PATH.read_text(encoding="utf-8")
    block = _render_block(_git_log())
    updated = _update_readme(content, block)

    if updated != content:
        README_PATH.write_text(updated, encoding="utf-8")
        print("README 已更新。")
    else:
        print("README 无需更新。")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

