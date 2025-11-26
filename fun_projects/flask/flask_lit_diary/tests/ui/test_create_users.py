import json
import pytest

# Path to JSON with users
USERS_JSON = "tests/ui/data/demo_users.json"


def load_users():
    """Load users from JSON file."""
    with open(USERS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.mark.parametrize("user", load_users())
def test_create_user(pages, user):
    """
    Create a user via UI registration form and verify success message.
    Each test iteration uses one user from JSON.
    """
    # Open the registration page
    pages.register.open_register_page()

    # Fill out and submit the registration form
    pages.register.register(
        name=user["name"],
        email=user["email"],
        password=user["password"]
    )

    # Verify that the logout button is visible
    assert pages.register.is_logged_in(), f"Registration failed for: {user['email']}"

    # Logout for next user
    pages.register.logout()