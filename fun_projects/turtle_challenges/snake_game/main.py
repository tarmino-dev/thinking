from turtle import Screen
import time
from snake import Snake
from food import Food
from scoreboard import Scoreboard

screen = Screen()
screen.setup(width=600, height=600)
screen.bgcolor("black")
screen.title("My Snake Game")
screen.tracer(0)

snake = Snake()
food = Food()
scoreboard = Scoreboard()

screen.listen()
screen.onkey(snake.up, "Up")
screen.onkey(snake.down, "Down")
screen.onkey(snake.left, "Left")
screen.onkey(snake.right, "Right")

scoreboard.hideturtle()
scoreboard.penup()
scoreboard.goto(-40, 275)
scoreboard.write(f"Score: {scoreboard.score}", move=False, align="left",
                 font=("Arial", 18, "normal"))


game_is_on = True
while game_is_on:
    screen.update()
    time.sleep(0.5)
    snake.move()

    # Detect collision with food.
    if snake.head.distance(food) < 15:
        food.refresh()
        scoreboard.score += 1
        scoreboard.clear()
        scoreboard.write(f"Score: {scoreboard.score}", move=False, align="left",
                 font=("Arial", 18, "normal"))

screen.exitonclick()
