from art import logo

print(logo)

MENU = {
    "espresso": {
        "ingredients": {
            "water": 50,
            "coffee": 18,
        },
        "cost": 1.5,
    },
    "latte": {
        "ingredients": {
            "water": 200,
            "milk": 150,
            "coffee": 24,
        },
        "cost": 2.5,
    },
    "cappuccino": {
        "ingredients": {
            "water": 250,
            "milk": 100,
            "coffee": 24,
        },
        "cost": 3.0,
    }
}

resources = {
    "water": [300, "ml"],
    "milk": [200, "ml"],
    "coffee": [100, "g"],
}

coins = {
    "quarter": 0.25,
    "dime": 0.10,
    "nickle": 0.05,
    "pennie": 0.01,
}

def prompt():
    while True:
        drink = input("What would you like? (espresso/latte/cappuccino): ").lower()
        if drink in MENU or drink == "off" or drink == "report":
            return drink
        print("Invalid choice. Please type 'espresso' or 'latte' or 'cappuccino'")

def print_report(money):
    for k, v in resources.items():
        print(f"{k.capitalize()}: {v[0]}{v[1]}")
    print(f"Money: ${money}")

def start_coffee_machine():
    money = 0
    while True:
        order = prompt()
        if order == "off":
            print("The coffee machine is off. Bye!")
            break
        if order == "report":
            print_report(money)
            continue
        enough_ingredients = True
        for item, amount in MENU[order]["ingredients"].items():
            if resources[item][0] < amount:
                print(f"Sorry, there is not enough {item}.")
                enough_ingredients = False
        if not enough_ingredients:
            continue
        print("Please insert coins.")
        total_inserted = 0
        for coin, value in coins.items():
            total_inserted += int(input(f"How many {coin}s are you inserting? ")) * value
        total_inserted = float("{:.2f}".format(total_inserted))
        change = 0
        order_cost = MENU[order]['cost']
        if order_cost > total_inserted:
            print(f"Your drink costs ${order_cost}, but you have inserted only ${total_inserted}")
            print("Sorry, that's not enough money. Money refunded.")
            continue
        elif order_cost < total_inserted:
            change = total_inserted - order_cost
            change = float("{:.2f}".format(change))
        money += total_inserted
        if change:
            money -= change
            print(f"Here is ${change} in change.")
        for item, amount in MENU[order]["ingredients"].items():
            resources[item][0] -= amount
        print(f"Here is your {order}. Enjoy!")

if __name__ == "__main__":
    start_coffee_machine()