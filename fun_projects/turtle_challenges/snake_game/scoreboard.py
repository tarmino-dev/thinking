from turtle import Turtle

ALIGNMENT = "left"
FONT = ("Arial", 18, "normal")


class Scoreboard(Turtle):
    def __init__(self):
        super().__init__()
        self.score = 0
        self.color("white")
        self.hideturtle()
        self.penup()
        self.goto(-40, 275)
        self.update_scoreboard()

    def update_scoreboard(self):
        self.write(f"Score: {self.score}", move=False, align=ALIGNMENT,
                   font=FONT)
        
    def game_over(self):
        self.goto(-50, 0)
        self.write("GAME OVER", move=False, align=ALIGNMENT,
                   font=FONT)

    def increase_score(self):
        self.score += 1
        self.clear()
        self.update_scoreboard()
