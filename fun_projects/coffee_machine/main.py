from art import logo
from data import MENU, RESOURCES, COINS
import copy

def get_prompt():
    while True:
        drink = input("What would you like? (espresso/latte/cappuccino): ").lower()
        if drink in MENU or drink == "off" or drink == "report":
            return drink
        print("Invalid choice. Please type 'espresso' or 'latte' or 'cappuccino'")

def print_report(money):
    print("\n=== Coffee Machine Report ===")
    for ingredient, (amount, unit) in RESOURCES.items():
        print(f"{ingredient.capitalize()}: {amount}{unit}")
    print(f"Money: ${money:.2f}\n")

def is_enough_resources(order, resources):
    enough_resources = True
    for ingredient, amount in MENU[order]["ingredients"].items():
        if resources[ingredient][0] < amount:
            print(f"Sorry, there is not enough {ingredient}.")
            enough_resources = False
    return enough_resources

def process_coin_input():
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

def is_enough_money(total_inserted, order):
    order_cost = MENU[order]['cost']
    if order_cost > total_inserted:
        print(f"Your drink costs ${order_cost}, but you have inserted only ${total_inserted}")
        print("Sorry, that's not enough money. Money refunded.")
        return False, 0
    change = round(total_inserted - order_cost, 2)
    if change > 0:
        print(f"Here is ${change} in change.")
    return True, order_cost

def start_coffee_machine(RESOURCES):
    print(logo)
    profit = 0
    while True:
        order = get_prompt()
        if order == "off":
            print("The coffee machine is off. Bye!")
            break
        if order == "report":
            print_report(profit)
            continue
        if not is_enough_resources(order, RESOURCES):
            continue
        total_inserted = process_coin_input()
        enough_money, income = is_enough_money(total_inserted, order)
        if not enough_money:
            continue
        for item, amount in MENU[order]["ingredients"].items():
            RESOURCES[item][0] -= amount
        print(f"Here is your {order}. Enjoy!")
        profit += income
        

if __name__ == "__main__":
    start_coffee_machine(copy.deepcopy(RESOURCES))
