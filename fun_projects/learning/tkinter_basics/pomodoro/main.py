import tkinter
# ---------------------------- CONSTANTS ------------------------------- #
PINK = "#e2979c"
RED = "#e7305b"
GREEN = "#9bdeac"
YELLOW = "#f7f5dd"
FONT_NAME = "Courier"
WORK_MIN = 25
SHORT_BREAK_MIN = 5
LONG_BREAK_MIN = 20
reps = 0
timer = None
# ---------------------------- TIMER RESET ------------------------------- #


def reset_timer():
    global reps
    window.after_cancel(timer)
    # Configure the text placed on the canvas
    canvas.itemconfig(timer_text, text="00:00")
    title_label.config(text="Timer")
    checkmark_label.config(text="")
    reps = 0
# ---------------------------- TIMER MECHANISM ------------------------------- #


def start_timer():
    work_sec = WORK_MIN * 60
    short_break_sec = SHORT_BREAK_MIN * 60
    long_break_sec = LONG_BREAK_MIN * 60
    global reps
    reps += 1
    if reps % 8 == 0:
        count_down(long_break_sec)
        title_label.config(text="Break", fg=RED)
    elif reps % 2 == 0:
        count_down(short_break_sec)
        title_label.config(text="Break", fg=PINK)
    else:
        count_down(work_sec)
        title_label.config(text="Work", fg=GREEN)
# ---------------------------- COUNTDOWN MECHANISM ------------------------------- #


def count_down(count):
    global timer
    min_sec = list(divmod(count, 60))
    if min_sec[1] < 10:
        min_sec[1] = f"0{min_sec[1]}"
    # Configure timer text placed on the canvas using new counter value
    canvas.itemconfig(timer_text, text=f"{min_sec[0]}:{min_sec[1]}")
    if count > 0:
        # Update the counter value after 1 second by calling the function recursively with reduced argument
        timer = window.after(1000, count_down, count - 1)
    else:
        start_timer()
        if reps % 2 == 0:
            checkmark_label.config(text=int(reps / 2) * "✔")


# ---------------------------- UI SETUP ------------------------------- #
window = tkinter.Tk()
window.title("Pomodoro")
window.config(padx=100, pady=50, bg=YELLOW)

# Create a canvas (highlightthickness - border)
canvas = tkinter.Canvas(width=200, height=224, bg=YELLOW, highlightthickness=0)
# Create an image object from the file
tomato_img = tkinter.PhotoImage(file="tomato.png")
# The center of the image (adjust if cropped), The image obgect
canvas.create_image(100, 112, image=tomato_img)
# Place the text on the canvas
timer_text = canvas.create_text(100, 130, text="00:00", fill="white",
                                font=(FONT_NAME, 35, "bold"))
# Put the canvas on the window
canvas.grid(column=1, row=1)

title_label = tkinter.Label(text="Timer", bg=YELLOW,
                            fg=GREEN, font=(FONT_NAME, 50))
title_label.grid(column=1, row=0)

checkmark_label = tkinter.Label(bg=YELLOW, fg=GREEN)
checkmark_label.grid(column=1, row=3)

start_button = tkinter.Button(
    text="Start", highlightbackground=YELLOW, command=start_timer)
start_button.grid(column=0, row=2)

reset_button = tkinter.Button(
    text="Reset", highlightbackground=YELLOW, command=reset_timer)
reset_button.grid(column=2, row=2)

window.mainloop()
