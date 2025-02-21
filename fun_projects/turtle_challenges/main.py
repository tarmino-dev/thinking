from turtle import Turtle, Screen

bill = Turtle()
for i in range(4):
    print(bill.pos())
    bill.fd(100)
    bill.rt(90)
john = Turtle()
john.up()
john.setposition(-300, -200)
for i in range(10):
    john.down()
    john.fd(25)
    john.up()
    john.fd(25)
screen = Screen()
screen.exitonclick()
