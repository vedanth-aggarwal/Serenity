import sqlite3
import smtplib
import schedule
import time
from email.message import EmailMessage

# Database Connection
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Email Configuration
SENDER_EMAIL = "vedanth.aggarwal@gmail.com"  # Replace with your email
SENDER_PASSWORD = "sosn sqso pncz uzjc"  # Replace with app password

# Blog Content
BLOG_CONTENT = """\
Subject: Weekly Wellness: Understanding Anxiety Disorders

Dear Serenity User,

Anxiety disorders affect millions worldwide, often silently disrupting daily life. From generalized anxiety disorder (GAD) to panic attacks and social anxiety, these conditions create overwhelming worry, rapid heartbeat, and persistent tension. However, understanding the root causes—whether genetic, environmental, or psychological—can help individuals navigate their journey toward mental well-being.

Managing anxiety is possible through mindfulness, cognitive behavioral therapy (CBT), and lifestyle changes like regular exercise and structured routines. Seeking support from loved ones or professionals can also provide relief. Remember, anxiety doesn’t define you—healing is a journey, not a destination. At Serenity, we stand with you in embracing peace and balance.

Stay strong,
The Serenity Team
"""

# Function to send email
def send_email(recipient_email, recipient_name):
    msg = EmailMessage()
    msg.set_content(BLOG_CONTENT)
    msg["Subject"] = "Weekly Wellness: Understanding Anxiety Disorders"
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print(f"Email sent to {recipient_name} at {recipient_email}")
    except Exception as e:
        print(f"Error sending email to {recipient_email}: {e}")

# Function to fetch users and send emails
def send_weekly_email():
    cursor.execute("SELECT full_name, email FROM users")
    users = cursor.fetchall()

    for user in users:
        full_name, email = user
        send_email(email, full_name)

# Schedule the function to run every Monday
schedule.every().monday.at("09:00").do(send_weekly_email)

print("Weekly email scheduler is running...")

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute
