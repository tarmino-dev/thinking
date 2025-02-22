from turtle import Turtle, Screen, colormode, resetscreen
import random

bill = Turtle()
john = Turtle()
jack = Turtle()


def bill_go():
    """Bill draws a square."""
    for i in range(4):
        bill.forward(100)
        bill.right(90)


def john_go():
    """John draws a dashed line"""
    for i in range(10):
        john.pendown()
        john.forward(25)
        john.penup()
        john.forward(25)


def jack_go():
    """Jack draws 8 polyhedrons with the number of edges from 3 to 10"""
    colormode(255)

    def draw_polyhedron(number_of_edges):
        color = random.randint(0, 255), random.randint(
            0, 255), random.randint(0, 255)
        jack.pencolor(color)
        for _ in range(number_of_edges):
            jack.forward(100)
            jack.right(360/number_of_edges)
    for i in range(3, 11):
        draw_polyhedron(i)


def burt_go():
    """Burt draws a Random Walk"""


def nick_go():
    """Nick """
    pass


TURTLES_FUNCTIONS = {"bill": bill_go, "john": john_go,
                     "jack": jack_go, "burt": burt_go, "nick": nick_go}


def run_turtle(turtle):
    TURTLES_FUNCTIONS[turtle]()  # call the corresponding function


while True:
    user_choice = input(
        "Choose your turtle (bill / john / jack / burt / nick) or type 'off' and close the window to exit: ")
    if user_choice == "off":
        break
    resetscreen()
    run_turtle(user_choice)

screen = Screen()
screen.exitonclick()
