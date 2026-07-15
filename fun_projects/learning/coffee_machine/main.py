import logging
import config


logging.basicConfig(
    filename=config.LOG_FILE,
    level=logging.INFO,
    format="[%(asctime)s] - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

if config.USE_DATABASE:
    from coffee_db import CoffeeMachineDB as CoffeeMachine
else:
    from coffee_json import CoffeeMachineJSON as CoffeeMachine


if __name__ == "__main__":
    coffee_machine = CoffeeMachine()
    coffee_machine.start()
