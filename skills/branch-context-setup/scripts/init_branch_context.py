#!/usr/bin/env python3

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_CONTEXT_DIR = ".branch-context"


def run_git(args, cwd):
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git command failed")
    return result.stdout.strip()


def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sanitize_branch_name(branch_name):
    cleaned = branch_name.strip().replace("/", "__")
    cleaned = cleaned.replace(" ", "-")
    if not cleaned:
        raise ValueError("branch name is empty")
    return cleaned


def detect_repo_root(repo):
    return Path(run_git(["rev-parse", "--show-toplevel"], cwd=repo))


def detect_branch(repo):
    branch = run_git(["branch", "--show-current"], cwd=repo)
    if not branch:
        raise RuntimeError("current HEAD is detached; pass --branch explicitly")
    return branch


def ensure_file(path, content):
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def write_json_if_missing(path, payload):
    if not path.exists():
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )


def ensure_local_exclude(repo_root, context_dir):
    exclude_path = Path(repo_root) / ".git" / "info" / "exclude"
    existing = exclude_path.read_text(encoding="utf-8") if exclude_path.exists() else ""
    entry = f"{context_dir}/"
    if entry not in {line.strip() for line in existing.splitlines()}:
        with exclude_path.open("a", encoding="utf-8") as handle:
            if existing and not existing.endswith("\n"):
                handle.write("\n")
            handle.write(f"{entry}\n")


def set_repo_config(repo_root, context_dir):
    subprocess.run(
        ["git", "config", "--local", "branch-context.dir", context_dir],
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )


def build_environment_template(branch_name, envs):
    env_lines = "\n".join(f"- {env}" for env in envs) if envs else "- 待补充"
    return f"""# 环境信息

## 分支

- {branch_name}

## 泳道 / 环境

{env_lines}

## 说明

- 记录本需求涉及的开发、测试、预发、生产或其他泳道环境
- 标明环境差异、开关、数据前提、依赖服务
"""


def build_requirement_template():
    return """# 需求信息

## 背景

- 待补充

## 目标

- 待补充

## 非目标

- 待补充

## 约束

- 待补充

## 外部链接

- 待补充

## 验收要点

- 待补充
"""


def build_development_template(branch_name, scopes):
    scope_lines = "\n".join(f"- {scope}" for scope in scopes) if scopes else "- 待补充"
    return f"""# 开发信息

## 分支

- {branch_name}

## 改动范围

{scope_lines}

## 手工备注

- 记录不适合从 Git 自动推断的实现约束、风险和阶段性结论

## 自动同步区

本文件下方的“自动生成”部分由 `branch-context` 技能刷新，请不要手工编辑。

<!-- AUTO-GENERATED-START -->
_尚未同步_
<!-- AUTO-GENERATED-END -->
"""


def main():
    parser = argparse.ArgumentParser(description="Initialize branch-scoped context storage.")
    parser.add_argument("--repo", default=".", help="Path inside the target Git repository")
    parser.add_argument("--context-dir", default=DEFAULT_CONTEXT_DIR, help="Repository-local storage root")
    parser.add_argument("--branch", help="Branch name. Defaults to the current checked-out branch")
    parser.add_argument("--env", action="append", default=[], help="Seed environment/swimlane entry")
    parser.add_argument("--scope", action="append", default=[], help="Seed initial change scope entry")
    args = parser.parse_args()

    try:
        repo_root = detect_repo_root(args.repo)
        branch_name = args.branch or detect_branch(repo_root)
        branch_key = sanitize_branch_name(branch_name)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    context_root = repo_root / args.context_dir
    branch_dir = context_root / branch_key
    branch_dir.mkdir(parents=True, exist_ok=True)
    ensure_local_exclude(repo_root, args.context_dir)
    set_repo_config(repo_root, args.context_dir)

    metadata = {
        "repo_root": str(repo_root),
        "context_dir": args.context_dir,
        "branch": branch_name,
        "branch_key": branch_key,
        "initialized_at": now_iso(),
        "updated_at": now_iso(),
    }

    write_json_if_missing(branch_dir / "metadata.json", metadata)
    ensure_file(branch_dir / "environment.md", build_environment_template(branch_name, args.env))
    ensure_file(branch_dir / "requirement.md", build_requirement_template())
    ensure_file(branch_dir / "development.md", build_development_template(branch_name, args.scope))

    print(
        json.dumps(
            {
                "repo_root": str(repo_root),
                "branch": branch_name,
                "branch_key": branch_key,
                "context_dir": str(context_root),
                "branch_dir": str(branch_dir),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
