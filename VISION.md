# Layton — Vision & Roadmap

Named after [Elizabeth Layton](https://en.wikipedia.org/wiki/Elizabeth_Nel) (later Elizabeth Nel), Winston Churchill's wartime personal secretary — a trusted assistant who anticipated needs, tracked what mattered, and synthesized information so her boss could focus on what only he could do.

## Identity

Layton is a **shareable framework for building personal AI secretaries**.

The problem: your AI assistant starts every conversation at zero. It doesn't know what you were working on, what you're waiting for, or what deserves your attention today. You end up repeating context, managing your own attention, and doing the work your secretary should do.

Layton provides the pattern: an AI assistant that manages attention, synthesizes information from multiple systems, and remembers across sessions. Ask "What should I know?" and get an answer that respects your time.

## The Secretary's Desk

Two objects and one operating principle:

**The notepad** — [Beads](https://github.com/beads-ai/beads-cli) (`bd`) is Layton's memory. Everything tracked, watched, focused on, or dispatched lives as beads. Labels drive state: `watching`, `focus`, `scheduled`, `needs-review`. Beads persist across sessions, branch with git, and resolve conflicts automatically. This is the sole mutable state store — there is no other.

**The filing cabinet** — `.layton/` is Layton's personalization directory. Config, rolodex cards, protocols, errand definitions. These are stable reference materials — AI-readable markdown files that tell Layton how to work with your systems, how to run your processes, and what to do when you're away.

**The thin CLI** — Deterministic operations (health checks, temporal context, config, listing/scheduling) live in the CLI. Synthesis, judgment, conversation, and adaptation live in the AI. The CLI serves the AI, not the other way around.

## Three Primitives

Layton has three building blocks. Each serves a distinct role:

| Primitive | What it is | Execution model | Stored in |
|-----------|-----------|-----------------|-----------|
| **Rolodex card** | How to query an external system (Gmail, Jira, calendar) | Referenced by protocols and errands | `.layton/rolodex/` |
| **Protocol** | Interactive multi-step process (briefings, reviews, authoring) | AI + human in conversation — can pause, branch, ask questions | `.layton/protocols/` |
| **Errand** | Autonomous background task (syncs, checks, reviews) | AI alone, no human — runs unattended, results reviewed later | `.layton/errands/` |

### When to use which

- Need to **query data** from an external system? → Add a **rolodex card**.
- Need to **guide a conversation** with decision points? → Write a **protocol**.
- Need to **run something unattended** and review the result later? → Define an **errand**.

Protocols and errands both reference rolodex cards for external system access. The key difference is human involvement: protocols are interactive, errands are autonomous.

### How they relate

```text
                    ┌──────────────────┐
                    │   Rolodex Cards   │  ← "How to reach Gmail, Jira, etc."
                    │   (data layer)    │
                    └────────┬─────────┘
                             │ referenced by
                ┌────────────┼────────────┐
                ▼                         ▼
       ┌────────────────┐       ┌─────────────────┐
       │   Protocols    │       │    Errands       │
       │ (interactive)  │       │  (autonomous)    │
       │ AI + human     │       │  AI alone        │
       │ ephemeral      │       │  persistent      │
       └────────────────┘       └────────┬────────┘
                                         │ scheduled into
                                         ▼
                                ┌─────────────────┐
                                │  Beads (bd CLI)  │
                                │  (the notepad)   │
                                │  labels, state   │
                                └─────────────────┘
```

An errand is the *recipe* ("how to do a code review"). A bead is the *instance* ("code review #47, scheduled Jan 28, closed with findings"). Recipe vs. execution record.

## Design Principles

1. **Protocols are AI instructions, not code.** Markdown documents the AI reads and follows — not scripts, not YAML pipelines. Users customize by editing prose.

2. **Thin CLI.** Deterministic operations only. Intelligence stays in the AI. The CLI answers "what exists?" — the AI decides "what matters?"

3. **bd is the sole state store.** No `.layton/state.json`, no custom persistence. Beads handles typing, dependencies, git integration, and conflict resolution. Layton doesn't reinvent this.

4. **System-agnostic integration.** Layton doesn't hardcode knowledge of Gmail or Jira. Rolodex cards describe how to reach each system. Swap the card, the protocols adapt.

5. **Self-extending.** Layton can author new rolodex cards, protocols, and errands through its own authoring protocols. The framework grows itself.

## What's Built

- **CLI infrastructure** — doctor (health checks), context (temporal awareness), config (preferences), orientation (single-command status)
- **Three primitives** — rolodex cards, protocols, and errands with templates and authoring protocols for each
- **Errand lifecycle** — schedule from template → autonomous execution → close with findings → human review
- **Self-improvement loop** — errand retrospectives capture proposed updates to cards, protocols, and errand definitions
- **Project instruction auditing** — analyze and improve CLAUDE.md/AGENTS.md files
- **Retrospection protocol** — reflect on completed work and capture improvements
- **Primitive rename** — renamed "skills" → "rolodex" and "bead templates" → "errands" across CLI, modules, templates, references, protocols, specs, tests, and documentation
- **Workflow → Protocol rename** — renamed "workflows" → "protocols" across CLI, modules, templates, references, specs, tests, and documentation to better reflect that these are interactive multi-step processes, not automated pipelines

## What's Next

### 1. First real integration

Use a rolodex card in an actual daily protocol. Pick one system (calendar, email, or task manager), create the card, wire it into a briefing protocol, and validate the end-to-end loop: card → protocol → briefing.

### 2. Briefing synthesis

The original value proposition: "What should I know?" A morning briefing that synthesizes current focus, attention items, and data from rolodex cards into a context-aware summary. This is what Layton was built for — the rest is infrastructure.

### 3. Cross-system correlation

Connecting dots between systems. "This PR is related to that Jira ticket." "The email from Alex is about the same thing you're focused on." This requires entity awareness across rolodex cards.

### 4. Self-improvement feedback loop

Errand retrospectives already capture proposed updates. Close the loop: surface those proposals, apply them, and verify that cards/protocols/errands actually improve over time.

---

> *"Layton, what should I know?"*
>
> *"You're focused on the API refactoring. PR #847 has been waiting for review since Thursday. Your 10am with the platform team is in 40 minutes — you might want to review the agenda. And the stale-items errand flagged 3 watching items that haven't been updated in over a week. Shall I pull those up?"*

That's the destination.
