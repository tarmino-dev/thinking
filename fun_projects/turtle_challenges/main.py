from turtle import Turtle, Screen

bill = Turtle()
bill.fd(100)
for i in range(3):
    bill.rt(90)
    bill.fd(100)
screen = Screen()
screen.exitonclick()
