"""Unit tests for config module."""

import sys
from pathlib import Path

import pytest

# Add laytonlib to path for testing
sys.path.insert(
    0,
    str(Path(__file__).parent.parent.parent / "skills" / "layton" / "scripts"),
)

from laytonlib.config import (
    collect_keys,
    detect_skill_directory,
    find_vault_root,
    get_default_config,
    get_nested,
    load_config,
    parse_value,
    save_config,
    set_nested,
)


class TestGetNested:
    """Tests for dot-notation get."""

    def test_flat_key(self):
        """Get flat key."""
        data = {"timezone": "UTC"}
        assert get_nested(data, "timezone") == "UTC"

    def test_nested_key(self):
        """Get nested key."""
        data = {"work": {"schedule": {"start": "09:00"}}}
        assert get_nested(data, "work.schedule.start") == "09:00"

    def test_get_object(self):
        """Get returns entire object."""
        data = {"work": {"schedule": {"start": "09:00", "end": "17:00"}}}
        result = get_nested(data, "work.schedule")
        assert result == {"start": "09:00", "end": "17:00"}

    def test_missing_key(self):
        """Missing key raises KeyError."""
        data = {"timezone": "UTC"}
        with pytest.raises(KeyError):
            get_nested(data, "nonexistent")

    def test_missing_nested_key(self):
        """Missing nested key raises KeyError."""
        data = {"work": {}}
        with pytest.raises(KeyError):
            get_nested(data, "work.schedule.start")


class TestSetNested:
    """Tests for dot-notation set."""

    def test_set_flat_key(self):
        """Set flat key."""
        data = {}
        set_nested(data, "timezone", "UTC")
        assert data == {"timezone": "UTC"}

    def test_set_nested_key(self):
        """Set nested key creates path."""
        data = {}
        set_nested(data, "work.schedule.start", "09:00")
        assert data == {"work": {"schedule": {"start": "09:00"}}}

    def test_set_overwrites_existing(self):
        """Set overwrites existing value."""
        data = {"timezone": "UTC"}
        set_nested(data, "timezone", "America/Los_Angeles")
        assert data["timezone"] == "America/Los_Angeles"

    def test_set_adds_to_existing(self):
        """Set adds to existing structure."""
        data = {"work": {"schedule": {"start": "09:00"}}}
        set_nested(data, "work.schedule.end", "17:00")
        assert data["work"]["schedule"]["end"] == "17:00"


class TestCollectKeys:
    """Tests for key collection."""

    def test_flat_keys(self):
        """Collect flat keys."""
        data = {"a": 1, "b": 2}
        keys = collect_keys(data)
        assert sorted(keys) == ["a", "b"]

    def test_nested_keys(self):
        """Collect nested keys."""
        data = {"work": {"schedule": {"start": "09:00", "end": "17:00"}}}
        keys = collect_keys(data)
        assert sorted(keys) == ["work.schedule.end", "work.schedule.start"]

    def test_mixed_keys(self):
        """Collect mixed flat and nested keys."""
        data = {
            "timezone": "UTC",
            "work": {"schedule": {"start": "09:00"}},
        }
        keys = collect_keys(data)
        assert sorted(keys) == ["timezone", "work.schedule.start"]


class TestParseValue:
    """Tests for value parsing."""

    def test_string(self):
        """Plain string returned as-is."""
        assert parse_value("hello") == "hello"

    def test_number(self):
        """JSON number parsed."""
        assert parse_value("42") == 42
        assert parse_value("3.14") == 3.14

    def test_boolean(self):
        """JSON boolean parsed."""
        assert parse_value("true") is True
        assert parse_value("false") is False

    def test_object(self):
        """JSON object parsed."""
        result = parse_value('{"start": "09:00"}')
        assert result == {"start": "09:00"}

    def test_array(self):
        """JSON array parsed."""
        result = parse_value("[1, 2, 3]")
        assert result == [1, 2, 3]


