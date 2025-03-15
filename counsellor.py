import sys
import sqlite3
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QLineEdit, QMessageBox, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QLinearGradient, QPalette, QBrush

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
    c.execute('''CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    counsellor_name TEXT NOT NULL,
                    user_email TEXT NOT NULL,
                    time_slot TEXT NOT NULL,
                    message TEXT
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

# Fetch all upcoming bookings
def fetch_upcoming_bookings():
    conn = sqlite3.connect("counsellors.db")
    c = conn.cursor()
    c.execute("SELECT * FROM bookings")
    bookings = c.fetchall()
    conn.close()
    return bookings

# Save a new booking to the database
def save_booking(counsellor_name, user_email, time_slot, message):
    conn = sqlite3.connect("counsellors.db")
    c = conn.cursor()
    c.execute('''INSERT INTO bookings (counsellor_name, user_email, time_slot, message)
                 VALUES (?, ?, ?, ?)''', (counsellor_name, user_email, time_slot, message))
    conn.commit()
    conn.close()

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
    def __init__(self, stacked_widget, main_app):
        super().__init__()
        self.stacked_widget = stacked_widget  # Store the stacked widget
        self.main_app = main_app  # Store the main application reference
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Find a Mental Health Counsellor")
        self.setGeometry(100, 100, 800, 600)

        # Main layout
        main_layout = QVBoxLayout()

        # Title
        title = QLabel("Find a Counsellor")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        main_layout.addWidget(title)

        # Upcoming bookings table
        self.bookings_table = QTableWidget()
        self.bookings_table.setColumnCount(4)
        self.bookings_table.setHorizontalHeaderLabels(["Counsellor", "User Email", "Time Slot", "Message"])
        self.bookings_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.bookings_table.setStyleSheet("font-size: 14px;")
        self.update_bookings_table()
        main_layout.addWidget(QLabel("Upcoming Bookings:"))
        main_layout.addWidget(self.bookings_table)

        # Horizontal scroll area for counsellors
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
            }
            QScrollBar:horizontal {
                background: #ecf0f1;
                height: 10px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #bdc3c7;
                min-width: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                background: none;
            }
        """)

        # Counsellor cards container
        counsellor_container = QWidget()
        counsellor_layout = QHBoxLayout(counsellor_container)
        counsellor_layout.setSpacing(20)
        counsellor_layout.setContentsMargins(20, 10, 20, 10)

        # Display 3 random counsellors
        self.counsellors = fetch_random_counsellors()
        for counsellor in self.counsellors:
            counsellor_widget = self.create_counsellor_widget(counsellor)
            counsellor_layout.addWidget(counsellor_widget)

        scroll_area.setWidget(counsellor_container)
        main_layout.addWidget(scroll_area)

        # Back button
        back_button = QPushButton("Back to Home")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        back_button.clicked.connect(self.go_back)
        main_layout.addWidget(back_button)

        # Set layout
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def create_counsellor_widget(self, counsellor):
        widget = QFrame()
        widget.setFrameShape(QFrame.StyledPanel)
        widget.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 10px;
                padding: 15px;
                border: 1px solid #bdc3c7;
            }
            QFrame:hover {
                border: 2px solid #3498db;
            }
        """)

        layout = QVBoxLayout(widget)

        # Counsellor details
        name_label = QLabel(f"Name: {counsellor[1]}")
        name_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #34495e;")
        age_label = QLabel(f"Age: {counsellor[2]}")
        email_label = QLabel(f"Email: {counsellor[3]}")
        timezone_label = QLabel(f"Timezone: {counsellor[4]}")
        profile_label = QLabel(f"Profile: {counsellor[5]}")
        specialty_label = QLabel(f"Specialty: {counsellor[6]}")

        # Book button
        book_button = QPushButton("Book Session")
        book_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        book_button.clicked.connect(lambda: self.book_session(counsellor))

        # Add to layout
        layout.addWidget(name_label)
        layout.addWidget(age_label)
        layout.addWidget(email_label)
        layout.addWidget(timezone_label)
        layout.addWidget(profile_label)
        layout.addWidget(specialty_label)
        layout.addWidget(book_button)

        return widget

    def update_bookings_table(self):
        bookings = fetch_upcoming_bookings()
        self.bookings_table.setRowCount(len(bookings))
        for row, booking in enumerate(bookings):
            for col, data in enumerate(booking[1:]):  # Skip the ID column
                self.bookings_table.setItem(row, col, QTableWidgetItem(str(data)))

    def book_session(self, counsellor):
        # Booking window
        self.booking_window = QWidget()
        self.booking_window.setWindowTitle("Book a Session")
        self.booking_window.setGeometry(150, 150, 400, 300)

        layout = QVBoxLayout()

        # Counsellor details
        counsellor_label = QLabel(f"Booking with {counsellor[1]}")
        counsellor_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
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
        confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        confirm_button.clicked.connect(lambda: self.confirm_booking(counsellor))
        layout.addWidget(confirm_button)

        self.booking_window.setLayout(layout)
        self.booking_window.show()

    def confirm_booking(self, counsellor):
        time_slot = self.time_input.currentText()
        message = self.message_input.toPlainText()

        # Save booking to database
        user_email = "user@example.com"  # Replace with user's email
        save_booking(counsellor[1], user_email, time_slot, message)

        # Send emails
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
        self.update_bookings_table()

    def go_back(self):
        """Navigate back to the homepage."""
        self.stacked_widget.setCurrentWidget(self.main_app.home_page)

# Main application
if __name__ == "__main__":
    create_database()
    #insert_dummy_data()  # Comment this line after first run to avoid duplicate data

    app = QApplication(sys.argv)
    window = CounsellorApp()
    window.show()
    sys.exit(app.exec_())