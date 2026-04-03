#!/usr/bin/env python3

import argparse
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_CONTEXT_DIR = ".branch-context"
AUTO_START = "<!-- AUTO-GENERATED-START -->"
AUTO_END = "<!-- AUTO-GENERATED-END -->"


def run_git(args, cwd, check=True):
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git command failed")
    return result


def git_lines(args, cwd, check=True):
    result = run_git(args, cwd, check=check)
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sanitize_branch_name(branch_name):
    cleaned = branch_name.strip().replace("/", "__")
    cleaned = cleaned.replace(" ", "-")
    if not cleaned:
        raise ValueError("branch name is empty")
    return cleaned


def detect_repo_root(repo):
    result = run_git(["rev-parse", "--show-toplevel"], cwd=repo)
    return Path(result.stdout.strip())


def detect_branch(repo):
    result = run_git(["branch", "--show-current"], cwd=repo)
    branch = result.stdout.strip()
    if not branch:
        raise RuntimeError("current HEAD is detached; an active branch is required")
    return branch


def detect_configured_context_dir(repo_root, explicit_value):
    if explicit_value:
        return explicit_value

    configured = run_git(
        ["config", "--get", "branch-context.dir"],
        cwd=repo_root,
        check=False,
    )
    value = configured.stdout.strip()
    return value or DEFAULT_CONTEXT_DIR


def detect_default_base(repo):
    symbolic = run_git(["symbolic-ref", "refs/remotes/origin/HEAD"], cwd=repo, check=False)
    ref = symbolic.stdout.strip()
    if symbolic.returncode == 0 and ref:
        return ref.replace("refs/remotes/", "", 1)

    for candidate in ("origin/main", "origin/master"):
        probe = run_git(["rev-parse", "--verify", candidate], cwd=repo, check=False)
        if probe.returncode == 0:
            return candidate

    return None


def top_level_scope(path_str):
    path = Path(path_str)
    parts = path.parts
    return parts[0] if parts else "."


def summarize_scopes(paths):
    counter = Counter(top_level_scope(path) for path in paths)
    return [{"scope": scope, "files": count} for scope, count in sorted(counter.items())]


def read_metadata(metadata_path):
    if not metadata_path.exists():
        return {}
    return json.loads(metadata_path.read_text(encoding="utf-8"))


def write_metadata(metadata_path, metadata):
    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def replace_auto_block(content, replacement):
    if AUTO_START not in content or AUTO_END not in content:
        raise RuntimeError("development.md is missing auto-generated markers")

    before, remainder = content.split(AUTO_START, 1)
    _, after = remainder.split(AUTO_END, 1)
    return f"{before}{AUTO_START}\n{replacement}\n{AUTO_END}{after}"


def format_list(items):
    if not items:
        return "- 无"
    return "\n".join(f"- {item}" for item in items)


def build_auto_section(facts):
    scope_lines = format_list(
        [f"{entry['scope']} ({entry['files']} files)" for entry in facts["scope_summary"]]
    )
    base_line = facts["default_base"] or "未检测到 origin/HEAD"
    return f"""### 自动生成

- 更新时间: {facts['updated_at']}
- 当前分支: {facts['branch']}
- 默认基线分支: {base_line}

#### 工作区改动文件

{format_list(facts['working_tree_files'])}

#### 已暂存文件

{format_list(facts['staged_files'])}

#### 未跟踪文件

{format_list(facts['untracked_files'])}

#### 相对默认基线的改动文件

{format_list(facts['since_base_files'])}

#### 改动范围汇总

{scope_lines}
"""


def collect_facts(repo_root, branch_name):
    working_tree_files = git_lines(["diff", "--name-only"], cwd=repo_root)
    staged_files = git_lines(["diff", "--cached", "--name-only"], cwd=repo_root)
    untracked_files = git_lines(["ls-files", "--others", "--exclude-standard"], cwd=repo_root)

    default_base = detect_default_base(repo_root)
    since_base_files = []
    if default_base:
        merge_base = git_lines(["merge-base", "HEAD", default_base], cwd=repo_root)
        if merge_base:
            since_base_files = git_lines(
                ["diff", "--name-only", f"{merge_base[0]}...HEAD"],
                cwd=repo_root,
            )

    all_paths = sorted(set(working_tree_files + staged_files + untracked_files + since_base_files))

    return {
        "branch": branch_name,
        "default_base": default_base,
        "working_tree_files": working_tree_files,
        "staged_files": staged_files,
        "untracked_files": untracked_files,
        "since_base_files": since_base_files,
        "scope_summary": summarize_scopes(all_paths),
        "updated_at": now_iso(),
    }


