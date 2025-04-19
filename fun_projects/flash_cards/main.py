import tkinter
# ---------------------------- CONSTANTS ------------------------------- #
BACKGROUND_COLOR = "#B1DDC6"
# ---------------------------- UI SETUP ------------------------------- #
window = tkinter.Tk()
window.title("Flashy")
window.config(padx=50, pady=50, bg=BACKGROUND_COLOR)

canvas = tkinter.Canvas(width=800, height=526, bg=BACKGROUND_COLOR, highlightthickness=0)
card_front_img = tkinter.PhotoImage(file="./images/card_front.png")
canvas.create_image(400, 263, image=card_front_img)
canvas.create_text(400, 150, text="Title", fill="black", font=("Ariel", 40, "italic"))
canvas.create_text(400, 263, text="word", fill="black", font=("Ariel", 60, "bold"))
canvas.grid(column=0, row=0, columnspan=2)

cross_image = tkinter.PhotoImage(file="./images/wrong.png")
unknown_button = tkinter.Button(image=cross_image, highlightthickness=0)
unknown_button.grid(column=0, row=1)

check_image = tkinter.PhotoImage(file="./images/right.png")
known_button = tkinter.Button(image=check_image, highlightthickness=0)
known_button.grid(column=1, row=1)



window.mainloop()