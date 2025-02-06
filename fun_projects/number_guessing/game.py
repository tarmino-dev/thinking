from art import logo
from random import randint

def greeting():
    """Greets the user."""
    print(logo)
    print("Welcome to the Number Guessing Game!")

def get_difficulty():
    """Asks user for the difficulty level"""
    difficulty_mapping = {"easy": 10, "hard": 5}
    while True:
        difficulty = input("Choose a difficulty. Type 'easy' or 'hard': ").strip().lower()
        if difficulty in difficulty_mapping:
            return difficulty_mapping[difficulty]
        print("Invalid choice. Please type 'easy' or 'hard'.")

def get_user_guess():
    """Asks user for a guess."""
    while True:
        try:
            return int(input(f"Make a guess: "))
        except ValueError:
            print("Please enter a valid number!")

def play_game():
    """Basic game logic."""
    while True:
        print("\nI'm thinking of a number between 1 and 100.")
        number = randint(1, 100)
        attempts = get_difficulty()
        while attempts > 0:
            if attempts == 1:
                print(f"Last attempt! Make it count!")
            else:
                print(f"You have {attempts} attempts remaining to guess the number.")
            user_guess = get_user_guess()
            if number > user_guess:
                print("Too low." if attempts == 1 else "Too low.\nGuess again.")
            elif number < user_guess:
                print("Too high." if attempts == 1 else "Too high.\nGuess again.")
            else:
                print(f"You got it! The answer was {number}.")
                break
            attempts -= 1
        print(f"The number was {number}.\nYou've run out of guesses. Game over.") if attempts == 0 else print("Great job!")
        play_again = input("Want to play again? (yes/no): ")
        if play_again.strip().lower() not in ("yes", "y", "да"):
            print("Thanks for playing! Goodbye!")
            break

if __name__ == "__main__":
    greeting()
    play_game()