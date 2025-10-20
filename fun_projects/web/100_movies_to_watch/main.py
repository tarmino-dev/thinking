import requests
from bs4 import BeautifulSoup

URL = "https://web.archive.org/web/20200518073855/https://www.empireonline.com/movies/features/best-movies-2/"

response = requests.get(URL)
website_html = response.text
soup = BeautifulSoup(website_html, "html.parser")
all_movies = soup.find_all(name="h3", class_="title")
movie_titles = []
for movie in all_movies:
    title = movie.get_text()
    movie_titles.insert(0, title)
with open("fun_projects/web/100_movies_to_watch/movies.txt", mode="w") as movies_file:
    for movie_title in movie_titles:
        movies_file.write(f"{movie_title}\n")
