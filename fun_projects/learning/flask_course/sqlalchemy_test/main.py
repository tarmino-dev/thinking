from flask import Flask
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

# Create record
with app.app_context():
    new_book = Book(title="Harry Potter",
                    author="J. K. Rowling", rating=9.3)  # the primary key field (id=1) is optional. If it is not passed, it will be auto-generated
    db.session.add(new_book)
    db.session.commit()

if __name__ == "__main__":
    # ! Add use_reloader=False to prevent duplicate rows in the database and errors due to the inability to do so
    app.run(debug=True, use_reloader=False)
