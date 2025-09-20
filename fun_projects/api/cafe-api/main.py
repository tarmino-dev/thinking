from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import random


app = Flask(__name__)

# CREATE DB
class Base(DeclarativeBase):
    pass

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        #Method 1. 
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            #Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary
        
        #Method 2. Altenatively use Dictionary Comprehension to do the same thing.
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random") # GET is allowed by default on all routes
def get_random_cafe():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    random_cafe = random.choice(all_cafes) # Now random_cafe is an SQLAlchemy Object
    #Simply convert the random_cafe data record to a dictionary of key-value pairs. 
    return jsonify(cafe=random_cafe.to_dict())

@app.route("/all")
def get_all_cafes():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.name))
    all_cafes = result.scalars().all()
    all_cafes_list_of_dicts = [cafe.to_dict() for cafe in all_cafes]
    return jsonify(cafes=all_cafes_list_of_dicts)

@app.route("/search")
def get_cafe_at_location():
    query_location = request.args.get("loc") # get a parameter passed in the URL with a ? e.g. /search?loc=Peckham
    result = db.session.execute(db.select(Cafe).where(Cafe.location == query_location))
    all_cafes = result.scalars().all()
    if all_cafes: # check if there are any search results
        all_cafes_list_of_dicts = [cafe.to_dict() for cafe in all_cafes]
        return jsonify(cafes=all_cafes_list_of_dicts)
    return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404

# HTTP POST - Create Record


# HTTP PUT/PATCH - Update Record


# HTTP DELETE - Delete Record



if __name__ == '__main__':
    app.run(debug=True)
