"""Unit tests for profile_module.profile.load_profile.

Every test points PROFILE_FILE at a throwaway file inside pytest's tmp_path
fixture (a fresh, auto-cleaned-up temp directory per test), so nothing here
touches the real profile.json in the project root.
"""

import json

import pytest

from profile_module.profile import Profile, load_profile


def _write_profile(path, data):
    path.write_text(json.dumps(data))


def test_load_profile_raises_when_file_missing(tmp_path, monkeypatch):
    monkeypatch.setattr("profile_module.profile.PROFILE_FILE", str(tmp_path / "profile.json"))

    with pytest.raises(RuntimeError):
        load_profile()


def test_load_profile_returns_valid_profile_when_file_exists(tmp_path, monkeypatch):
    profile_file = tmp_path / "profile.json"
    _write_profile(
        profile_file,
        {"interests": ["jazz music", "board games"], "waking_hours_start": 9, "waking_hours_end": 21},
    )
    monkeypatch.setattr("profile_module.profile.PROFILE_FILE", str(profile_file))

    profile = load_profile()

    assert profile == Profile(interests=["jazz music", "board games"], waking_hours_start=9, waking_hours_end=21)


def test_load_profile_raises_on_malformed_json(tmp_path, monkeypatch):
    profile_file = tmp_path / "profile.json"
    profile_file.write_text("{not valid json")
    monkeypatch.setattr("profile_module.profile.PROFILE_FILE", str(profile_file))

    with pytest.raises(json.JSONDecodeError):
        load_profile()


def test_load_profile_raises_when_interests_missing(tmp_path, monkeypatch):
    profile_file = tmp_path / "profile.json"
    _write_profile(profile_file, {"waking_hours_start": 9, "waking_hours_end": 21})
    monkeypatch.setattr("profile_module.profile.PROFILE_FILE", str(profile_file))

    with pytest.raises(RuntimeError):
        load_profile()


def test_load_profile_raises_when_waking_hours_start_missing(tmp_path, monkeypatch):
    profile_file = tmp_path / "profile.json"
    _write_profile(profile_file, {"interests": ["jazz music"], "waking_hours_end": 21})
    monkeypatch.setattr("profile_module.profile.PROFILE_FILE", str(profile_file))

    with pytest.raises(RuntimeError):
        load_profile()


def test_load_profile_raises_when_waking_hours_end_missing(tmp_path, monkeypatch):
    profile_file = tmp_path / "profile.json"
    _write_profile(profile_file, {"interests": ["jazz music"], "waking_hours_start": 9})
    monkeypatch.setattr("profile_module.profile.PROFILE_FILE", str(profile_file))

    with pytest.raises(RuntimeError):
        load_profile()
