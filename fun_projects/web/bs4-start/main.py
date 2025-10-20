from bs4 import BeautifulSoup
import requests

with open("fun_projects/web/bs4-start/website.html", "r") as website_file:
    contents = website_file.read()

soup = BeautifulSoup(contents, "html.parser")
print(soup)
print(soup.prettify())  # pretty formatted
print(soup.a)  # Anchor tag (1st occasion)
# h1 tag (1st occasion) if it has "name" id attribute
print(soup.find(name="h1", id="name"))
# Important! Use class_ (with underscore) to search for class attribute
print(soup.find_all(name="a"))  # Anchor tag (all occasions)
print(soup.title)  # <title>Angela's Personal Site</title>
print(soup.title.name)  # title
print(soup.title.string)  # Angela's Personal Site
print(soup.title.get_text())  # Angela's Personal Site

all_anchor_tags = soup.find_all(name="a")
for tag in all_anchor_tags:
    print(tag.getText())  # Get link text
    print(tag.get("href"))  # Get link URL

response = requests.get("https://appbrewery.github.io/news.ycombinator.com/")
yc_web_page = response.text

page_soup = BeautifulSoup(yc_web_page, "html.parser")

# Finding 1st element on the page
article_a_tag = page_soup.find(name="a", class_="storylink")
article_text = article_a_tag.get_text()
article_link = article_a_tag.get("href")

article_span_tag = page_soup.find(name="span", class_="score")
article_upvote = article_span_tag.get_text()

print(article_text)
print(article_link)
print(article_upvote)

# Finding all the elements on the page
articles = page_soup.find_all(name="a", class_="storylink")
article_texts = []
article_links = []
for article in articles:
    text = article.get_text()
    article_texts.append(text)
    link = article.get("href")
    article_links.append(link)

article_upvotes = [int(score.getText().split()[0])
                   for score in page_soup.find_all(name="span", class_="score")]

print(article_texts)
print(article_links)
print(article_upvotes)

largest_number = max(article_upvotes)
largest_index = article_upvotes.index(largest_number)

print(article_texts[largest_index])
print(article_links[largest_index])
print(article_upvotes[largest_index])
