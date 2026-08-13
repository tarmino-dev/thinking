"""User interest profile.

Loaded once from a local profile.json file (gitignored — see
profile.example.json for the expected shape, and README.md for setup). No
database yet — this is deliberately the simplest thing that works for a
single user.
"""

import json
import os
from dataclasses import dataclass

from config import PROFILE_FILE


@dataclass
class Profile:
    """The user's interests and preferred time-of-day window for
    suggestions. interests are free-text phrases (e.g. "jazz music", "board
    games") — classifier_module will later embed these the same way it
    embeds event descriptions, to compare them by meaning.
    """

    interests: list[str]
    waking_hours_start: int
    waking_hours_end: int


def load_profile() -> Profile:
    """Load the user's profile from PROFILE_FILE in the project root."""
    if not os.path.exists(PROFILE_FILE):
        raise RuntimeError(
            f"{PROFILE_FILE} not found. Copy profile.example.json to "
            f"{PROFILE_FILE} and fill in your own interests — see README.md."
        )

    with open(PROFILE_FILE) as f:
        raw = json.load(f)

    return Profile(
        interests=raw["interests"],
        waking_hours_start=raw["waking_hours_start"],
        waking_hours_end=raw["waking_hours_end"],
    )
