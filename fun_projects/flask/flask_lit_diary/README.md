# Literature Diary

A minimalistic yet elegant Flask web application designed for writers, readers, and creative thinkers to capture their thoughts, reflections, and inspirations.  
With its warm aesthetic and intuitive interface, Literature Diary blends the charm of traditional journaling with the power of modern web technology.

## Features

- Create, edit, and delete personal notes  
- Public/private note visibility — keep notes to yourself or share them with all visitors  
- "My Notes" personal feed — see all your notes, including private ones  
- Paginated notes lists — 10 notes per page, newest first, with `?page=` navigation  
- Optional `book` field for notes, which utilizes the Open Library API for book search  
- User authentication (register, login, logout)  
- Password reset via email link  
- Account Settings page — download your data, change your password, or delete your account  
- GDPR data export — download all your notes and comments as JSON  
- Privacy Policy page and cookie consent banner  
- Contact form with SendGrid email integration  
- Self-hosted fonts and icons — no CDN calls to Google Fonts or Font Awesome  
- Clean and cozy interface with warm, book-like tones  
- Multilingual UI (English and Ukrainian) with an in-page language switcher, preference stored per session  
- Structured templates powered by Flask Blueprints  
- SQLite or PostgreSQL database support  
- Gravatar integration for user avatars  
- Bootstrap 5 and CKEditor for rich-text editing  
- REST API for programmatic access  

## Project Structure

The project follows a modular Flask architecture:

- `app/` — main application package  
  - `api/` — REST API (v1)  
  - `routes/` — organized Blueprints (`main`, `auth`, `notes`)  
  - `models/` — SQLAlchemy models  
  - `forms/` — Flask-WTF form definitions  
  - `utils/` — utility functions and decorators (e.g., `admin_only`)  
  - `templates/` — feature-based HTML templates  
  - `static/` — CSS, JS, and image assets  
- `tests/` —  Unit tests
  - `api/` - REST API tests  
  - `ui/` - UI and browser tests  
- `config.py` — environment configuration  
- `main.py` — application entry point  
- `requirements.txt` — dependencies  
- `README.md` — project documentation

## Installation and Setup

### 1. Clone only the `blog_to_deploy` branch

`git clone -b blog_to_deploy https://github.com/tarmino-dev/thinking.git`  
`cd thinking/fun_projects/flask/flask_lit_diary`

### 2. Create and activate a virtual environment

`python3 -m venv venv`  
`source venv/bin/activate`   # on macOS/Linux  
`venv\Scripts\activate`      # on Windows

### 3. Install dependencies

`pip install -r requirements.txt`

### 4. Notes on SendGrid setup

1. Sign up at https://sendgrid.com
2. In your SendGrid dashboard, go to Settings → API Keys and create a new key with "Full Access" or "Mail Send" permissions.
3. Verify your sender identity in Settings → Sender Authentication → Single Sender Verification.
4. The email you verify here must match the value of `GMAIL_EMAIL` in your environment variables (see below).
5. Once verified, you'll be able to send emails through your Flask contact form and password reset flow.

### 5. Set environment variables

Environment variables are read from your system configuration, for example from `~/.zshrc` or system environment settings.
Add the following lines to your shell configuration file:

`export FLASK_KEY=your_secret_key`  
`export SQLALCHEMY_DATABASE_URI=sqlite:///literature_diary.db`  
`export GMAIL_EMAIL=your_verified_sender@example.com`  
`export SENDGRID_API_KEY=your_sendgrid_api_key`

> **Note:** `GMAIL_EMAIL` is the SendGrid verified sender address used for outgoing email (contact form replies and password reset links). It does not have to be a Gmail address — any address verified with SendGrid works.

For production deployments served over HTTPS, also set:

`export SESSION_COOKIE_SECURE=true`

After editing, reload your terminal session or run:

`source ~/.zshrc`     # on macOS/Linux

## Run the application

The application is launched by running the main.py file located in the project root.

`python main.py`

Then open your browser and visit:

http://localhost:5000

## Running Tests

The test suite is split into unit/API tests (no server required) and browser tests (requires a running server).

### Unit and API tests

`python -m pytest tests/ --ignore=tests/ui -q`

These tests run against an in-memory SQLite database and do not require any environment setup beyond installing dependencies.

### Browser tests (Selenium)

Start the application first (`python main.py`), then in a separate terminal:

`python -m pytest tests/ui/ -v`

Selenium tests require Google Chrome and `chromedriver` to be installed. The base URL defaults to `http://localhost:5000` and can be overridden with the `BASE_URL` environment variable.

## Seeding demo data

To populate the database with sample notes — for example, to exercise the
paginated notes list — use the seeding script. Titles are made unique per run,
so it is safe to run repeatedly (each run appends more notes):

`./venv/bin/python scripts/seed_notes.py --count 12`

Notes are public by default (visible on the home page); pass `--no-public` to
create private ones. The script writes to whatever `SQLALCHEMY_DATABASE_URI`
points to, so prefer your local database when testing.

## Deployment

