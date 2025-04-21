import tkinter
import pandas
import random
# ---------------------------- CONSTANTS ------------------------------- #
BACKGROUND_COLOR = "#B1DDC6"
# ---------------------------- CREATE NEW FLASH CARD ------------------------------- #
data = pandas.read_csv("./data/french_words.csv")
# ‘records’ : list like [{column -> value}, … , {column -> value}]
words_to_learn = data.to_dict(orient="records")
current_card = {}


def next_card():
    global current_card, flip_timer
    window.after_cancel(flip_timer)
    current_card = random.choice(words_to_learn)
    canvas.itemconfig(card_title, fill="black", text="French")
    canvas.itemconfig(card_word, fill="black", text=current_card["French"])
    canvas.itemconfig(card_background, image=card_front_img)
    flip_timer = window.after(3000, flip_card)
# ---------------------------- FLIP CARD ------------------------------- #


def flip_card():
    canvas.itemconfig(card_title, fill="white", text="English")
    canvas.itemconfig(card_word, fill="white", text=current_card["English"])
    canvas.itemconfig(card_background, image=card_back_img)


# ---------------------------- UI SETUP ------------------------------- #
window = tkinter.Tk()
window.title("Flashy")
window.config(padx=50, pady=50, bg=BACKGROUND_COLOR)

flip_timer = window.after(3000, flip_card)

canvas = tkinter.Canvas(width=800, height=526,
                        bg=BACKGROUND_COLOR, highlightthickness=0)
card_front_img = tkinter.PhotoImage(file="./images/card_front.png")
card_back_img = tkinter.PhotoImage(file="./images/card_back.png")
card_background = canvas.create_image(400, 263, image=card_front_img)
card_title = canvas.create_text(
    400, 150, text="", fill="", font=("Ariel", 40, "italic"))
card_word = canvas.create_text(
    400, 263, text="", fill="", font=("Ariel", 60, "bold"))
canvas.grid(column=0, row=0, columnspan=2)

cross_image = tkinter.PhotoImage(file="./images/wrong.png")
unknown_button = tkinter.Button(
    image=cross_image, highlightthickness=0, command=next_card)
unknown_button.grid(column=0, row=1)

check_image = tkinter.PhotoImage(file="./images/right.png")
known_button = tkinter.Button(
    image=check_image, highlightthickness=0, command=next_card)
known_button.grid(column=1, row=1)

next_card()  # Fill an initial card with data

window.mainloop()
