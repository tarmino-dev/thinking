from turtle import Turtle, Screen, colormode, resetscreen, pensize
import random

bill = Turtle()
john = Turtle()
jack = Turtle()
burt = Turtle()
nick = Turtle()


def random_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return r, g, b


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
        jack.pencolor(random_color())
        for _ in range(number_of_edges):
            jack.forward(100)
            jack.right(360/number_of_edges)
    for i in range(3, 11):
        draw_polyhedron(i)


def burt_go():
    """Burt draws a Random Walk"""
    burt.pensize(10)
    burt.speed("fastest")
    colormode(255)
    for _ in range(200):
        burt.pencolor(random_color())
        burt.setheading(random.choice(DIRECTIONS))
        burt.forward(50)


def nick_go():
    """Nick imitates spirograph"""
    colormode(255)
    nick.speed("fastest")
    def draw_spirograph(size_of_gap):
        for _ in range(int(360 / size_of_gap)):
            nick.pencolor(random_color())
            nick.circle(100)
            nick.setheading(nick.heading() + size_of_gap) # Get the current heading and turn it by X degrees
    draw_spirograph(5)


TURTLES_FUNCTIONS = {"bill": bill_go, "john": john_go,
                     "jack": jack_go, "burt": burt_go, "nick": nick_go}
DIRECTIONS = [0, 90, 180, 270]


def run_turtle(turtle):
    TURTLES_FUNCTIONS[turtle]()  # call the corresponding function


while True:
    user_choice = input(
        "Choose your turtle (bill / john / jack / burt / nick) or type 'off' and close the window to exit: ")
    if user_choice == "off":
        print("Exiting... Please close the canvas window.")
        break
    if user_choice not in TURTLES_FUNCTIONS:
        print("Invalid input. Type bill / john / jack / burt / nick")
        continue
    resetscreen()
    run_turtle(user_choice)

screen = Screen()
screen.exitonclick()
