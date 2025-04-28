from turtle import Turtle, Screen
import random

is_race_on = False
screen = Screen()
screen.setup(width=500, height=400)
user_bet = screen.textinput(
    title="Make your bet", prompt="Which turtle will win the race? Enter a color: ")
colors = ["red", "orange", "yellow", "green", "blue", "purple"]
all_turtles = {}

for i, color in enumerate(colors):
    all_turtles[color] = Turtle(shape="turtle")
    all_turtles[color].penup()
    all_turtles[color].color(color)
    all_turtles[color].goto(-240, -70 + i * 30)

if user_bet:
    is_race_on = True

while is_race_on:
    for turtle_name, turtle_obj in all_turtles.items():
        rand_distance = random.randint(0, 10)
        turtle_obj.forward(rand_distance)
        if turtle_obj.xcor() > 240:
            winning_color = turtle_name
            if winning_color == user_bet:
                print(f"You've won! The {winning_color} turtle is the winner!")
            else:
                print(
                    f"You've lost! The {winning_color} turtle is the winner!")
            is_race_on = False
            break

screen.exitonclick()
