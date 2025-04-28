# Coffee Machine Simulator
This is a Python-based coffee machine simulator that allows users to purchase coffee while tracking available resources. The program supports two storage options:

- **JSON Mode (Default)**: Stores resources in a JSON file. This requires no additional setup.  
- **Database Mode (Optional)**: Uses an SQL Server database to manage resources. This requires a database connection.

# How to Run
1. Clone the repository and navigate to the project folder:

git clone https://github.com/tarmino-dev/thinking.git
cd fun_projects/coffee_machine

2. Set up and run a virtual environment (optional but recommended):

On Linux or macOS:

python3 -m venv venv
source venv/bin/activate

On Windows:

python3 -m venv venv
venv\Scripts\activate

3. Install dependencies:

pip install -r requirements.txt

4. Configure the mode (optional):
The default mode uses JSON storage. If you want to use the SQL database, modify the config.ini file and set:

USE_DATABASE = True

If you choose to use the SQL database, ensure your database is properly configured before running the program. You will also need to set up an SQL Server. See README_DB.md for instructions.

5. Run the script:

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
- Stores resources and profit in JSON or database (configured in config.py)
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
