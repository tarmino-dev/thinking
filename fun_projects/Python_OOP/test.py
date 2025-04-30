class Car:
    def __init__(self, color, model, year):
        self._color = color
        self.__model = model
        self.__year__ = year

    def get_color(self):
        return self._color

c = Car("red", "Toyota", 2020)

# print(c._color) # OK - 'red'
# print(c.__model) # AttributeError: 'Car' object has no attribute '__model'
# print(c.__year__ ) # OK - 2020
# c._Car_color = "green" # OK - new attribute is assigned
# c._Car__model = "BMW" # OK - attribute is reassigned
# c._Car__year__ = 2019 # OK - new attribute is assigned
# c.__model = "BMW" # OK - new attribute is assigned
