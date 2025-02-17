# Coffee Machine Simulator
A Python console program that simulates a coffee vending machine.

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
- Serves espresso, latte, and cappuccino
- Checking if resources are sufficient
- Allows users to refill resources (triggered by the "refill" command)
- Accepts coins and returns change if necessary
- Verifying successful transactions
- Returning change 
- Dispensing coffee
- Printing a report on the current state of resources and the profit (triggered by the "report" command)
- Saves and loads resources using JSON
- Logs all operations in a log file
- Turning the coffee machine off (triggered by the "off" command)
- Fully tested with pytest


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