class TestDefaultConfig:
    """Tests for default config."""

    def test_has_timezone(self):
        """Default config has timezone."""
        config = get_default_config()
        assert "timezone" in config

    def test_has_work_schedule(self):
        """Default config has work schedule."""
        config = get_default_config()
        assert config["work"]["schedule"]["start"] == "09:00"
        assert config["work"]["schedule"]["end"] == "17:00"


class TestFindVaultRoot:
    """Tests for vault root discovery via .layton/config.json marker."""

    def test_finds_vault_in_cwd(self, tmp_path, monkeypatch):
        """Finds vault when .layton/config.json is in cwd."""
        (tmp_path / ".layton").mkdir()
        (tmp_path / ".layton" / "config.json").write_text("{}")
        monkeypatch.chdir(tmp_path)

        assert find_vault_root() == tmp_path

    def test_finds_vault_in_parent(self, tmp_path, monkeypatch):
        """Walks up and finds vault in a parent directory."""
        (tmp_path / ".layton").mkdir()
        (tmp_path / ".layton" / "config.json").write_text("{}")
        child = tmp_path / "sub" / "deep"
        child.mkdir(parents=True)
        monkeypatch.chdir(child)

        assert find_vault_root() == tmp_path

    def test_returns_none_when_no_vault(self, tmp_path, monkeypatch):
        """Returns None when no .layton/config.json exists anywhere up."""
        monkeypatch.chdir(tmp_path)

        assert find_vault_root() is None

    def test_finds_layton_dir_without_config(self, tmp_path, monkeypatch):
        """A .layton/ directory without config.json is still a vault."""
        (tmp_path / ".layton").mkdir()
        # No config.json inside — but .layton/ directory exists
        monkeypatch.chdir(tmp_path)

        assert find_vault_root() == tmp_path

    def test_finds_nearest_vault(self, tmp_path, monkeypatch):
        """When nested vaults exist, returns the nearest (deepest) one."""
        # Outer vault
        (tmp_path / ".layton").mkdir()
        (tmp_path / ".layton" / "config.json").write_text("{}")
        # Inner vault
        inner = tmp_path / "project"
        (inner / ".layton").mkdir(parents=True)
        (inner / ".layton" / "config.json").write_text("{}")
        monkeypatch.chdir(inner)

        assert find_vault_root() == inner


class TestDetectSkillDirectory:
    """Tests for detecting when running from the Layton skill directory."""

    def test_detects_skill_directory(self, tmp_path, monkeypatch):
        """Returns True when SKILL.md and scripts/laytonlib/ exist."""
        (tmp_path / "SKILL.md").write_text("# Layton")
        (tmp_path / "scripts" / "laytonlib").mkdir(parents=True)
        monkeypatch.chdir(tmp_path)

        assert detect_skill_directory() is True

    def test_false_without_skill_md(self, tmp_path, monkeypatch):
        """Returns False when SKILL.md is missing."""
        (tmp_path / "scripts" / "laytonlib").mkdir(parents=True)
        monkeypatch.chdir(tmp_path)

        assert detect_skill_directory() is False

    def test_false_without_laytonlib(self, tmp_path, monkeypatch):
        """Returns False when scripts/laytonlib/ is missing."""
        (tmp_path / "SKILL.md").write_text("# Something")
        monkeypatch.chdir(tmp_path)

        assert detect_skill_directory() is False

    def test_false_in_normal_project(self, tmp_path, monkeypatch):
        """Returns False in a normal project directory."""
        (tmp_path / ".layton").mkdir()
        (tmp_path / ".layton" / "config.json").write_text("{}")
        monkeypatch.chdir(tmp_path)

        assert detect_skill_directory() is False


class TestLoadSaveConfig:
    """Tests for config persistence."""

    def test_load_missing_returns_none(self, isolated_env):
        """Load missing config returns None."""
        config_path = isolated_env / ".layton" / "config.json"
        if config_path.exists():
            config_path.unlink()

        result = load_config()
        assert result is None

    def test_save_and_load(self, isolated_env):
        """Save then load returns same config."""
        config = {"test": "value"}
        assert save_config(config) is True

        loaded = load_config()
        assert loaded == config
