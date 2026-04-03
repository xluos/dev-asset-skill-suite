---
name: branch-context
description: Read and sync branch-scoped requirement context for the current Git repository. Use when continuing work on an existing branch, when the user expects Codex to recover prior requirement or environment notes automatically, or when Codex needs to refresh changed files and change scope from Git before making edits.
---

# Branch Context

Recover requirement context for the current branch from repository-local files, then refresh the Git-derived development snapshot so the next step starts from current facts instead of stale memory.

This skill assumes the repository has already been initialized by `branch-context-setup`.

## Workflow

1. Confirm the current directory is inside a Git repository.
2. Run `scripts/branch_context.py show --repo <repo-path>` to locate and read the branch directory.
3. Read:
   - `requirement.md`
   - `environment.md`
   - `development.md`
4. If the task involves making changes, run `scripts/branch_context.py sync --repo <repo-path>` first, then re-read `development.md`.
5. Summarize the recovered context to the user only as needed; avoid dumping the files verbatim.

## Commands

Read branch context location and current snapshot:

```bash
python3 /absolute/path/to/branch-context/scripts/branch_context.py show --repo <repo-path>
```

Refresh Git-derived information:

```bash
python3 /absolute/path/to/branch-context/scripts/branch_context.py sync --repo <repo-path>
```

If setup stored a custom context root in local Git config, the script picks it up automatically. Only pass `--context-dir` when you need to override that value temporarily.

The `sync` command updates only:

- `metadata.json`
- the auto-generated section inside `development.md`

It does not overwrite manual requirement or environment notes.

## Auto-generated Facts

The sync script derives:

- current branch
- repository root
- tracked modified files
- staged files
- untracked files
- current diff file list relative to working tree
- changed file list relative to the merge-base with the default remote branch when detectable
- scope summary grouped by top-level path

The merge-base comparison is best-effort. If `origin/HEAD` is unavailable, the script falls back to working-tree facts only.

## Trigger Boundary

This skill helps future sessions recover context, but it is not a global middleware. If you need stronger guarantees that Codex always reads branch context before coding, add an instruction in the repository `AGENTS.md` telling Codex to invoke `$branch-context` at the start of Git-repository work.

## Failure Handling

- If the branch context directory does not exist, stop and use `branch-context-setup`.
- If the repository is dirty and the user wants a precise “changed scope”, prefer `sync` before any code edits.
- Do not claim requirement facts that are missing from `requirement.md`; call out the gap.
