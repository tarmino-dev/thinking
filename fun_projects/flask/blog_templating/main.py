from flask import Flask, render_template
import requests

blog_url = "https://api.npoint.io/249c50e23dd4fd8a4fc8"
response = requests.get(url=blog_url)
all_posts = response.json()

app = Flask(__name__)


@app.route("/")
def get_blog():
    return render_template("index.html", posts=all_posts)


@app.route("/post/<int:index>")
def show_post(index):
    return render_template("post.html", post=all_posts[index - 1])


if __name__ == "__main__":
    app.run(debug=True)
