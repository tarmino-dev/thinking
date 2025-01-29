from art import logo
from random import randint
from collections import defaultdict

def get_difficulty():
    """Asks user for the difficulty level"""
    difficulty_mapping = defaultdict(lambda: 5, {"easy": 10, "hard": 5})
    difficulty = input("Choose a difficulty. Type 'easy' or 'hard': ").lower()
    return difficulty_mapping[difficulty]

def get_user_guess():
    """Asks user for a guess."""
    while True:
        try:
            return int(input(f"Make a guess: "))
        except ValueError:
            print("Please enter a valid number!")

def play_game():
    """Basic game logic."""
    print(logo)
    print("Welcome to the Number Guessing Game!")
    print("I'm thinking of a number between 1 and 100.")
    number = randint(1, 100)
    attempts = get_difficulty()
    print(f"DEBUG. number: {number}")

    while attempts > 0:
        print(f"You have {attempts} attempts remaining to guess the number.")
        user_guess = get_user_guess()
        if number > user_guess:
            if attempts == 1:
                print("Too low.")
            else:
                print(f"Too low.\nGuess again.")
        elif number < user_guess:
            if attempts == 1:
                print("Too high.")
            else:
                print(f"Too high.\nGuess again.")
        else:
            print(f"You got it! The answer was {number}.")
            return
        attempts -= 1
    print("You've run out of guesses. Restart the game to play again.")


    print("-------------DEBUGGING-------------")
    print(f"DEBUG. number: {number}")
    print(f"DEBUG. attempts: {attempts}")
    print(f"DEBUG. user_guess: {user_guess}")

if __name__ == "__main__":
    play_game()