from employee import Employee

e1 = Employee('Alex', 25, 'junior')

# if name attribute is defined as '__name' in the class definition, then outside the class we should call in using such syntax: '_Employee__name'
print(f'Employee name is {e1._Employee__name}, age is {e1.get_age()}, salary is {e1._salary}')

# same for methods

print(e1._Employee__compute_salary())