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
