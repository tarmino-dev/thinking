from art import logo
from data import MENU, RESOURCES, COINS
from prettytable import PrettyTable
import copy
import json
import os
import logging


class CoffeeMachineJSON:
    """A class representing a coffee machine simulator with persistent storage in a JSON file."""

    DATA_FILE = "resources.json"

    def __init__(self):
        """Initialize the coffee machine with resources and profit, loading from a file if available."""
        self.resources, self.profit = self.load_resources()

    def load_resources(self):
        """Loads resources and profit from a JSON file if it exists; otherwise, uses default values."""
        if os.path.exists(self.DATA_FILE):
            with open(self.DATA_FILE, "r") as file:
                data = json.load(file)
                return data["resources"], data.get("profit", 0)
        return copy.deepcopy(RESOURCES), 0
    
    def save_resources(self):
        """Saves the current resources and profit to a JSON file."""
        data = {
            "resources": self.resources,
            "profit": self.profit
        }
        with open(self.DATA_FILE, "w") as file:
            json.dump(data, file, indent=4)

    def print_report(self):
        """Prints the current status of resources and profit."""
        print("\n=== Coffee Machine Report ===")
        report_table = PrettyTable()
        report_table.field_names = ["Resource", "Amount"]
        report_table.align = "l"
        for ingredient, data in self.resources.items():
            amount_unit = f"{data[0]} {data[1]}"
            report_table.add_row([ingredient.capitalize(), amount_unit])
        print(report_table)
        print(f"Money: ${self.profit:.2f}\n")

    def refill_resources(self):
        """Allows the user to manually refill water, milk, or coffee."""
        print("\n=== Refill Resources ===")
        print("Available resources to refill: water, milk, coffee")
        while True:
            resource = input("Which resource would you like to refill? (type 'exit' to cancel): ").lower()
            if resource == "exit":
                print("Exiting refill.")
                logging.info("Refill operation ended.")
                break
            if resource not in self.resources:
                print("Invalid resource. Please type 'water', 'milk', or 'coffee'.")
                continue
            while True:
                try:
                    amount = int(input(f"How much {resource} would you like to add? (current: {self.resources[resource][0]}{self.resources[resource][1]}): "))
                    if amount < 0:
                        print("Please enter a positive number.")
                        continue
                    break
                except ValueError:
                    print("Invalid input. Please enter a valid number.")

            self.resources[resource][0] += amount
            self.save_resources()
            logging.info(f"Refilled {amount}{self.resources[resource][1]} of {resource}")
            print(f"{amount}{self.resources[resource][1]} of {resource} added successfully!")

    def is_enough_resources(self, order):
        """Checks if there are enough resources for the selected drink."""
        enough_resources = True
        for ingredient, amount in MENU[order]["ingredients"].items():
            if self.resources[ingredient][0] < amount:
                logging.warning(f"Not enough resources: {ingredient}")
                print(f"Sorry, there is not enough {ingredient}.")
                enough_resources = False
        return enough_resources
    
    def process_coin_input(self):
        """Handles coin input from the user and returns the total inserted amount."""
        print("Please insert coins.")
        total_inserted = 0
        for coin, value in COINS.items():
            while True:
                try:
                    count = int(input(f"How many {coin}s are you inserting? "))
                    if count < 0:
                        print("Please enter a non-negative number.")
                        continue
                    total_inserted += count * value
                    break
                except ValueError:
                    print("Invalid input. Please enter a number.")
        return round(total_inserted, 2)
    
    def is_enough_money(self, total_inserted, order):
        """Checks if the user inserted enough money. Returns True and order cost if successful."""
        order_cost = MENU[order]['cost']
        if order_cost > total_inserted:
            logging.warning(f"Transaction failed: inserted ${total_inserted}, required ${order_cost}.")
            print(f"Your drink costs ${order_cost}, but you have inserted only ${total_inserted}")
            print("Sorry, that's not enough money. Money refunded.")
            return False, 0
        logging.info(f"Transaction successful: ${total_inserted} inserted.")
        change = round(total_inserted - order_cost, 2)
        if change > 0:
            print(f"Here is ${change} in change.")
        return True, order_cost
    
    def make_coffee(self, order):
        """Deducts the required ingredients and serves the coffee."""
        for ingredient, amount in MENU[order]["ingredients"].items():
            self.resources[ingredient][0] -= amount
        self.save_resources()
        logging.info(f"Dispensed: {order}.")
        print(f"Here is your {order}. Enjoy!")

    def start(self):
        """Starts the coffee machine and handles user input."""
        logging.info("Coffee machine started.")
        print(logo)
        while True:
            order = input("What would you like? (espresso/latte/cappuccino/report/refill/off): ").lower()
            if order == "off":
                logging.info("Coffee machine turned off.")
                print("Saving resources and shutting down...")
                self.save_resources()
                print("The coffee machine is off. Bye!")
                break
            if order == "report":
                self.print_report()
                continue
            if order == "refill":
                self.refill_resources()
                continue
            if order not in MENU:
                print("Invalid choice. Please type 'espresso' or 'latte' or 'cappuccino'")
                continue
            logging.info(f"User selected: {order}.")
            if not self.is_enough_resources(order):
                continue
            total_inserted = self.process_coin_input()
            enough_money, income = self.is_enough_money(total_inserted, order)
            if enough_money:
                self.make_coffee(order)
                self.profit += income
                self.save_resources()