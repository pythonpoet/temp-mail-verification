import smtplib
import email.utils
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import keys
from datetime import datetime
import config
# Email details


def send_mail(receiver_email, msg):
    # Set up the SMTP server
    server = smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT)

    server.starttls()  # Secure the connection
    server.login(keys.sender_email, keys.email_password)

    # Send the email and quit
    server.send_message(msg)
    server.quit()

def send_auth_token(receiver_email, session_id,token):
    # Create the email message
    subject = "Your yuva registration token"
    registration_link = f"{keys.server_name}/register/{session_id}/{token}"

    # Create the HTML content
    html_content = f"""
        <html>
        <body>
            <h2>Click the button to verify your email</h2>
            <a href="{registration_link}">
            <button style="background-color: #4CAF50; color: #ffffff; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer;">Verify Email</button>
            </a>
        </body>
        </html>
    """
    msg = MIMEMultipart()
    msg['From'] = keys.sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg['Date'] = email.utils.formatdate(localtime=True)
    
    # Attach the message body
    msg.attach(MIMEText(html_content, 'html'))
    send_mail(receiver_email, msg)





