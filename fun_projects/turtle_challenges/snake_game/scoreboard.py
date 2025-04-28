from turtle import Turtle

ALIGNMENT = "left"
FONT = ("Arial", 18, "normal")


class Scoreboard(Turtle):

    DATA_FILE = "data.txt"

    def __init__(self):
        super().__init__()
        self.score = 0
        self.highscore = self.read_highscore()
        self.color("white")
        self.hideturtle()
        self.penup()
        self.goto(-40, 275)
        self.update_scoreboard()

    def update_scoreboard(self):
        self.clear()
        self.write(f"Score: {self.score} High score: {self.highscore}", move=False, align=ALIGNMENT,
                   font=FONT)

    def reset(self):
        if self.score > self.highscore:
            self.highscore = self.score
            self.save_highscore()
        self.score = 0
        self.update_scoreboard()

    def increase_score(self):
        self.score += 1
        self.update_scoreboard()

    def read_highscore(self):
        with open(self.DATA_FILE, mode="r") as data:
            highscore = int(data.read())
            return highscore

    def save_highscore(self):
        with open(self.DATA_FILE, mode="w") as data:
            data.write(str(self.highscore))    
