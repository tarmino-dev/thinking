#!/usr/bin/env python
"""Seed the database with demo notes for manual/pagination testing.

Creates notes authored by the first existing user (or a freshly created seed
user). Each title carries a unique timestamp suffix, so the script is safe to
run repeatedly without hitting the UNIQUE constraint on Note.title — every run
simply appends more notes.

The target database is whatever SQLALCHEMY_DATABASE_URI points to in your
environment (see the README "Set environment variables" section). Prefer your
local database for testing; to seed the Render database instead, point
SQLALCHEMY_DATABASE_URI at its External Database URL.

Usage:
    ./venv/bin/python scripts/seed_notes.py [--count N] [--no-public]

Options:
    --count N      Number of notes to create (default: 12 — enough for 2 pages).
    --public       Create public notes (default); use --no-public for private.
"""

import argparse
import os
import sys
import time
from datetime import date

# Allow running as "./venv/bin/python scripts/seed_notes.py": add the project
# root (the parent of scripts/) to the import path so "app" can be imported.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # noqa: E402
from app.extensions import db  # noqa: E402
from app.models import User, Note  # noqa: E402
from werkzeug.security import generate_password_hash  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Seed demo notes for testing.")
    parser.add_argument(
        "--count", type=int, default=12,
        help="Number of notes to create (default: 12).",
    )
    parser.add_argument(
        "--public", action=argparse.BooleanOptionalAction, default=True,
        help="Create public notes (default) or use --no-public for private ones.",
    )
    args = parser.parse_args()

    if args.count < 1:
        parser.error("--count must be a positive integer")

    app = create_app()
    with app.app_context():
        user = db.session.execute(db.select(User)).scalars().first()
        if user is None:
            user = User(
                email="seed@example.com",
                password=generate_password_hash("seedpass", method="pbkdf2:sha256", salt_length=16),
                name="Seed User",
            )
            db.session.add(user)
            db.session.commit()

        stamp = int(time.time())  # unique suffix keeps titles unique across runs
        for i in range(1, args.count + 1):
            db.session.add(Note(
                title=f"Pagination demo {stamp}-{i:02d}",
                subtitle="Demo subtitle",
                body="<p>Demo body</p>",
                book="Demo Book",
                is_public=args.public,
                author=user,
                date=date.today().strftime("%B %d, %Y"),
            ))
        db.session.commit()

        total = len(db.session.execute(db.select(Note)).scalars().all())
        visibility = "public" if args.public else "private"
        print(f"Created {args.count} {visibility} note(s) as {user.email}. Total notes now: {total}.")


if __name__ == "__main__":
    main()
