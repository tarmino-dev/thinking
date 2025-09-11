from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float

# Create the app
app = Flask(__name__)

# As of flask-sqlalchemy version 3.1, you need to pass a subclass of DeclarativeBase to the constructor of the database.


class Base(DeclarativeBase):
    pass


# Configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///new-books-collection.db"

# Create the extension
db = SQLAlchemy(model_class=Base)

# Initialize the app with the extension
db.init_app(app)

# Define model


class Book(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(
        String(250), nullable=False, unique=True)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=True)

    # Optional: this will allow each book object to be identified by its title when printed.
    def __repr__(self):
        return f'<Book {self.title}>'


# Create the tables
with app.app_context():
    db.create_all()


@app.route('/')
def home():
    result = db.session.execute(db.select(Book).order_by(Book.title))
    all_books = result.scalars().all()
    return render_template("index.html", books=all_books)


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        new_book = Book(title=request.form["title"],
                        author=request.form["author"], rating=request.form["rating"])  # the primary key field (id=1) is optional. If it is not passed, it will be auto-generated
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add.html")

@app.route("/edit_rating/<int:id>", methods=["GET", "POST"])
def edit_rating(id):
    book_to_edit = db.session.execute(db.select(Book).where(Book.id == id)).scalar()
    if request.method == "POST":
        new_rating = request.form["new_rating"]
        book_to_edit.rating = new_rating
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit_rating.html", book=book_to_edit)

@app.route("/delete/<int:id>")
def delete(id):
    book_to_delete = db.session.execute(db.select(Book).where(Book.id == id)).scalar()
    db.session.delete(book_to_delete)
    db.session.commit()
    return redirect(url_for("home"))

if __name__ == "__main__":
    # ! Add use_reloader=False to prevent duplicate rows in the database and errors due to the inability to do so
    app.run(debug=True, use_reloader=False)

