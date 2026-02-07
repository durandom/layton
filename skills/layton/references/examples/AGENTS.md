# Agent Instructions

## ⚠️ MANDATORY: Session Start Protocol

**BEFORE doing ANYTHING else in a new session, you MUST:**

1. **Invoke the Layton skill**: `/layton` (no parameters)

**NO EXCEPTIONS** — unless the user explicitly says "skip Layton".

## Primary Entry Point: Layton

The `/layton` skill provides:

- **checks**: Status of integrations and config
- **skills**: Available data sources
- **workflows**: Available workflows with trigger phrases

Layton provides context-aware briefings and orchestrates other skills.
