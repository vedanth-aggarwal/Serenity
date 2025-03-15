import sys
import sqlite3
import smtplib
from email.message import EmailMessage
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QMessageBox, QVBoxLayout, QFormLayout, QComboBox, QTextEdit
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

# Database Setup
conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT,
    email TEXT UNIQUE,
    password TEXT,
    country TEXT,
    user_type TEXT,
    hobbies TEXT,
    stressors TEXT,
    relaxation TEXT
)
""")
conn.commit()

# Email Sending Function
def send_welcome_email(user_email, user_name):
    sender_email = "vedanth.aggarwal@gmail.com"  # Replace with your email
    sender_password = "sosn sqso pncz uzjc"  # Replace with your app password

    msg = EmailMessage()
    msg.set_content(f"Welcome to Serenity, {user_name}!\n\nWe're excited to have you on board. Explore and find your peace.")
    msg["Subject"] = "Welcome to Serenity"
    msg["From"] = sender_email
    msg["To"] = user_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print("Welcome email sent!")
    except Exception as e:
        print("Error sending email:", e)

# Custom Styling with QSS
style = """
    QWidget {
        background-color: #1E1E2E;
        color: white;
        font-family: Arial, sans-serif;
    }
    QLabel {
        font-size: 18px;
        font-weight: bold;
    }
    QLineEdit, QTextEdit, QComboBox {
        background: rgba(255, 255, 255, 0.1);
        color: white;
        border: 2px solid #8E44AD;
        border-radius: 10px;
        padding: 10px;
        font-size: 16px;
    }
    QPushButton {
        background-color: #8E44AD;
        color: white;
        font-size: 18px;
        border-radius: 10px;
        padding: 10px;
    }
    QPushButton:hover {
        background-color: #9B59B6;
    }
"""

class WelcomePage(QWidget):
    def __init__(self, stacked_widget, main_app):
        super().__init__()
        self.setWindowTitle("Welcome to Serenity")
        self.setGeometry(300, 100, 500, 400)
        self.setStyleSheet(style)

        self.stacked_widget = stacked_widget
        self.main_app = main_app  # Reference to the main application
        layout = QVBoxLayout()
        
        title = QLabel("Serenity")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        
        tagline = QLabel("Find your peace, embrace your journey.")
        tagline.setFont(QFont("Arial", 16))
        tagline.setAlignment(Qt.AlignCenter)
        
        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.show_login)
        
        self.register_btn = QPushButton("Register")
        self.register_btn.clicked.connect(self.show_register)
        
        layout.addWidget(title)
        layout.addWidget(tagline)
        layout.addWidget(self.login_btn)
        layout.addWidget(self.register_btn)
        
        self.setLayout(layout)
    
    def show_login(self):
        self.stacked_widget.setCurrentIndex(1)
    
    def show_register(self):
        self.stacked_widget.setCurrentIndex(2)

# Registration Window
class RegisterWindow(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.setWindowTitle("Register - Serenity")
        self.setGeometry(300, 100, 500, 500)
        self.setStyleSheet(style)
        self.stacked_widget = stacked_widget

        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.country_input = QLineEdit()
        self.user_type = QComboBox()
        self.user_type.addItems(["Student", "Adult"])
        self.hobbies_input = QTextEdit()
        self.stressors_input = QTextEdit()
        self.relaxation_input = QTextEdit()
        
        form_layout.addRow("Full Name:", self.name_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Password:", self.password_input)
        form_layout.addRow("Country:", self.country_input)
        form_layout.addRow("User Type:", self.user_type)
        form_layout.addRow("Hobbies:", self.hobbies_input)
        form_layout.addRow("Stressors:", self.stressors_input)
        form_layout.addRow("Relaxation Methods:", self.relaxation_input)
        
        self.register_btn = QPushButton("Register")
        self.register_btn.clicked.connect(self.register_user)
        
        layout.addLayout(form_layout)
        layout.addWidget(self.register_btn)
        self.setLayout(layout)

    def register_user(self):
        full_name = self.name_input.text()
        email = self.email_input.text()
        password = self.password_input.text()
        country = self.country_input.text()
        user_type = self.user_type.currentText()
        hobbies = self.hobbies_input.toPlainText()
        stressors = self.stressors_input.toPlainText()
        relaxation = self.relaxation_input.toPlainText()
        
        if not full_name or not email or not password:
            QMessageBox.warning(self, "Error", "Please fill in all required fields.")
            return
        
        try:
            cursor.execute("INSERT INTO users (full_name, email, password, country, user_type, hobbies, stressors, relaxation) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                           (full_name, email, password, country, user_type, hobbies, stressors, relaxation))
            conn.commit()
            send_welcome_email(email, full_name)
            QMessageBox.information(self, "Success", "Account created successfully! Check your email.")
            self.stacked_widget.setCurrentIndex(0)
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Email already registered.")

class LoginWindow(QWidget):
    def __init__(self, stacked_widget, main_app):
        super().__init__()
        self.setWindowTitle("Login - Serenity")
        self.setGeometry(300, 100, 500, 300)
        self.setStyleSheet(style)
        self.stacked_widget = stacked_widget
        self.main_app = main_app  # Reference to the main application

        layout = QVBoxLayout()
        self.email_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.login_user)

        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.email_input)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_btn)

        self.setLayout(layout)

    def login_user(self):
        email = self.email_input.text()
        password = self.password_input.text()
        
        cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = cursor.fetchone()
        
        if user:
            QMessageBox.information(self, "Login Successful", "Welcome back!")
            self.main_app.show_homepage(user[1])  # Pass the username to the homepage
        else:
            QMessageBox.warning(self, "Error", "Invalid credentials.")