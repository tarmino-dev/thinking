import tkinter


def button_clicked():
    # Gets a string from Entry and assigns it as text of Label
    new_text = my_entry.get()
    my_label.config(text=new_text)


window = tkinter.Tk()
window.title("My second GUI Program")
window.minsize(width=500, height=300)
window.config(padx=20, pady=20)


# Label
my_label = tkinter.Label(text="I'm a label", font=(
    "Atial", 24, "bold"))  # Create a Label object
my_label.grid(row=0, column=0)


# Button
my_button = tkinter.Button(text="Click me", command=button_clicked)
my_button.grid(row=1, column=1)

new_button = tkinter.Button(text="Click me too", command=button_clicked)
new_button.grid(row=0, column=2)


# Entry
my_entry = tkinter.Entry(width=10)
print(my_entry.get())
my_entry.grid(row=2, column=3)


window.mainloop()
