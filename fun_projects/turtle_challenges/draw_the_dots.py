from turtle import Turtle, colormode, Screen
from extracting import color_list
import random

jimmy = Turtle()


def jimmy_go():
    """Jimmy paints a 'dot' painting using extracted colors"""
    colormode(255)
    jimmy.speed("fastest")
    jimmy.penup()
    jimmy.hideturtle()
    jimmy.setposition(-300, -300)
    for _ in range(10):
        for _ in range(10):
            jimmy.dot(20, random.choice(color_list))
            jimmy.forward(50)
        jimmy.setposition(-300, jimmy.position()[1] + 50)


jimmy_go()

screen = Screen()
screen.exitonclick()
