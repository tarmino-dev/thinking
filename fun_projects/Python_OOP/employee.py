class Employee():
    def __init__(self, name, age, level='junior'):
        self.__name = name # name mangling
        self._age = age
        self._level = level
        self._salary = self.__compute_salary()

    def promote(self):
        if self._level == 'junior':
            self._level = 'senior'
        elif self._level == 'senior':
            self._level = 'CEO'
        self._salary = self.__compute_salary()

    def __compute_salary(self):
        if self._level == 'junior':
            return 10000  
        elif self._level == 'senior':
            return 20000
        elif self._level == 'CEO':
            return 1000000
        else:
            print('unknown level')

    def get_name(self):
        return self.__name

    def get_age(self):
        return self._age    

    def get_salary(self):
        return self._salary
