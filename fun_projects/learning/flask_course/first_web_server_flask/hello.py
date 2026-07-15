from flask import Flask


app = Flask(__name__)


def make_bold(func):
    def wrapper():
        return f"<b>{func()}</b>"
    return wrapper


def make_emphasized(func):
    def wrapper():
        return f"<em>{func()}</em>"
    return wrapper


def make_inserted(func):
    def wrapper():
        return f"<ins>{func()}</ins>"
    return wrapper


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/bye")
@make_bold
@make_emphasized
@make_inserted
def bye():
    return "<p>Bye!</p>"


@app.route("/username/<path:name>")
def greet(name):
    return f"Hey, {name}!"


@app.route("/add/<int:a>/<int:b>")
def addition(a, b):
    return f"{a + b}"


if __name__ == "__main__":
    app.run(debug=True)
