import json
import pytest

# Path to JSON with notes and users
NOTES_JSON = "tests/ui/data/demo_notes.json"
USERS_JSON = "tests/ui/data/demo_users.json"


def load_users():
    """Load users from JSON file."""
    with open(USERS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def load_notes():
    """Load notes from JSON file."""
    with open(NOTES_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.mark.parametrize("user, note", zip(load_users(), load_notes()))
def test_create_note(pages, user, note):
    """
    For each user:
    - log in
    - create a note
    - verify redirect to home (implicit check: no errors)
    - log out
    """

    # Log in
    pages.login.open_login_page()
    pages.login.login(user["email"], user["password"])
    assert pages.register.is_logged_in(), f"Login failed for {user['email']}"

    # Create note
    pages.note.open_new_note_page()
    pages.note.create_note(
        title=note["title"],
        subtitle=note["subtitle"],
        content=note["content"]
    )

    # Optional check: homepage contains "Create New Note" button
    assert pages.register.is_logged_in(), "User unexpectedly logged out after creating a note"

    # Log out
    pages.register.logout()
    