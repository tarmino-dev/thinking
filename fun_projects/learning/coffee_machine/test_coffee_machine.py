import pytest
import json
import os
import copy
from main import CoffeeMachine
from data import MENU, RESOURCES

@pytest.fixture
def coffee_machine():
    """Fixture to create a new coffee machine instance before each test."""
    machine = CoffeeMachine()
    machine.resources = copy.deepcopy(RESOURCES)  # Reset resources
    machine.profit = 0  # Reset profit
    return machine

def test_is_enough_resources_enough(coffee_machine):
    """Test that the machine correctly detects sufficient resources."""
    assert coffee_machine.is_enough_resources("espresso") is True

def test_is_enough_resources_not_enough(coffee_machine):
    """Test that the machine correctly detects insufficient resources."""
    coffee_machine.resources["water"][0] = 10  # Reduce water
    assert coffee_machine.is_enough_resources("latte") is False

def test_is_enough_money_exact(coffee_machine):
    """Test that the machine correctly accepts exact money."""
    assert coffee_machine.is_enough_money(2.5, "latte") == (True, 2.5)

def test_is_enough_money_more(coffee_machine):
    """Test that the machine correctly processes overpayment."""
    assert coffee_machine.is_enough_money(3.0, "latte") == (True, 2.5)

def test_is_enough_money_not_enough(coffee_machine):
    """Test that the machine rejects insufficient money."""
    assert coffee_machine.is_enough_money(1.0, "latte") == (False, 0)

def test_make_coffee_updates_resources(coffee_machine):
    """Test that making coffee correctly deducts resources."""
    coffee_machine.make_coffee("espresso")
    assert coffee_machine.resources["water"][0] == RESOURCES["water"][0] - MENU["espresso"]["ingredients"]["water"]
    assert coffee_machine.resources["coffee"][0] == RESOURCES["coffee"][0] - MENU["espresso"]["ingredients"]["coffee"]

def test_save_and_load_resources(coffee_machine):
    """Test that saving and loading resources works correctly."""
    test_data = {
        "resources": {
            "water": [123, "ml"],
            "milk": [456, "ml"],
            "coffee": [789, "g"]
        },
        "profit": 9.99
    }
    
    # Save test data
    with open(coffee_machine.DATA_FILE, "w") as file:
        json.dump(test_data, file)

    # Load data and check values
    coffee_machine.resources, coffee_machine.profit = coffee_machine.load_resources()
    assert coffee_machine.resources["water"][0] == 123
    assert coffee_machine.resources["milk"][0] == 456
    assert coffee_machine.resources["coffee"][0] == 789
    assert coffee_machine.profit == 9.99

    # Clean up test file
    os.remove(coffee_machine.DATA_FILE)