def branch_paths(repo, context_dir):
    repo_root = detect_repo_root(repo)
    branch_name = detect_branch(repo_root)
    resolved_context_dir = detect_configured_context_dir(repo_root, context_dir)
    branch_key = sanitize_branch_name(branch_name)
    branch_dir = repo_root / resolved_context_dir / branch_key
    return repo_root, branch_name, branch_key, branch_dir, resolved_context_dir


def command_show(args):
    repo_root, branch_name, branch_key, branch_dir, resolved_context_dir = branch_paths(
        args.repo, args.context_dir
    )
    if not branch_dir.exists():
        raise RuntimeError(
            f"branch context directory does not exist: {branch_dir}. Run branch-context-setup first."
        )

    payload = {
        "repo_root": str(repo_root),
        "branch": branch_name,
        "branch_key": branch_key,
        "context_dir": resolved_context_dir,
        "branch_dir": str(branch_dir),
        "files": {
            "metadata": str(branch_dir / "metadata.json"),
            "environment": str(branch_dir / "environment.md"),
            "requirement": str(branch_dir / "requirement.md"),
            "development": str(branch_dir / "development.md"),
        },
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def command_sync(args):
    repo_root, branch_name, branch_key, branch_dir, resolved_context_dir = branch_paths(
        args.repo, args.context_dir
    )
    if not branch_dir.exists():
        raise RuntimeError(
            f"branch context directory does not exist: {branch_dir}. Run branch-context-setup first."
        )

    metadata_path = branch_dir / "metadata.json"
    development_path = branch_dir / "development.md"

    if not development_path.exists():
        raise RuntimeError(f"development.md not found: {development_path}")

    facts = collect_facts(repo_root, branch_name)

    metadata = read_metadata(metadata_path)
    metadata.update(
        {
            "repo_root": str(repo_root),
            "branch": branch_name,
            "branch_key": branch_key,
            "context_dir": resolved_context_dir,
            "updated_at": facts["updated_at"],
            "default_base": facts["default_base"],
            "scope_summary": facts["scope_summary"],
        }
    )
    write_metadata(metadata_path, metadata)

    current_development = development_path.read_text(encoding="utf-8")
    updated_development = replace_auto_block(current_development, build_auto_section(facts))
    development_path.write_text(updated_development, encoding="utf-8")

    print(
        json.dumps(
            {
                "repo_root": str(repo_root),
                "branch": branch_name,
                "context_dir": resolved_context_dir,
                "branch_dir": str(branch_dir),
                "updated_at": facts["updated_at"],
                "files_considered": len(
                    set(
                        facts["working_tree_files"]
                        + facts["staged_files"]
                        + facts["untracked_files"]
                        + facts["since_base_files"]
                    )
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def main():
    parser = argparse.ArgumentParser(description="Read or sync branch-scoped context.")

    subparsers = parser.add_subparsers(dest="command", required=True)
    show_parser = subparsers.add_parser("show", help="Show the current branch context paths")
    show_parser.add_argument("--repo", default=".", help="Path inside the target Git repository")
    show_parser.add_argument("--context-dir", help="Repository-local storage root")

    sync_parser = subparsers.add_parser("sync", help="Refresh Git-derived development facts")
    sync_parser.add_argument("--repo", default=".", help="Path inside the target Git repository")
    sync_parser.add_argument("--context-dir", help="Repository-local storage root")

    args = parser.parse_args()

    try:
        if args.command == "show":
            command_show(args)
        elif args.command == "sync":
            command_sync(args)
        else:
            raise RuntimeError(f"unsupported command: {args.command}")
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
