import sys
import sqlite3
import random
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QRadioButton, QButtonGroup, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout, QScrollArea, QFrame, QApplication
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QLinearGradient, QPalette, QBrush
import pygame  # For playing ambient music

# Initialize pygame mixer for background music
pygame.mixer.init()

# Database setup
def create_database():
    conn = sqlite3.connect("reflection.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS answers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    prompt TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    is_public INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )''')
    conn.commit()
    conn.close()

# Insert dummy data into the database
def insert_dummy_data():
    users = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
    prompts = [
        "What are you most grateful for today?",
        "What challenged you today, and how did you overcome it?",
        "What is one thing you learned about yourself today?",
        "What made you smile today?",
        "What is one thing you can do better tomorrow?"
    ]
    sample_answers = [
        "I am grateful for the support of my friends and family. They always encourage me to keep going, even when things get tough.",
        "Today, I faced a challenging project at work. I overcame it by breaking it into smaller tasks and focusing on one step at a time.",
        "I learned that I need to take more breaks during the day. It helps me stay focused and productive in the long run.",
        "Seeing my dog wag its tail when I got home made me smile. It's the little things that bring joy.",
        "Tomorrow, I can improve by being more patient with myself and others. I tend to rush things, but slowing down can lead to better results."
    ]

    conn = sqlite3.connect("reflection.db")
    c = conn.cursor()

    for i in range(3):
        username = random.choice(users)
        c.execute("INSERT INTO users (username) VALUES (?)", (username,))

    for i in range(3):
        user_id = random.randint(1, 3)
        prompt = random.choice(prompts)
        answer = random.choice(sample_answers)
        is_public = 1
        date = datetime.now().strftime("%Y-%m-%d")
        c.execute('''INSERT INTO answers (user_id, prompt, answer, is_public, date)
                     VALUES (?, ?, ?, ?, ?)''', (user_id, prompt, answer, is_public, date))

    conn.commit()
    conn.close()

# Fetch a random prompt
def fetch_random_prompt():
    prompts = [
        "What are you most grateful for today?",
        "What challenged you today, and how did you overcome it?",
        "What is one thing you learned about yourself today?",
        "What made you smile today?",
        "What is one thing you can do better tomorrow?"
    ]
    return random.choice(prompts)

# Fetch public answers for the current prompt
def fetch_public_answers(prompt):
    conn = sqlite3.connect("reflection.db")
    c = conn.cursor()
    c.execute("SELECT users.username, answers.answer, answers.date FROM answers JOIN users ON answers.user_id = users.id WHERE prompt = ? AND is_public = 1", (prompt,))
    answers = c.fetchall()
    conn.close()
    return answers

# Save a new answer to the database
def save_answer(user_id, prompt, answer, is_public):
    conn = sqlite3.connect("reflection.db")
    c = conn.cursor()
    c.execute('''INSERT INTO answers (user_id, prompt, answer, is_public, date)
                 VALUES (?, ?, ?, ?, ?)''', (user_id, prompt, answer, is_public, datetime.now().strftime("%Y-%m-%d")))
    conn.commit()
    conn.close()

class ReflectionPage(QWidget):
    def __init__(self, stacked_widget, main_app):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.main_app = main_app
        create_database()
        insert_dummy_data()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Daily Reflection")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            background-color: #f0f4f8;
            color: #2c3e50;
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        title = QLabel("Daily Reflection Prompt")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
        """)
        main_layout.addWidget(title)

        self.prompt = fetch_random_prompt()
        prompt_label = QLabel(f"Today's Prompt: {self.prompt}")
        prompt_label.setStyleSheet("""
            font-size: 18px;
            color: #34495e;
            padding: 10px;
        """)
        main_layout.addWidget(prompt_label)

        self.answer_input = QTextEdit()
        self.answer_input.setPlaceholderText("Write your reflection here...")
        self.answer_input.setStyleSheet("""
            font-size: 14px;
            padding: 15px;
            border-radius: 10px;
            background-color: #ffffff;
            border: 1px solid #bdc3c7;
        """)
        main_layout.addWidget(self.answer_input)

        privacy_label = QLabel("Make your answer:")
        privacy_label.setStyleSheet("""
            font-size: 16px;
            color: #34495e;
            padding: 10px;
        """)
        main_layout.addWidget(privacy_label)

        self.privacy_group = QButtonGroup()
        self.public_radio = QRadioButton("Public")
        self.private_radio = QRadioButton("Private")
        self.public_radio.setChecked(True)
        self.privacy_group.addButton(self.public_radio)
        self.privacy_group.addButton(self.private_radio)

        privacy_layout = QHBoxLayout()
        privacy_layout.addWidget(self.public_radio)
        privacy_layout.addWidget(self.private_radio)
        privacy_layout.setSpacing(20)
        main_layout.addLayout(privacy_layout)

        submit_button = QPushButton("Submit Reflection")
        submit_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-size: 16px;
                padding: 15px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        submit_button.clicked.connect(self.submit_reflection)
        main_layout.addWidget(submit_button)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
            }
            QScrollBar:vertical {
                background: #ecf0f1;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #bdc3c7;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
            }
        """)

        self.answers_container = QWidget()
        self.answers_layout = QVBoxLayout(self.answers_container)
        self.answers_layout.setSpacing(15)
        self.answers_layout.setContentsMargins(10, 10, 10, 10)

        self.update_answers_layout()
        scroll_area.setWidget(self.answers_container)
        main_layout.addWidget(scroll_area)

        back_button = QPushButton("Back to Home")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #8E44AD;
                color: white;
                font-size: 16px;
                padding: 15px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #9B59B6;
            }
        """)
        back_button.clicked.connect(self.go_back)
        main_layout.addWidget(back_button)

        self.setLayout(main_layout)

    def update_answers_layout(self):
        """Update the layout with public answers."""
        for i in reversed(range(self.answers_layout.count())):
            self.answers_layout.itemAt(i).widget().setParent(None)

        answers = fetch_public_answers(self.prompt)
        for answer in answers:
            user, answer_text, date = answer

            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: #ffffff;
                    border-radius: 10px;
                    padding: 15px;
                    border: 1px solid #bdc3c7;
                }
            """)

            card_layout = QVBoxLayout(card)
            card_layout.setSpacing(10)

            user_label = QLabel(f"👤 {user} - {date}")
            user_label.setStyleSheet("font-size: 14px; color: #7f8c8d;")
            card_layout.addWidget(user_label)

            answer_label = QLabel(answer_text)
            answer_label.setStyleSheet("font-size: 16px; color: #2c3e50;")
            answer_label.setWordWrap(True)
            card_layout.addWidget(answer_label)

            self.answers_layout.addWidget(card)

    def submit_reflection(self):
        answer = self.answer_input.toPlainText()
        if not answer:
            QMessageBox.warning(self, "Error", "Please write your reflection before submitting.")
            return

        is_public = 1 if self.public_radio.isChecked() else 0
        user_id = 1  # Replace with the logged-in user's ID

        save_answer(user_id, self.prompt, answer, is_public)
        self.update_answers_layout()

        QMessageBox.information(self, "Success", "Your reflection has been submitted.")
        self.answer_input.clear()

    def go_back(self):
        """Switch back to the homepage."""
        self.main_app.show_homepage()

# Play ambient music in the background
def play_ambient_music():
    pygame.mixer.music.load("ambient.wav")  # Load the ambient music file
    pygame.mixer.music.play(-1)  # Play in an infinite loop

if __name__ == "__main__":
    create_database()
    insert_dummy_data()

    play_ambient_music()

    app = QApplication(sys.argv)
    window = ReflectionPage(None, None)
    window.show()
    sys.exit(app.exec_())