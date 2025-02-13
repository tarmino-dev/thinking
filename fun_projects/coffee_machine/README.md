# Coffee Machine
A simple Python program that simulates a coffee machine. It offers users various drinks, accepts different coins, and provides change if excess money is inserted. The software can report the current state of resources and be turned off when needed.

# How to Run
1. Clone the repository:

git clone https://github.com/tarmino-dev/thinking.git

2. Navigate to the project folder:

cd fun_projects/coffee_machine

3. Run the script:

python main.py

or

python3 main.py

# Features
- Prompting the user to select a drink
- Checking if resources are sufficient
- Processing coin input
- Verifying successful transactions
- Returning change if necessary
- Dispensing coffee
- Printing a report on the current state of resources and the profit (triggered by the "report" command)
- Turning the coffee machine off (triggered by the "off" command)


# Example Output
What would you like? (espresso/latte/cappuccino): latte
Please insert coins.
How many quarters are you inserting? 8
How many dimes are you inserting? 8
How many nickles are you inserting? 8
How many pennies are you inserting? 8
Here is $0.78 in change.
Here is your latte. Enjoy!
What would you like? (espresso/latte/cappuccino): report
Water: 100ml
Milk: 50ml
Coffee: 76g
Money: $2.5
What would you like? (espresso/latte/cappuccino): off
The coffee machine is off. Bye!
