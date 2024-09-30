from email.mime.multipart import MIMEMultipart
import smtplib
import requests


def gotify(url, token, title, message):
    url = f'{url}/message?token={token}'
    data = {
        "title": title,
        "message": message,
        "extras": {"client::display": {"contentType": "text/markdown"}},
        "priority": 1,
    }
    requests.post(url, json=data).json()

def send_mail(address, code, subject, content):
    smtp_server = 'smtp.qq.com'
    smtp_port = 587

    # Create a message
    msg = MIMEMultipart()
    msg['From'] = address
    msg['To'] = address
    msg['Subject'] = subject
    msg.attach(content)

    # Connect to SMTP server
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(address, code)

    # Send the email
    server.sendmail(address, code, msg.as_string())

    # Close the SMTP connection
    server.quit()

    print('Email sent successfully!')


if __name__ == "__main__":
    gotify('title', 'foo *content* bar')