"""Shared pytest fixtures for Layton tests."""

import shutil
from pathlib import Path  # noqa: F401 - used in type hints

import pytest


@pytest.fixture
def isolated_env(tmp_path, monkeypatch):
    """Fully isolated environment with temp .layton/ and .beads/."""
    # Create isolated directories
    layton_dir = tmp_path / ".layton"
    layton_dir.mkdir()
    beads_dir = tmp_path / ".beads"
    beads_dir.mkdir()

    # Change working directory to temp (isolates bd auto-detection)
    monkeypatch.chdir(tmp_path)

    return tmp_path


@pytest.fixture
def temp_config(isolated_env):
    """Temporary .layton/config.json for isolated tests."""
    config_path = isolated_env / ".layton" / "config.json"
    return config_path


@pytest.fixture
def mock_beads_available(monkeypatch):
    """Mock bd CLI availability check (unit tests only)."""
    monkeypatch.setattr(
        shutil,
        "which",
        lambda cmd: "/usr/bin/bd" if cmd == "bd" else None,
    )


@pytest.fixture
def mock_beads_unavailable(monkeypatch):
    """Mock bd CLI as unavailable (unit tests only)."""
    monkeypatch.setattr(shutil, "which", lambda cmd: None)


@pytest.fixture
def real_beads_isolated(isolated_env):
    """Real bd CLI in isolated temp directory (integration tests)."""
    # bd will auto-init in isolated_env/.beads/ on first write
    return isolated_env / ".beads"


@pytest.fixture
def temp_rolodex_dir(isolated_env):
    """Temporary .layton/rolodex/ directory for isolated tests."""
    rolodex_dir = isolated_env / ".layton" / "rolodex"
    rolodex_dir.mkdir(exist_ok=True)
    return rolodex_dir


@pytest.fixture
def temp_protocols_dir(isolated_env):
    """Temporary .layton/protocols/ directory for isolated tests."""
    protocols_dir = isolated_env / ".layton" / "protocols"
    protocols_dir.mkdir(exist_ok=True)
    return protocols_dir


@pytest.fixture
def temp_errands_dir(isolated_env):
    """Temporary .layton/errands/ directory for isolated tests."""
    errands_dir = isolated_env / ".layton" / "errands"
    errands_dir.mkdir(exist_ok=True)
    return errands_dir


@pytest.fixture
def temp_skills_root(isolated_env):
    """Temporary skills/ directory (for skill discovery tests)."""
    skills_root = isolated_env / "skills"
    skills_root.mkdir(exist_ok=True)
    return skills_root


@pytest.fixture
def sample_rolodex_card(temp_rolodex_dir):
    """Create a sample rolodex card for testing."""
    card_path = temp_rolodex_dir / "sample.md"
    card_path.write_text("""---
name: sample
description: A sample card for testing
source: skills/sample/SKILL.md
---

## Commands

```bash
sample --help
```

## What to Extract

- Important data
- Key metrics

## Key Metrics

| Metric | Meaning |
|--------|---------|
| count  | Number of items |
""")
    return card_path


@pytest.fixture
def sample_protocol_file(temp_protocols_dir):
    """Create a sample protocol file for testing."""
    protocol_path = temp_protocols_dir / "sample.md"
    protocol_path.write_text("""---
name: sample
description: A sample protocol for testing
triggers:
  - run sample
  - test protocol
---

## Objective

Test the protocol system.

## Steps

1. Get context:
   ```bash
   layton context
   ```

2. Do something

## Context Adaptation

- If morning: do morning things
- If evening: do evening things

## Success Criteria

- [ ] Task completed
- [ ] No errors
""")
    return protocol_path


# Backward compatibility aliases for old fixture names
@pytest.fixture
def temp_skills_dir(temp_rolodex_dir):
    """Alias for temp_rolodex_dir (backward compat)."""
    return temp_rolodex_dir


@pytest.fixture
def temp_beads_dir(temp_errands_dir):
    """Alias for temp_errands_dir (backward compat)."""
    return temp_errands_dir


@pytest.fixture
def sample_skill_file(sample_rolodex_card):
    """Alias for sample_rolodex_card (backward compat)."""
    return sample_rolodex_card


@pytest.fixture
def temp_workflows_dir(temp_protocols_dir):
    """Alias for temp_protocols_dir (backward compat)."""
    return temp_protocols_dir


@pytest.fixture
def sample_workflow_file(sample_protocol_file):
    """Alias for sample_protocol_file (backward compat)."""
    return sample_protocol_file
