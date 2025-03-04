import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email login credentials
sender_email = "your_email@gmail.com"
receiver_email = "receiver_email@example.com"
password = "your_password"

# Email subject and body
subject = "Automated Email"
body = "This is an automated email sent by Python."

# Create the email message
msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = receiver_email
msg['Subject'] = subject
msg.attach(MIMEText(body, 'plain'))

# Send the email
try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, password)
    text = msg.as_string()
    server.sendmail(sender_email, receiver_email, text)
    server.quit()
    print("Email sent successfully!")
except Exception as e:
    print(f"Error: {e}")

