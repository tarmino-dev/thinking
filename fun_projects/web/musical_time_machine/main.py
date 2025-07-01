import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime

from config import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI

HEADER = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"}


def main():
    date, year, url = songs_date_input()
    song_names = get_song_names(url=url)
    spotify_object = create_spotify_object()
    spotify_user_id = get_spotify_user_id(sp=spotify_object)
    song_uris = get_song_uris(song_names=song_names,
                              year=year,
                              sp=spotify_object)
    playlist = create_playlist(
        sp=spotify_object,
        spotify_user_id=spotify_user_id,
        date=date)
    add_tracks(sp=spotify_object,
               spotify_user_id=spotify_user_id,
               playlist=playlist, song_uris=song_uris)


def songs_date_input():
    date = input(
        "Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")
    year = date.split("-")[0]
    url = f"https://www.billboard.com/charts/hot-100/{date}"
    return date, year, url


def get_song_names(url):
    response = requests.get(url=url, headers=HEADER)
    soup = BeautifulSoup(response.text, "html.parser")
    song_names_spans = soup.select("li ul li h3")
    song_names = [song.getText(strip=True) for song in song_names_spans]
    return song_names


def create_spotify_object():
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI))
    return sp


def get_spotify_user_id(sp):
    spotify_user_id = sp.current_user()["id"]
    return spotify_user_id


def get_song_uris(song_names, year, sp):
    song_uris = []
    for song in song_names:
        search_str = f"track: {song} year: {year}"
        result = sp.search(q=search_str, type="track")
        try:
            uri = result["tracks"]["items"][0]["uri"]
            song_uris.append(uri)
        except IndexError:
            print(f"{song} is not found in Spotify. Skipped.")
    return song_uris


def create_playlist(sp, spotify_user_id, date):
    date_time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return sp.user_playlist_create(
        user=spotify_user_id,
        name=f"{date} Billboard 100",
        public=False,
        description=f"created with Python script {date_time_now}")


def add_tracks(sp, spotify_user_id, playlist, song_uris):
    sp.user_playlist_add_tracks(
        user=spotify_user_id,
        playlist_id=playlist["id"],
        tracks=song_uris)


if __name__ == "__main__":
    main()
