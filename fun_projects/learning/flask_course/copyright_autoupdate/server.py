from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)


@app.route('/')
def home():
    name = "Student"
    current_year = datetime.now().year
    return render_template("index.html", name=name, year=current_year)


if __name__ == "__main__":
    app.run(debug=True)
