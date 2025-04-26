import datetime as dt
import smtplib
import pandas
import random

# Fill in the constants with your data.
# Hint: Create an App Password in the Security section of your mailbox' settings
#       and use it instead of your regular password.
MY_EMAIL = ""
MY_PASSWORD = ""

birthdays_data = pandas.read_csv("birthdays.csv")

current_month = dt.datetime.now().month
current_day = dt.datetime.now().day

for index, row in birthdays_data.iterrows():
    if row["month"] == current_month and row["day"] == current_day:
        recipient_name = row["name"]
        recipient_email = row["email"]
        with open(f"./letter_templates/letter_{random.randint(1, 3)}.txt", mode="r") as letter_file:
            template_text = letter_file.read()
            personal_text = template_text.replace("[NAME]", recipient_name)
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(user=MY_EMAIL, password=MY_PASSWORD)
            connection.sendmail(from_addr=MY_EMAIL, to_addrs=recipient_email,
                                msg=f"Subject:Happy Birthday!\n\n{personal_text}")
