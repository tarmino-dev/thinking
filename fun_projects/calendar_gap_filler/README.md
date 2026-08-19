# Calendar Gap Filler

An AI-powered scheduling assistant that finds empty slots in your calendar and
fills them with personalized, locally relevant events based on your interests
and real-time availability.

## Setup

### 1. Install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Google Calendar API credentials

The app reads your Google Calendar (read-only) via the official Google Calendar API.

1. Go to the [Google Cloud Console](https://console.cloud.google.com/) and create a new project.
2. Enable the **Google Calendar API** for that project (APIs & Services → Library).
3. Configure the **OAuth consent screen**:
   - User type: External
   - Publishing status: Testing (no Google verification needed for personal use)
   - Add your own Google account under **Test users**
4. Create credentials: APIs & Services → Credentials → Create Credentials → OAuth client ID.
   - Application type: **Desktop app**
5. Download the resulting JSON file, rename it to `credentials.json`, and place it in the
   project root. This file is gitignored — never commit it.
6. On first run, the app will open a browser window asking you to log in and grant
   read-only calendar access. After that, a `token.json` file is created and cached
   locally so you won't need to log in again (also gitignored).
7. Because the consent screen is in "Testing" status, Google expires `token.json`
   roughly every 7 days regardless of use. If you see an error about the refresh
   token being expired or revoked, just delete `token.json` and run again — the
   browser login flow will repeat and issue a fresh one.

### 3. Ticketmaster API key

Local events are sourced from the [Ticketmaster Discovery API](https://developer.ticketmaster.com/products-and-docs/apis/discovery-api/v2/)
(free tier: 5000 calls/day, 5 requests/second).

1. Register for a developer account at the [Ticketmaster Developer Portal](https://developer-account.ticketmaster.com/user/register).
2. Once logged in, create an app to get your API key (shown on your account/app dashboard).
3. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
4. Open `.env` and paste your key as the value of `TICKETMASTER_API_KEY`. This file is
   gitignored — never commit it.
5. Also in `.env`, set `USER_LATITUDE` and `USER_LONGITUDE` to your approximate home
   coordinates (this is what local events are searched around), and optionally
   `USER_SEARCH_RADIUS_KM` (defaults to 20 if not set).

### 4. Interest profile

1. Copy `profile.example.json` to `profile.json`:
   ```bash
   cp profile.example.json profile.json
   ```
2. Edit `profile.json`: list your own interests as free-text phrases (e.g. "jazz
   music", "board games"), and set `waking_hours_start`/`waking_hours_end` to the
   hours you'd actually want event suggestions in. This file is gitignored — never
   commit it.

### 5. ML ranking model

Event ranking uses a small pretrained TinyBERT model (`sentence-transformers`).
No setup needed — it's downloaded from the Hugging Face Hub automatically the
first time it's used (a couple hundred MB) and cached locally after that. The
first run needs an internet connection; later runs work offline.
