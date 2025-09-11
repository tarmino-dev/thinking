from flask import Flask, render_template
import requests

blog_url = "https://api.npoint.io/fbce267e92535cc0ad1b"
response = requests.get(url=blog_url)
all_posts = response.json()

app = Flask(__name__)


@app.route('/')
def get_all_posts():
    return render_template("index.html", posts=all_posts)

@app.route('/about')
def about_page():
    return render_template("about.html")

@app.route('/contact')
def contact_page():
    return render_template("contact.html")

@app.route("/post/<int:index>")
def show_post(index):
    return render_template("post.html", post=all_posts[index - 1])

if __name__ == "__main__":
    app.run(debug=True)
