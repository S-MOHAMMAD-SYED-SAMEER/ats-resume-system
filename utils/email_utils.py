import smtplib
from email.mime.text import MIMEText


def send_email(receiver_email, subject, body):

    sender_email = "your_email@gmail.com"
    password = "your_app_password"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.send_message(msg)

        return True

    except Exception as e:
        print("Email error:", e)
        return False