from turtle import Turtle

FONT = ("Courier", 14, "normal")

class Marker(Turtle):
    def __init__(self):
        super().__init__()
        self.hideturtle()
        self.penup()
    
    def mark(self, x_cor, y_cor, state_name):
        self.goto(x_cor, y_cor)
        self.write(state_name, align="left", font=FONT)