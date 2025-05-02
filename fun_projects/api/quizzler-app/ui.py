import tkinter

THEME_COLOR = "#375362"


class QuizInterface:
    def __init__(self):
        self.window = tkinter.Tk()
        self.window.title("Quizzler")
        self.window.config(bg=THEME_COLOR, padx=20, pady=20)

        self.score_label = tkinter.Label(
            text="Score: 0", fg="white", bg=THEME_COLOR)
        self.score_label.grid(column=1, row=0)

        self.canvas = tkinter.Canvas(
            bg="white", width=300, height=250, highlightthickness=0)
        self.question_text = self.canvas.create_text(
            150, 125, text="QUESTION TEXT", font=("Arial", 20, "italic"), fill=THEME_COLOR)
        self.canvas.grid(column=0, row=1, columnspan=2, pady=50)

        true_button_image = tkinter.PhotoImage(file="./images/true.png")
        self.right_button = tkinter.Button(
            image=true_button_image, highlightthickness=0)
        self.right_button.grid(column=0, row=2)

        false_button_image = tkinter.PhotoImage(file="./images/false.png")
        self.wrong_button = tkinter.Button(
            image=false_button_image, highlightthickness=0)
        self.wrong_button.grid(column=1, row=2)

        self.window.mainloop()
