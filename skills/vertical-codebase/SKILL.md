---
name: vertical-codebase
description: Provides architecture advice for organizing code into verticals (grouped by functionality/domain) instead of technical layers. Use when the user writes code, creates files, plans directory structure, asks about project organization, mentions "where should I put this", refactors a codebase, or needs guidance on code colocation, coupling, cohesion, or module boundaries. This is an architectural taste skill — it recommends rather than dictates.
---

# Vertical Codebase

## North Star

> **Organize code by what it _does_, not by what it _is_.**

The directory structure should answer the question "what problem does this solve?" — not "what JavaScript category does this belong to?" A file that handles widget data fetching belongs with the widget component, not in a generic `utils/` folder.

## Core Principles

### 1. Code that changes together lives together

If you touch two files in the same PR most of the time, they belong in the same vertical. This is the litmus test: **would a feature change require touching files scattered across `components/`, `hooks/`, `utils/`, and `types/`?** If yes, regroup them.

**Before (horizontal):**
```
src/components/Widget.tsx
src/hooks/useWidget.ts
src/utils/widgetHelpers.ts
src/types/widget.ts
```

**After (vertical):**
```
src/widgets/
  Widget.tsx
  useWidget.ts
  helpers.ts
  types.ts
```

The `WidgetProps` type lives next to the `Widget` component — they share a public interface, so they should share a directory.

### 2. The right question is "what does this code do?"

Every piece of code solves a problem. Find that problem, and group code by the problems they solve together:

- `src/dashboard/` — everything dashboard-related
- `src/authentication/` — login, sessions, permissions
- `src/payment/` — billing, invoices, checkout
- `src/design-system/` — reusable Button, Modal, tokens

Routes and pages are often the best starting point. If you have a `/dashboard` route, start a `dashboard/` vertical. Widgets used on that dashboard live there too — unless they're used across enough routes to warrant their own vertical.

### 3. Shared code is just a vertical that hasn't been named yet

If something is used by multiple verticals, it **becomes its own vertical** — don't dump it into `shared/` or `common/`. Give it a name that describes what it does:

- `src/page-filters/` — not `src/components/pageFilters` + `src/types/core` + `src/utils/withPageFilters`
- `src/design-system/` — for reusable UI primitives
- `src/i18n/` — for internationalization

A directory named `shared/`, `common/`, or `utils/` is a sign that something hasn't been named properly. If you can't name it, you don't understand it well enough.

### 4. Boundaries are the public interface

Moving code together increases cohesion but doesn't automatically prevent coupling. Every vertical needs a clear public API:

- **Barrel exports**: `src/widgets/index.ts` exports only what other verticals should consume
- **Private internals**: Everything not exported from the barrel is private to the vertical
- **Lint rules**: Use `eslint-plugin-boundaries` to prevent deep imports from private internals
- **Monorepo packages**: Each vertical as its own package with `exports` field in `package.json` — the most explicit form of boundaries

Before importing from another vertical, ask: "is this intended to be public API, or am I reaching into someone's internals?"

### 5. Horizontal grouping is a trap — but a natural one

Everyone starts with `components/`, `hooks/`, `utils/`, `types/`. It feels safe because the answer to "where does this go?" is mechanical rather than thoughtful. But it creates:
- **No discoverability**: 200 files in `components/` with nothing in common
- **No ownership**: Anyone can import anything from anywhere
- **Hidden coupling**: Logically related code scattered across four directories

The moment a codebase grows beyond ~20 files, the horizontal structure becomes a liability. Fixing it later is painful — it's better to start vertical from the beginning.

## When to Apply

| Situation | Recommendation |
|-----------|---------------|
| New project / greenfield | Start vertical from day one. Pages/routes are your first verticals. |
| Adding a feature | Put all feature files in one vertical directory. Types next to component next to hooks. |
| A vertical is growing too large | Split it. If `dashboard/` has 30 files and `dashboard/widgets/` has 15 of them, `widgets` might be its own vertical. |
| Something is used in 3+ places | Make it its own vertical with a clear name and public API. |
| Refactoring an existing horizontal codebase | Move one vertical at a time. Start with the most self-contained feature. Don't try to reorganize everything at once. |

## The Hard Parts (Don't Ignore These)

- **Naming is hard.** A vertical that's too vague (`src/core/`) is almost as bad as `src/utils/`. A vertical that's too specific (`src/blue-login-button/`) isn't reusable. This requires judgment and iteration.
- **Duplication risk.** With "private" code inside verticals, teams might reimplement the same thing. This is a communication problem, not an architecture problem — it surfaces the need for cross-team visibility.
- **Not everything fits cleanly.** Some code is genuinely cross-cutting (logging, analytics, error tracking). These can live at a top level with their own clear vertical name — but resist the urge to call them `common/`.

## Guiding Questions

When deciding where code belongs, ask (in order):

1. **What does this code do?** — Not "what type is it?"
2. **What does it change with?** — What other files are touched in the same PRs?
3. **Who owns it?** — Which team or person would you ask about this code?
4. **Can this be its own vertical?** — If it's shared, give it a name and make it one.
5. **What's the public interface?** — What should other verticals know about?

If you can't answer question 1 clearly, the code might do too much — consider splitting it.

## References

- [The Vertical Codebase — TkDodo](https://tkdodo.eu/blog/the-vertical-codebase)
- [Cognitive Load is what matters](https://github.com/zakirullin/cognitive-load)
- [eslint-plugin-boundaries](https://github.com/javierbrea/eslint-plugin-boundaries)
