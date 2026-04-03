# Context Fields

The runtime skill uses four files under the current branch directory.

## requirement.md

Durable human notes:

- business background
- target outcome
- non-goals
- constraints
- acceptance points
- external links

## environment.md

Durable human notes for environments and swimlanes:

- dev / test / staging / prod
- feature flags
- data prerequisites
- dependency services

## development.md

Mixed file:

- Manual section for scope and implementation notes
- Auto-generated block with Git-derived facts

The runtime script must only update the auto-generated block between:

- `<!-- AUTO-GENERATED-START -->`
- `<!-- AUTO-GENERATED-END -->`

## metadata.json

Machine-readable state used by tools:

- repo root
- branch name and sanitized branch key
- timestamps
- default base branch when detected
- scope summary
