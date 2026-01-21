# Layton

**Your personal AI secretary.**

Named after [Elizabeth Layton](https://en.wikipedia.org/wiki/Elizabeth_Nel), Churchill's wartime secretary - a trusted assistant who anticipated needs, tracked what mattered, and synthesized information so her boss could focus on what only he could do.

## The Problem

Your AI assistant starts every conversation at zero. It doesn't know what you were working on, what you're waiting for, or what deserves your attention today. You end up repeating context, losing track of threads, and managing your own attention instead of doing the actual work.

## The Vision

Layton remembers for you:

- **What you're watching** - that PR waiting for review, the Jira ticket blocked on someone else
- **Where your focus is** - your current work, so you can context-switch and return
- **How you work** - your schedule, preferences, and patterns
- **What's happening** - synthesized briefings across all your connected systems

Ask "What should I know?" and get an answer that respects your time.

## Installation

```bash
claude plugin marketplace add durandom/layton
claude plugin install --scope project layton@layton
```

## Prerequisites

[Beads](https://github.com/beads-ai/beads-cli) - Layton's memory and notepad.

```bash
bd --version  # verify it's installed
```

## Getting Started

```text
/layton
```

Layton will guide you through setup and explain what it can do.

## Learn More

See the `examples/` directory for workflow patterns you can adapt.

## License

MIT
