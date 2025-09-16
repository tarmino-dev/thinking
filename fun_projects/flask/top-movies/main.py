from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
from config import TMDB_API_SEARCH_MOVIE_URL, TMDB_API_MOVIE_DETAILS_URL, TMDB_API_HEADERS


class FindMovieForm(FlaskForm):
    title = StringField(label="Movie Title", validators=[DataRequired()])
    submit = SubmitField(label="Add Movie")

class EditForm(FlaskForm):
    rating = StringField(label="Your Rating Out of 10 e.g. 7.5", validators=[DataRequired()])
    review = StringField(label="Your Review", validators=[DataRequired()])
    submit = SubmitField(label="Done")

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

# CREATE DB
class Base(DeclarativeBase):
    pass

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///top-movies.db"

db = SQLAlchemy(model_class=Base)
db.init_app(app)

# CREATE TABLE
class Movie(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=True)
    ranking: Mapped[int] = mapped_column(Integer, nullable=True)
    review: Mapped[str] = mapped_column(String, nullable=True)
    img_url: Mapped[str] = mapped_column(String, nullable=False)

    def __repr__(self):
        return f'<Movie {self.title}>'

with app.app_context():
    db.create_all()



@app.route("/")
def home():
    result = db.session.execute(db.select(Movie))
    all_movies = result.scalars().all()
    return render_template("index.html", movies=all_movies)

@app.route("/add", methods=["GET", "POST"])
def add():
    form = FindMovieForm()
    if form.validate_on_submit():
        movie_title = form.title.data
        # TODO use the requests library to make a request and search The Movie Database API for all the movies that match that title
        response = requests.get(url=TMDB_API_SEARCH_MOVIE_URL, params={"query": movie_title}, headers=TMDB_API_HEADERS)
        response.raise_for_status()
        data = response.json()
        return render_template("select.html", movie_candidates=data)
    return render_template("add.html", form=form)

@app.route("/select/<int:id>")
def select(id):
    response = requests.get(url=f"{TMDB_API_MOVIE_DETAILS_URL}/{id}", headers=TMDB_API_HEADERS)
    response.raise_for_status()
    data = response.json()
    new_movie = Movie(
    title=data["title"],
    year=data["release_date"].split("-")[0],
    description=data["overview"],
    img_url=f"https://image.tmdb.org/t/p/w500{data['poster_path']}"
    )
    db.session.add(new_movie)
    db.session.commit()
    movie_id = new_movie.id
    return redirect(url_for("edit", id=movie_id))

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    movie_to_edit = db.session.execute(db.select(Movie).where(Movie.id == id)).scalar()
    edit_form = EditForm()
    if edit_form.validate_on_submit():
        movie_to_edit.rating = float(edit_form.rating.data)
        movie_to_edit.review = edit_form.review.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", form=edit_form, movie=movie_to_edit)

@app.route("/delete/<int:id>")
def delete(id):
    movie_to_delete = db.session.execute(db.select(Movie).where(Movie.id == id)).scalar()
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for("home"))

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
