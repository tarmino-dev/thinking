import tkinter


def button_clicked():
    # Gets a string from Entry and assigns it as text of Label
    print("I got clicked")
    new_text = my_entry.get()
    my_label.config(text=new_text)


window = tkinter.Tk()
window.title("My first GUI Program")
window.minsize(width=500, height=300)


# Label
my_label = tkinter.Label(text="I'm a label", font=(
    "Atial", 24, "bold"))  # Create a Label object

# Updating an object property by accessing the property as a dictionary element
my_label["text"] = "New text"

# Updating an object property using config() method
my_label.config(text="New new text")

# Display the Label
my_label.pack()


# Button
my_button = tkinter.Button(text="Click me", command=button_clicked)
my_button.pack()


# Entry
my_entry = tkinter.Entry(width=10)
print(my_entry.get())
my_entry.pack()


window.mainloop()
