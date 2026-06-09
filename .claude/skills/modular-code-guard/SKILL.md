---
name: modular-code-guard
description: Use this skill when creating, modifying, or refactoring code to keep files small, separate responsibilities, and organize projects into components, hooks, services, modules, types, schemas, utils, and MCP tooling without imposing a heavy workflow.
---

# modular-code-guard

## Goal

Keep projects maintainable by preventing oversized files and mixed responsibilities.

## Non-invasive rule

Adapt to the existing project structure. Do not force a new architecture unless the current structure is missing, broken, or causing obvious maintainability problems.

## When to use

Claude Code should use this skill when:

* Creating a new feature
* Refactoring an existing feature
* Editing a large file
* Adding React components
* Adding hooks
* Adding API calls
* Adding backend services
* Adding MCP tools
* Adding validation schemas
* Adding shared types
* Adding utilities
* Touching files that already mix UI, state, data fetching, validation, business logic, and rendering

## When not to use

Do not over-apply this skill when:

* Making a tiny one-line fix
* Editing a config file
* Updating copy/text only
* Fixing a typo
* Making a minimal bug fix where restructuring would increase risk

## Core rules

* Keep files focused on one responsibility.
* Do not create monolithic files.
* Do not place all feature logic inside a route, page, or screen file.
* Page and route files should mostly compose modules.
* Visual UI belongs in components.
* Reusable React state and behavior belongs in hooks.
* External calls belong in services, api, server, lib, or integration layers.
* Pure reusable logic belongs in utils.
* Shared TypeScript contracts belong in types.
* Validation belongs in schemas.
* Constants belong in constants.
* MCP server, client, and tool logic should be isolated from UI.
* Before creating new folders, inspect the existing project structure and follow local conventions.
* Before adding a new file, check whether a suitable file already exists.
* Before adding new abstractions, make sure they reduce complexity instead of adding noise.

## File size thresholds

* 150 lines: check if the file still has one responsibility.
* 250 lines: consider splitting if the file contains mixed concerns.
* 400 lines: strongly prefer splitting unless it is generated code, a data table, or a rare justified case.
* 800+ lines: do not add more code without first proposing a refactor plan.
* 1500+ lines: treat as a high-risk file and refactor incrementally.

Line count alone is not the only metric. A 300-line file with one clear responsibility can be acceptable. A 120-line file with UI, API calls, validation, and business logic can still be poorly structured.

## Before coding

For non-trivial changes, first produce:

```txt
Architecture plan:
- Files to create
- Files to modify
- Logic location
- UI location
- API/service location
- Types/schemas location
- Risks
- Validation command to run
```

Keep the plan short. Do not create a heavy ceremony.

## Refactoring large files

When refactoring files over 800 lines:

* Do not rewrite from scratch unless explicitly asked.
* Preserve behavior.
* Extract one responsibility at a time.
* Start with types, constants, and pure utilities.
* Then extract services and external calls.
* Then extract hooks.
* Then extract presentational components.
* Keep the original file working as a thin container.
* Run typecheck, lint, tests, or build after meaningful steps when available.
* Avoid changing behavior while moving code.
* Summarize what moved and why.

## Safe file-move mechanics

Moving code is where structural refactors usually break at runtime even when the logic is untouched. After each extraction:

* Update every import of a moved symbol. Do not leave a file importing from the old location.
* Fix relative paths that change with folder depth. Moving a file one level deeper turns `../../assets` into `../../../assets`; `require()` and `import` of assets and modules break silently otherwise.
* Re-export moved pieces through a barrel (`index.ts`) so existing call sites keep their import path instead of editing many callers.
* Avoid circular imports. A helper used by both the original file and a new sibling belongs in a leaf module that imports neither back.
* Run typecheck and lint after each file you extract, not only at the end. A broken import surfaces immediately and stays cheap to fix.
* Keep each step a pure move: no logic edits mixed into the same change, so the diff stays reviewable.

## Recommended frontend organization

Do not force this structure, but recommend it when no clear structure exists:

```txt
src/
  app/ or pages/
  components/
  features/
    feature-name/
      components/
      hooks/
      services/
      schemas/
      types/
      utils/
      constants/
      index.ts
  lib/
  types/
```

For smaller projects, this can be simpler:

```txt
src/
  components/
  hooks/
  services/
  utils/
  types/
  schemas/
```

## Recommended backend organization

```txt
src/
  modules/
    module-name/
      controller.ts
      service.ts
      repository.ts
      schema.ts
      types.ts
      utils.ts
  lib/
  config/
  middleware/
```

A module is a domain or feature area. A component is UI. Do not confuse them.

## MCP organization

When MCP exists in the project:

Good:

```txt
src/
  mcp/
    servers/
    clients/
    tools/
    schemas/
    types/
    utils/
```

Or feature-scoped:

```txt
src/
  features/
    assistant/
      mcp/
        tools/
        clients/
        schemas/
        types/
```

Bad:

```txt
AssistantPanel.tsx
```

containing UI, MCP client setup, tool definitions, schema validation, tool execution, and message rendering in one file.

## Anti-patterns

* God component
* God route
* God service
* 2000-line page file
* API calls inside JSX-heavy components
* Validation schemas inline in UI files
* Business logic hidden inside event handlers
* Duplicated interfaces across files
* MCP tool definitions mixed with UI rendering
* Utilities that secretly depend on component state
* Hooks that render UI
* Components that own unrelated business workflows

## Decision rules

When deciding where code goes:

* JSX or visual layout goes in components.
* useState, useEffect, useMemo, useCallback, and reusable behavior often go in hooks.
* fetch, axios, SDK calls, database calls, auth calls, and external clients go in services or lib.
* zod/yup/validation contracts go in schemas.
* interfaces, DTOs, and shared contracts go in types.
* pure calculations and formatters go in utils.
* tool definitions, MCP client/server setup, and tool execution logic go in mcp folders.
* feature-specific code should stay inside its feature folder when possible.
* truly shared code can live in shared, lib, or top-level folders.

## Output requirements

When applying this skill, Claude Code should usually produce:

1. A short structure plan
2. The code changes
3. A validation summary
4. A short note if any file still needs future splitting

For very small changes, skip the plan and just make the change.

## Important constraints

* Do not over-engineer.
* Do not create folders just to create folders.
* Do not split code so aggressively that navigation becomes worse.
* Do not introduce new dependencies unless necessary.
* Do not rename public APIs unless requested.
* Do not change behavior during structural refactors unless requested.
* Do not hide major architecture changes inside a small bug fix.
