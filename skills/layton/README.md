# Layton Skill - Technical Notes

## CLAUDE_PLUGIN_ROOT Issue and Workaround

### Problem

This skill originally used `${CLAUDE_PLUGIN_ROOT}` to reference its bundled scripts, following what appeared to be standard practice for Claude Code plugins/skills. However, `${CLAUDE_PLUGIN_ROOT}` **does not work in skill markdown files** - it only works in JSON configuration files (hooks, MCP servers).

**Related Issue:** [anthropics/claude-code#9354](https://github.com/anthropics/claude-code/issues/9354)

When skills try to use:
```bash
${CLAUDE_PLUGIN_ROOT}/scripts/layton
```

The variable is empty/undefined, resulting in:
```bash
/scripts/layton  # Invalid path - fails with "no such file or directory"
```

### Solution

**Verdict:** Use relative paths from project root instead of environment variables.

Since skills follow the `.claude/skills/<skill-name>/` convention by design, we use:
```bash
.claude/skills/layton/scripts/layton
```

This works because:
- ✅ **Portable** - Works for any user without environment setup
- ✅ **Standard** - Skills live in `.claude/skills/` by convention
- ✅ **Simple** - No dependency on broken environment variables
- ✅ **Reliable** - No workarounds or shell scripts needed

### Implementation

All references to `${CLAUDE_PLUGIN_ROOT}` in SKILL.md have been replaced with `.claude/skills/layton/scripts/layton`.

Users do NOT need to set any environment variables. The skill works out of the box.

### Alternative (Optional)

Users can optionally set `LAYTON` in their shell config for convenience:
```bash
export LAYTON=".claude/skills/layton/scripts/layton"
```

But this is **not required** - the skill references the full relative path directly.

### When Will This Be Fixed Upstream?

Issue #9354 is open as of February 2026. Until Claude Code implements `CLAUDE_PLUGIN_ROOT` support in markdown contexts, **relative paths are the recommended approach** for all skills.

---

**Last Updated:** 2026-02-03
