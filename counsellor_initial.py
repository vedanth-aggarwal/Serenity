import sys
import sqlite3
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QLineEdit, QMessageBox, QComboBox
from PyQt5.QtCore import Qt

# Database setup
def create_database():
    conn = sqlite3.connect("counsellors.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS counsellors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age INTEGER,
                    email TEXT NOT NULL,
                    timezone TEXT,
                    profile TEXT,
                    specialty TEXT
                )''')
    conn.commit()
    conn.close()

# Insert dummy data into the database
def insert_dummy_data():
    counsellors = [
        ("Dr. John Doe", 45, "john.doe@example.com", "GMT+1", "Experienced in anxiety and depression.", "Anxiety"),
        ("Dr. Jane Smith", 38, "jane.smith@example.com", "GMT+2", "Specializes in relationship counseling.", "Relationships"),
        ("Dr. Emily Brown", 50, "emily.brown@example.com", "GMT+0", "Expert in trauma and PTSD.", "Trauma"),
        ("Dr. Michael Lee", 42, "michael.lee@example.com", "GMT-5", "Focuses on career counseling.", "Career"),
        ("Dr. Sarah Green", 55, "sarah.green@example.com", "GMT+3", "Specializes in child psychology.", "Child Psychology")
    ]
    conn = sqlite3.connect("counsellors.db")
    c = conn.cursor()
    c.executemany('''INSERT INTO counsellors (name, age, email, timezone, profile, specialty)
                     VALUES (?, ?, ?, ?, ?, ?)''', counsellors)
    conn.commit()
    conn.close()

# Fetch 3 random counsellors from the database
def fetch_random_counsellors():
    conn = sqlite3.connect("counsellors.db")
    c = conn.cursor()
    c.execute("SELECT * FROM counsellors ORDER BY RANDOM() LIMIT 3")
    counsellors = c.fetchall()
    conn.close()
    return counsellors

# Send email with Zoom invite
def send_email(to_email, subject, body):
    sender_email = "vedanth.aggarwal@gmail.com"  # Replace with your email
    sender_password = "sosn sqso pncz uzjc"  # Replace with your email password

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

# Main application window
class CounsellorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Find a Mental Health Counsellor")
        self.setGeometry(100, 100, 600, 400)

        # Main layout
        layout = QVBoxLayout()

        # Title
        title = QLabel("Find a Counsellor")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        # Display 3 random counsellors
        self.counsellors = fetch_random_counsellors()
        for counsellor in self.counsellors:
            counsellor_widget = self.create_counsellor_widget(counsellor)
            layout.addWidget(counsellor_widget)

        # Set layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def create_counsellor_widget(self, counsellor):
        widget = QWidget()
        layout = QVBoxLayout()

        # Counsellor details
        name_label = QLabel(f"Name: {counsellor[1]}")
        age_label = QLabel(f"Age: {counsellor[2]}")
        email_label = QLabel(f"Email: {counsellor[3]}")
        timezone_label = QLabel(f"Timezone: {counsellor[4]}")
        profile_label = QLabel(f"Profile: {counsellor[5]}")
        specialty_label = QLabel(f"Specialty: {counsellor[6]}")

        # Book button
        book_button = QPushButton("Book Session")
        book_button.clicked.connect(lambda: self.book_session(counsellor))

        # Add to layout
        layout.addWidget(name_label)
        layout.addWidget(age_label)
        layout.addWidget(email_label)
        layout.addWidget(timezone_label)
        layout.addWidget(profile_label)
        layout.addWidget(specialty_label)
        layout.addWidget(book_button)

        widget.setLayout(layout)
        return widget

    def book_session(self, counsellor):
        # Booking window
        self.booking_window = QWidget()
        self.booking_window.setWindowTitle("Book a Session")
        self.booking_window.setGeometry(150, 150, 400, 300)

        layout = QVBoxLayout()

        # Counsellor details
        counsellor_label = QLabel(f"Booking with {counsellor[1]}")
        layout.addWidget(counsellor_label)

        # Time slot input
        time_label = QLabel("Select Time Slot:")
        self.time_input = QComboBox()
        self.time_input.addItems(["10:00 AM", "2:00 PM", "4:00 PM", "6:00 PM"])
        layout.addWidget(time_label)
        layout.addWidget(self.time_input)

        # Message input
        message_label = QLabel("Message to Counsellor:")
        self.message_input = QTextEdit()
        layout.addWidget(message_label)
        layout.addWidget(self.message_input)

        # Book button
        confirm_button = QPushButton("Confirm Booking")
        confirm_button.clicked.connect(lambda: self.confirm_booking(counsellor))
        layout.addWidget(confirm_button)

        self.booking_window.setLayout(layout)
        self.booking_window.show()

    def confirm_booking(self, counsellor):
        time_slot = self.time_input.currentText()
        message = self.message_input.toPlainText()

        # Send emails
        user_email = "vedanth.aggarwal@gmail.com"  # Replace with user's email
        counsellor_email = counsellor[3]

        # Email to user
        user_subject = "Counselling Session Booking Confirmation"
        user_body = f"""Dear User,
Your session with {counsellor[1]} has been booked for {time_slot}.
Zoom Link: https://zoom.us/j/1234567890
Message to Counsellor: {message}
"""
        send_email(user_email, user_subject, user_body)

        # Email to counsellor
        counsellor_subject = "New Session Booking"
        counsellor_body = f"""Dear {counsellor[1]},
You have a new session booked for {time_slot}.
User Message: {message}
Zoom Link: https://zoom.us/j/1234567890
"""
        send_email(counsellor_email, counsellor_subject, counsellor_body)

        QMessageBox.information(self, "Booking Confirmed", "Your session has been booked. Check your email for details.")
        self.booking_window.close()

# Main application
if __name__ == "__main__":
    create_database()
    #insert_dummy_data()  # Comment this line after first run to avoid duplicate data

    app = QApplication(sys.argv)
    window = CounsellorApp()
    window.show()
    sys.exit(app.exec_())