import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import keys
from datetime import datetime
# Email details


def send_mail(receiver_email, msg):
    # Set up the SMTP server
    server = smtplib.SMTP('smtp.autistici.org','587')
    #server.connect('smtp.autistici.org','587')
    server.starttls()  # Secure the connection
    server.login(keys.sender_email, keys.email_password)

    # Send the email and quit
    server.send_message(msg)
    server.quit()

def send_auth_code(receiver_email, code):
    # Create the email message
    subject = "Yuva registration code"
    message_body = f"This is your registration code: {code}"

    msg = MIMEMultipart()
    msg['From'] = keys.sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg['Date'] = email.utils.formatdate(localtime=True)
    
    # Attach the message body
    msg.attach(MIMEText(message_body, 'plain'))
    msg.attach(MIMEText(message_body, 'plain'))
    send_mail(receiver_email, msg)


if __name__ == '__main__':
    send_auth_code('david_wild@bluewin.ch', 'your code')


