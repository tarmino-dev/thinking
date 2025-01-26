from art import logo
from random import randint

print(logo)

number = randint(1, 100)
print(f"DEBUG. number: {number}")

difficulty = input("""Welcome to the Number Guessing Game!
I'm thinking of a number between 1 and 100.
Choose a difficulty. Type 'easy' or 'hard': """)

difficulty_mapping = {"easy": 10, "hard": 5}
attempts_number = difficulty_mapping[difficulty]

def give_attempt(result):
    global attempts_number
    attempts_number -= 1
    if attempts_number > 0:
        print(f"""Too {result}.\nGuess again.""")

while attempts_number > 0:
    user_guess = int(input(f"""You have {attempts_number} attempts remaining to guess the number.\nMake a guess: """))
    if number > user_guess:
        give_attempt("low")
        
    elif number < user_guess:
        give_attempt("high")
        
    else:
        print(f"You got it! The answer was {number}.")
        break
else:
    print("You've run out of guesses. Restart the game to play again.")


print("-------------DEBUGGING-------------")
print(f"DEBUG. number: {number}")
print(f"DEBUG. difficulty: {difficulty}")
print(f"DEBUG. attempts_number: {attempts_number}")
print(f"DEBUG. user_guess: {user_guess}")
