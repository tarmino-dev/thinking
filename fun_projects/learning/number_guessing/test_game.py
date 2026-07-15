import pytest
from game import get_difficulty, get_user_guess

# Using monkeypatch to simulate user input

def test_get_difficulty_easy(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "easy")
    assert get_difficulty() == 10

def test_get_difficulty_hard(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "hard")
    assert get_difficulty() == 5

def test_get_user_guess_valid(monkeypatch):
    """Imitating of valid input"""
    monkeypatch.setattr("builtins.input", lambda _: "42")
    assert get_user_guess() == 42

def test_get_user_guess_invalid_then_valid(monkeypatch):
    """Imitating of invalid input and valid input"""
    inputs = iter(["abc", "100"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    assert get_user_guess() == 100
