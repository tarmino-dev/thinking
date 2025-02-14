from art import logo
from data import MENU, RESOURCES, COINS

def get_prompt():
    while True:
        drink = input("What would you like? (espresso/latte/cappuccino): ").lower()
        if drink in MENU or drink == "off" or drink == "report":
            return drink
        print("Invalid choice. Please type 'espresso' or 'latte' or 'cappuccino'")

def print_report(money):
    for ingredient, amount in RESOURCES.items():
        print(f"{ingredient.capitalize()}: {amount[0]}{amount[1]}")
    print(f"Money: ${money}")

def is_enough_resources(order):
    enough_resources = True
    for ingredient, amount in MENU[order]["ingredients"].items():
        if RESOURCES[ingredient][0] < amount:
            print(f"Sorry, there is not enough {ingredient}.")
            enough_resources = False
    return enough_resources

def process_coin_input():
    print("Please insert coins.")
    total_inserted = 0
    for coin, value in COINS.items():
        total_inserted += int(input(f"How many {coin}s are you inserting? ")) * value
    total_inserted = float("{:.2f}".format(total_inserted))
    return total_inserted

def is_enough_money(total_inserted, order):
    income = 0
    change = 0
    order_cost = MENU[order]['cost']
    if order_cost > total_inserted:
        print(f"Your drink costs ${order_cost}, but you have inserted only ${total_inserted}")
        print("Sorry, that's not enough money. Money refunded.")
        return False, 0
    elif order_cost < total_inserted:
        change = total_inserted - order_cost
        change = float("{:.2f}".format(change))
    income += total_inserted
    if change:
        income -= change
        print(f"Here is ${change} in change.")
    return True, income

def start_coffee_machine():
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
        if not is_enough_resources(order):
            continue
        total_inserted = process_coin_input()
        enough_money, income = is_enough_money(total_inserted, order)
        if enough_money:
            for item, amount in MENU[order]["ingredients"].items():
                RESOURCES[item][0] -= amount
            print(f"Here is your {order}. Enjoy!")
            profit += income
        continue

if __name__ == "__main__":
    start_coffee_machine()
