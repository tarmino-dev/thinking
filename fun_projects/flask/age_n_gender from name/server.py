from flask import Flask, render_template
import requests

app = Flask(__name__)


@app.route("/guess/<username>")
def guess(username):
    response_agify = requests.get(
        url="https://api.agify.io", params={"name": username})
    response_agify.raise_for_status()
    response_agify_json = response_agify.json()
    age = response_agify_json["age"]

    response_genderize = requests.get(
        url="https://api.genderize.io", params={"name": username})
    response_genderize.raise_for_status()
    response_genderize_json = response_genderize.json()
    gender = response_genderize_json["gender"]

    return render_template("guess.html", name=username, age=age, gender=gender)


if __name__ == "__main__":
    app.run(debug=True)
