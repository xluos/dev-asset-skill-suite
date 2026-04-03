---
name: branch-context-setup
description: Initialize branch-scoped requirement context storage inside the current Git repository. Use when Codex needs to set up a branch-specific context directory, create editable templates for requirement and environment notes, or bootstrap the first-time branch workflow so later sessions can recover context without asking the user to repeat it.
---

# Branch Context Setup

Initialize the current Git repository so future sessions can recover requirement context from a branch-specific directory instead of asking the user to restate background every time.

This skill only handles first-time setup for a repository or a new branch. For ongoing reads and syncs, use the sibling skill `branch-context`.

## Workflow

1. Confirm the current working directory is inside a Git repository.
2. Detect the repository root and current branch.
3. Run `scripts/init_branch_context.py` from this skill against the target repository.
4. Tell the user which directory was created and which files are intended for manual editing.
5. If the user already knows requirement details or environment names, append them immediately after initialization by editing the generated files.

## Command

Run:

```bash
python3 /absolute/path/to/branch-context-setup/scripts/init_branch_context.py --repo <repo-path>
```

Optional flags:

- `--context-dir .xx` to change the repository-local storage root.
- `--branch <branch-name>` to initialize a branch other than the checked-out branch.
- `--env dev --env staging` to seed known environment names during setup.
- `--scope path/a --scope path/b` to seed the initial change scope.

## What Gets Created

The script creates a branch directory under the repository-local context root:

`<repo>/.branch-context/<branch>/`

Files:

- `metadata.json`: branch, repository, timestamps, and storage settings.
- `environment.md`: manually maintained environment and swimlane notes.
- `requirement.md`: manually maintained requirement summary, constraints, links, and acceptance notes.
- `development.md`: mixed file containing generated Git-derived facts plus manually editable notes.

The script also:

- stores the chosen context root in local Git config under `branch-context.dir`
- adds the context root to `.git/info/exclude` so these notes do not pollute normal change lists

See `references/storage-layout.md` for the file contract.

## Editing Guidance

After setup, prioritize filling these fields because Git cannot infer them reliably:

- Which environments or swimlanes are involved
- Requirement summary and non-obvious constraints
- External links such as ticket, doc, or PR references

Do not try to infer requirement truth from branch name alone. A branch can be stale, overloaded, or renamed.

## Failure Handling

- If the current directory is not inside a Git repository, stop and ask the user for the target repository path.
- If the branch is detached, require an explicit `--branch`.
- If the directory already exists, do not overwrite manual notes; the script is idempotent and only fills missing files.
