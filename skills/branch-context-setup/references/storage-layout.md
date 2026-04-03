# Storage Layout

The setup skill creates one repository-local directory per branch:

`<repo>/.branch-context/<branch-key>/`

`branch-key` is derived from the branch name by replacing `/` with `__`.

Files:

## metadata.json

Machine-oriented record of repository path, branch, timestamps, and the chosen context root.

## environment.md

Human-maintained notes about swimlanes, environments, toggles, and deployment prerequisites.

## requirement.md

Human-maintained requirement notes. This is the durable source for background, goal, constraints, and acceptance notes that Git cannot infer.

## development.md

Mixed file:

- Manual top section for change scope, risk notes, and implementation decisions
- Auto-generated block delimited by:
  - `<!-- AUTO-GENERATED-START -->`
  - `<!-- AUTO-GENERATED-END -->`

The runtime skill refreshes only the delimited block.
