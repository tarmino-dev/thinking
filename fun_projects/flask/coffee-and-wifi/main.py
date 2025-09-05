from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired, URL
import csv

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)


class CafeForm(FlaskForm):
    cafe = StringField(label='Cafe name', validators=[DataRequired()])
    location = StringField(label='Cafe Location on Google Maps (URL)', validators=[DataRequired(), URL()])
    opening = StringField(label='Opening Time e.g. 8AM', validators=[DataRequired()])
    closing = StringField(label='Closing Time e.g. 5:30PM', validators=[DataRequired()])
    rating = SelectField(label='Coffee Rating', choices=['☕', '☕☕', '☕☕☕', '☕☕☕☕', '☕☕☕☕☕'], default='☕', validators=[DataRequired()])
    wifi = SelectField(label='Wifi Strength Rating', choices=['✘', '💪', '💪💪', '💪💪💪', '💪💪💪💪', '💪💪💪💪💪'], default='✖️', validators=[DataRequired()])
    power = SelectField(label='Power Socket Availability', choices=['✘', '🔌', '🔌🔌', '🔌🔌🔌', '🔌🔌🔌🔌', '🔌🔌🔌🔌🔌'], default='✖️', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route("/")
def home():
    return render_template("index.html")


@app.route('/add', methods=["GET", "POST"])
def add_cafe():
    form = CafeForm()
    if form.validate_on_submit():
        data = request.form.to_dict()
        print(f"DATA: {data} !!!!!!!!!!!!")
        fieldnames = ["cafe","location","opening","closing","rating","wifi","power"]
        filtered_data = {k: data.get(k, "") for k in fieldnames} # Filter to remove "submit" and "csrf_token" and keep only required fields
        with open('cafe-data.csv', newline='', encoding='utf-8', mode='a') as csv_file:
            writer = csv.DictWriter(f=csv_file, fieldnames=fieldnames)
            writer.writerow(filtered_data)
        return redirect(url_for('cafes'))
    return render_template('add.html', form=form)


@app.route('/cafes')
def cafes():
    with open('cafe-data.csv', newline='', encoding='utf-8') as csv_file:
        csv_data = csv.reader(csv_file, delimiter=',')
        list_of_rows = []
        for row in csv_data:
            list_of_rows.append(row)
    return render_template('cafes.html', cafes=list_of_rows)


if __name__ == '__main__':
    app.run(debug=True)
