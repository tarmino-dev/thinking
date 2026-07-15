import datetime as dt
import smtplib
import random

# Fill in the constants with your data.
# Hint: Create an App Password in the Security section of your mailbox' settings
#       and use it instead of your regular password.
MY_EMAIL = ""
MY_PASSWORD = ""
RECIPIENTS_EMAIL = ""

current_day = dt.datetime.now().weekday()
if current_day == 0:  # Monday
    with open("./quotes.txt", mode="r") as quote_file:
        all_quotes = quote_file.readlines()
        quote = random.choice(all_quotes)

    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(user=MY_EMAIL, password=MY_PASSWORD)
        connection.sendmail(
            from_addr=MY_EMAIL,
            to_addrs=RECIPIENTS_EMAIL,
            msg=f"Subject:Monday motivation\n\n{quote}"
        )
