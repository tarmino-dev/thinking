from turtle import Turtle, Screen, colormode, resetscreen, pensize
import random

bill = Turtle()
john = Turtle()
jack = Turtle()
burt = Turtle()
nick = Turtle()
gary = Turtle()


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
            # Get the current heading and turn it by X degrees
            nick.setheading(nick.heading() + size_of_gap)
    draw_spirograph(5)


def gary_go():
    """Gary paints a 'dot' painting"""
    colormode(255)
    gary.speed("fastest")
    gary.penup()
    gary.setposition(-300, -300)
    for _ in range(10):
        for _ in range(10):
            gary.dot(20, random.choice(DOT_COLORS))
            gary.forward(50)
        gary.setposition(-300, gary.position()[1] + 50)


TURTLES_FUNCTIONS = {"bill": bill_go, "john": john_go,
                     "jack": jack_go, "burt": burt_go, "nick": nick_go, "gary": gary_go}
DIRECTIONS = [0, 90, 180, 270]
DOT_COLORS = [(36, 95, 183), (236, 165, 79), (244, 223, 87), (215, 69, 105), (98, 197, 234), (250, 51, 22), (203, 70, 21), (240, 106, 143), (185, 47, 90), (143, 233, 216), (252, 136, 166), (165, 175, 233),
              (66, 45, 13), (72, 205, 170), (83, 187, 100), (20, 156, 51), (24, 36, 86), (252, 220, 0), (164, 28, 8), (105, 39, 44), (250, 152, 2), (22, 151, 229), (108, 213, 249), (254, 12, 3), (38, 48, 98), (98, 96, 186)]


def run_turtle(turtle):
    TURTLES_FUNCTIONS[turtle]()  # call the corresponding function


while True:
    user_choice = input(
        "Choose your turtle (bill / john / jack / burt / nick / gary)\nor type 'off' and close the window to exit: ")
    if user_choice == "off":
        print("Exiting... Please close the canvas window.")
        break
    if user_choice not in TURTLES_FUNCTIONS:
        print("Invalid input. Type bill / john / jack / burt / nick / gary")
        continue
    resetscreen()
    run_turtle(user_choice)

screen = Screen()
screen.exitonclick()
