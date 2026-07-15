import turtle
import pandas as pd
from marker import Marker

screen = turtle.Screen()
screen.title("U.S. States Game")
image = "./blank_states_img.gif"
screen.addshape(image)  # Add the image as a new shape
# Set the image as a shape of the turtle to insert it into the screen
turtle.shape(image)

data = pd.read_csv("./50_states.csv")

marker = Marker()

missing_states = data.copy(deep=True)
guessed_states = []
while len(guessed_states) < 50:
    answer_state = screen.textinput(
        title=f"{len(guessed_states)}/50 States Correct", prompt="What's another state's name?")
    answer_state = answer_state.title()
    if answer_state == "Exit":
        break
    is_state = answer_state in data["state"].values
    is_guessed = answer_state in guessed_states
    if is_state and not is_guessed:
        guessed_states.append(answer_state)
        state_data = data[data["state"] == answer_state]
        # state_data["x"].iloc[0] is also possible
        x_cor = state_data["x"].item()
        # state_data["y"].iloc[0] is also possible
        y_cor = state_data["y"].item()
        marker.mark(x_cor, y_cor, answer_state)
        state_index = data.index[data['state'] == answer_state][0]
        data = data.drop(index=state_index)
        data.to_csv("./states_to_learn.csv")
