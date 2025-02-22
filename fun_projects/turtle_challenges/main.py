from turtle import Turtle, Screen, colormode, resetscreen, pensize
import random

bill = Turtle()
john = Turtle()
jack = Turtle()
burt = Turtle()


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
    burt.pensize(10)
    colormode(255)
    for _ in range(50):
        color = random.randint(0, 255), random.randint(
            0, 255), random.randint(0, 255)
        burt.pencolor(color)
        MOVES[random.choice(list(MOVES))](burt)


def nick_go():
    """Nick """
    pass


def move_right(turtle):
    turtle.right(90)
    turtle.forward(50)


def move_left(turtle):
    turtle.left(90)
    turtle.forward(50)


def move_forward(turtle):
    turtle.forward(50)


def move_back(turtle):
    turtle.back(50)


TURTLES_FUNCTIONS = {"bill": bill_go, "john": john_go,
                     "jack": jack_go, "burt": burt_go, "nick": nick_go}
MOVES = {"move_right": move_right, "move_left": move_left,
         "move_forward": move_forward, "move_back": move_back}


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
