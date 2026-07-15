import tkinter


def miles_to_km():
    miles_number = float(miles_number_entry.get())
    km_number = round(miles_number * 1.609, 3)
    result_label.config(text=f"{km_number}")


window = tkinter.Tk()
window.title("Mile to Km Converter")
window.minsize(width=250, height=100)
window.config(padx=20, pady=20)

# Entry: miles
miles_number_entry = tkinter.Entry(width=10)
miles_number_entry.insert(tkinter.END, string="0")
miles_number_entry.grid(column=1, row=0)

# Label: "Miles"
miles_label = tkinter.Label(text="Miles", font=("Arial", 18, "normal"))
miles_label.grid(column=2, row=0)

# Label: "is equal to"
is_equal_to_label = tkinter.Label(
    text="is equal to", font=("Arial", 18, "normal"))
is_equal_to_label.grid(column=0, row=1)

# Label: result
result_label = tkinter.Label(text="0", font=("Arial", 18, "normal"))
result_label.grid(column=1, row=1)

# Label: "Km"
km_label = tkinter.Label(text="Km", font=("Arial", 18, "normal"))
km_label.grid(column=2, row=1)

# Button: "Calculate"
calculate_button = tkinter.Button(text="Calculate", command=miles_to_km)
calculate_button.grid(column=1, row=2)


window.mainloop()
