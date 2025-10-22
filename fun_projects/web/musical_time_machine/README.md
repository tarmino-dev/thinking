# Musical Time Machine

**Musical Time Machine** is a Python mini-project that combines **web scraping** and the **Spotify API** to recreate the Billboard Hot 100 playlist for any historical date.  
Enter a date like `1985-08-10`, and the script will:
1. Scrape Billboard’s chart for that day.
2. Find matching songs on Spotify.
3. Create a private Spotify playlist containing those tracks — instantly.

---

## Features

- Scrapes Billboard Hot 100 songs for any user-provided date.
- Searches and retrieves matching tracks from Spotify.
- Automatically creates a **private Spotify playlist**.
- Includes structured logging and graceful error handling.


---

## Setup

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/musical_time_machine.git
cd musical_time_machine
```

### 2. Create a Virtual Environment (recommended)
```bash
python -m venv venv
source venv/bin/activate      # On macOS/Linux
venv\Scripts\activate       # On Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Spotify Credentials

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
2. Create an **App** and note your:
   - `Client ID`
   - `Client Secret`
   - `Redirect URI` (use something like `http://localhost:8888/callback`)
3. Create a `.env` file in your project root (three levels above this script) and add:
   ```bash
   SPOTIPY_CLIENT_ID=your_client_id
   SPOTIPY_CLIENT_SECRET=your_client_secret
   SPOTIPY_REDIRECT_URI=your_redirect_uri
   ```

---

## Usage

Run the script:
```bash
python main.py
```

You’ll be prompted to enter a date:
```
Enter a date (YYYY-MM-DD) to travel back to:
```

The program will:
1. Scrape Billboard Hot 100 songs for that date.
2. Authenticate your Spotify account.
3. Create a **private playlist** named:
   ```
   YYYY-MM-DD Billboard 100
   ```
4. Add available tracks automatically.

---

## Example

```
$ python main.py
Enter a date (YYYY-MM-DD) to travel back to: 1999-11-20
[INFO] Fetching Billboard Hot 100 for 1999-11-20
[INFO] Found 100 songs.
[INFO] Created playlist: 1999-11-20 Billboard 100
[INFO] Added 92 tracks to playlist.
Playlist successfully created!
```

---

## Error Handling

- Songs not found on Spotify are gracefully skipped with a warning.
- API or connection errors are logged with full stack traces.
- Invalid or missing credentials raise clear configuration errors.

---

## License

This project is released under the **MIT License**.  
You’re free to use, modify, and share it — attribution appreciated.

---

## Inspiration

Inspired by the “Musical Time Machine” project concept from the [100 Days of Python](https://www.udemy.com/course/100-days-of-code/) course, modernized and refactored for production-style readability.

---

## Author

**Tarmino**  
GitHub: [@tarmino-dev](https://github.com/tarmino-dev)