Literature Diary is optimized for deployment on Render, Railway, or Heroku.

To deploy:

1. Set your environment variables in the hosting service dashboard
2. Push your latest code to the main branch
3. Wait for automatic deployment to complete

## Database backup & rollback

The production database (PostgreSQL on Render) can be backed up and rolled back
with the helper scripts in `scripts/`, run locally against the database's
**External Database URL**. Each script reads its connection URL from an
environment variable (set it in your shell profile, e.g. `~/.zshrc`, rather than
inline — see each script's header) and never prints credentials. Dumps are
written to the git-ignored `backups/` directory.

- **Back up** — `scripts/db_backup.sh` reads `SOURCE_DATABASE_URL` and writes a
  timestamped custom-format dump to `backups/`.
- **Roll back in place** — `scripts/db_rollback.sh BACKUP_FILE` reads
  `TARGET_DATABASE_URL` and reverts that same database to the given dump. This is
  destructive — it overwrites current data and asks for confirmation; take a
  fresh backup first if you might want to undo it.
- **Restore into a new database** — `scripts/db_restore.sh BACKUP_FILE` restores
  a dump into a freshly created, empty database (e.g. when provisioning a new
  Render instance).

## API

The project provides a REST API that exposes the core functionality of the application.
The API coexists with the HTML-based interface and follows REST principles.

### Base URL
```
/api/v1
```

### Authentication
- `GET /api/v1/notes` returns all public notes without authentication. Authenticated users also receive their own private notes in the response.
- Write operations (create, update, delete) require authentication.
- Authentication is session-based (Flask-Login).
- Only the owner of a resource can update or delete it.

### Notes Endpoints

#### Get all notes
```
GET /api/v1/notes
```

Returns public notes. Authenticated users also see their own private notes.

Response example:
```json
{
  "total": 2,
  "items": [
    {
      "id": 1,
      "title": "Reading reflection",
      "subtitle": "Notes after session",
      "book": "Sample Book Title — Sample Author",
      "date": "2026-01-01",
      "is_public": true,
      "author": {
        "id": 1,
        "name": "Sample User"
      }
    }
  ]
}
```

---

#### Create a note (authenticated)
```
POST /api/v1/notes
```

Request body:
```json
{
  "title": "Reading reflection",
  "subtitle": "Notes after session",
  "body": "Reflection on chapter themes.",
  "book": "Sample Book Title — Sample Author",
  "img_url": "https://example.com/image.png"
}
```

Optional fields:
- `is_public` (boolean, default `true`) — sets note visibility
- `book` (string) — free-text metadata in format like `Title — Author`

Responses:
- `201 Created` – note successfully created
- `401 Unauthorized` – authentication required
- `400 Bad Request` – validation or input error

---

#### Update a note (authenticated, owner only)
```
PUT /api/v1/notes/<id>
```

Request body (partial update supported):
```json
{
  "title": "Updated reflection",
  "body": "Updated reflection on chapter themes.",
  "book": "Another Sample Book Title — Another Sample Author"
}
```

You may include:
- `is_public` to switch between public and private
- `book` to set or update book metadata

Responses echo these fields like `POST` and `GET`.

Responses:
- `200 OK`
- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`
- `400 Bad Request`

---

#### Delete a note (authenticated, owner only)
```
DELETE /api/v1/notes/<id>
```

Responses:
- `204 No Content`
- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`

---

### Data Export Endpoint

#### Export your data (authenticated)
```
GET /api/v1/export
```

Returns the authenticated user's full profile, notes, and comments as JSON. This endpoint implements the GDPR right to data portability (Art. 20) and is also accessible from the Account Settings page in the UI.

Response example:
```json
{
  "profile": {
    "id": 1,
    "email": "user@example.com",
    "name": "Alice"
  },
  "notes": [
    {
      "id": 3,
      "title": "My Note",
      "subtitle": "A subtitle",
      "date": "June 01, 2026",
      "body": "<p>…</p>",
      "img_url": null,
      "book": "Dune",
      "is_public": true
    }
  ],
  "comments": [
    {
      "id": 7,
      "text": "<p>Great book!</p>",
      "note_id": 5,
      "note_title": "Another Note"
    }
  ]
}
```

Responses:
- `200 OK`
- `401 Unauthorized`

### API Testing

The API is covered by automated tests written with `pytest` using Flask's test client.

Test location:
```
tests/api/
```

Each endpoint is tested for both successful and error scenarios (authentication, authorization, validation).

## Technologies Used

- Python 3.10+
- Flask
- SQLAlchemy
- Bootstrap 5
- CKEditor
- SendGrid API

## Author

Literature Diary is developed by tarmino-dev.
Inspired by the timeless art of journaling and the "Blog" project concept from the [100 Days of Python](https://www.udemy.com/course/100-days-of-code/) course, modernized and refactored for production-style readability.

## License

This project is intended for educational and portfolio purposes only.

## Acknowledgements

Special thanks to:

- The Flask and Python community
- Bootstrap and Font Awesome contributors
- The writers and thinkers who inspired this project
