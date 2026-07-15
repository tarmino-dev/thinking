import smtplib

# Fill in the constants with your data.
# Hint: Create an App Password in the Security section of your mailbox' settings
#       and use it instead of your regular password.
MY_EMAIL = ""
MY_PASSWORD = ""
RECIPIENTS_EMAIL = ""

with smtplib.SMTP("smtp.gmail.com") as connection:
    connection.starttls()
    connection.login(user=MY_EMAIL, password=MY_PASSWORD)
    connection.sendmail(
        from_addr=MY_EMAIL,
        to_addrs=RECIPIENTS_EMAIL,
        msg="Subject:Hello\n\nThis is the body of my email."
    )
