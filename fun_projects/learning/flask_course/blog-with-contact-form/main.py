from flask import Flask, render_template, request
import requests
import smtplib
from config import *

posts = requests.get("https://api.npoint.io/fbce267e92535cc0ad1b").json()

app = Flask(__name__)


@app.route('/')
def get_all_posts():
    return render_template("index.html", all_posts=posts)


@app.route("/about")
def about():
    return render_template("about.html")


@app.get("/contact")
def contact():
    return render_template("contact.html")


@app.post("/contact")
def receive_data():
    data = request.form
    email_msg = f"Subject: New message in the Blog Conctact Form\n\nName: {data['name']}\nEmail: {data['email']}\nPhone: {data['phone']}\nMessage: {data['message']}"
    send_email(email_msg)
    return render_template("contact.html", msg_sent=True)


def send_email(message):
    with smtplib.SMTP(GMAIL_SMTP_ADDRESS) as connection:
        connection.starttls()
        connection.login(user=GMAIL_EMAIL, password=GMAIL_APP_PASSWORD)
        connection.sendmail(from_addr=GMAIL_EMAIL,
                            to_addrs=GMAIL_EMAIL, msg=message)


@app.route("/post/<int:index>")
def show_post(index):
    requested_post = None
    for blog_post in posts:
        if blog_post["id"] == index:
            requested_post = blog_post
    return render_template("post.html", post=requested_post)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
