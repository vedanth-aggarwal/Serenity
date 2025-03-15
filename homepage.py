import sys
import sqlite3
import requests
import random
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QGridLayout, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt

# Function to Fetch Mental Health Quotes from ZenQuotes API
def get_quote():
    try:
        response = requests.get("https://zenquotes.io/api/random", timeout=5)
        response.raise_for_status()
        quote_data = response.json()
        return quote_data[0]['q']  # Extracting the quote text
    except requests.RequestException as e:
        print(f"Error fetching quote: {e}")
        return "Take time to do what makes your soul happy."  # Default quote if API fails

def get_quote2(keyword="strength"):
    """
    Fetches a random Stoic quote related to the given keyword (e.g., "strength").
    """
    try:
        # Make a GET request to the Stoicism Quote API
        response = requests.get(f"https://stoicismquote.com/api/v1/quote/search?keyword={keyword}", timeout=5)
        response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)

        # Parse the JSON response
        quote_data = response.json()

        # Extract the list of quotes
        quotes = quote_data.get("quotes", [])

        if not quotes:
            return "No quotes found. Take time to do what makes your soul happy."

        # Select a random quote from the list
        random_quote = random.choice(quotes)
        return random_quote["quote"]

    except requests.RequestException as e:
        print(f"Error fetching quote: {e}")
        return "Take time to do what makes your soul happy."  # Default quote if API fails
    
class UserHomePage(QWidget):
    def __init__(self, username, stacked_widget, main_app):
        super().__init__()
        self.setWindowTitle("Serenity - Home")
        self.setGeometry(300, 100, 800, 600)
        self.setStyleSheet("""
            background-color: #f0f4f8;
            color: #2c3e50;
        """)
        self.stacked_widget = stacked_widget
        self.main_app = main_app  # Reference to the main application
        self.username = username

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Welcome Label
        welcome_label = QLabel(f"Welcome, {self.username}!")
        welcome_label.setFont(QFont("Arial", 28, QFont.Bold))
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("color: #2c3e50;")
        main_layout.addWidget(welcome_label)

        # Quote Label
        self.quote_label = QLabel(get_quote())
        self.quote_label.setFont(QFont("Arial", 16))
        self.quote_label.setWordWrap(True)
        self.quote_label.setAlignment(Qt.AlignCenter)
        self.quote_label.setStyleSheet("""
            background-color: #ffffff;
            padding: 20px;
            border-radius: 10px;
            color: #2c3e50;
            font-style: italic;
        """)
        main_layout.addWidget(self.quote_label)

        # Buttons Grid Layout
        buttons_layout = QGridLayout()
        buttons_layout.setSpacing(15)

        # New Quote Button
        self.new_quote_btn = QPushButton("New Quote")
        self.new_quote_btn.setFont(QFont("Arial", 14))
        self.new_quote_btn.setStyleSheet("""
            QPushButton {
                background-color: #8E44AD;
                color: white;
                padding: 15px;
                border-radius: 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #7d3c98;
            }
        """)
        self.new_quote_btn.clicked.connect(self.update_quote)
        buttons_layout.addWidget(self.new_quote_btn, 0, 0)

        # Reflection Button
        self.reflection_btn = QPushButton("Daily Reflection")
        self.reflection_btn.setFont(QFont("Arial", 14))
        self.reflection_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 15px;
                border-radius: 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.reflection_btn.clicked.connect(self.main_app.show_reflection_page)
        buttons_layout.addWidget(self.reflection_btn, 0, 1)

        # Chatbot Button
        self.chatbot_btn = QPushButton("AI Companion")
        self.chatbot_btn.setFont(QFont("Arial", 14))
        self.chatbot_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 15px;
                border-radius: 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.chatbot_btn.clicked.connect(self.main_app.show_chatbot_page)
        buttons_layout.addWidget(self.chatbot_btn, 1, 0)

        # Mood Tracker Button
        self.mood_tracker_btn = QPushButton("Mood Tracker")
        self.mood_tracker_btn.setFont(QFont("Arial", 14))
        self.mood_tracker_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                padding: 15px;
                border-radius: 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        self.mood_tracker_btn.clicked.connect(self.main_app.show_mood_tracker_page)
        buttons_layout.addWidget(self.mood_tracker_btn, 1, 1)

        # Find a Counsellor Button
        self.counsellor_btn = QPushButton("Find a Counsellor")
        self.counsellor_btn.setFont(QFont("Arial", 14))
        self.counsellor_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                padding: 15px;
                border-radius: 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        self.counsellor_btn.clicked.connect(self.main_app.show_counsellor_page)
        buttons_layout.addWidget(self.counsellor_btn, 2, 0)

        # Chat with Buddies Button
        self.chat_btn = QPushButton("Chat with Buddies")
        self.chat_btn.setFont(QFont("Arial", 14))
        self.chat_btn.setStyleSheet("""
            QPushButton {
                background-color: #1abc9c;
                color: white;
                padding: 15px;
                border-radius: 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #16a085;
            }
        """)
        self.chat_btn.clicked.connect(self.main_app.show_chat_page)
        buttons_layout.addWidget(self.chat_btn, 2, 1)

        self.textchat_btn = QPushButton("GUIDANCE BOT")
        self.textchat_btn.setFont(QFont("Arial", 14))
        self.textchat_btn.setStyleSheet("""
            QPushButton {
                background-color: #1abc9c;
                color: white;
                padding: 15px;
                border-radius: 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #16a085;
            }
        """)
        self.textchat_btn.clicked.connect(self.main_app.show_chat_page2)
        buttons_layout.addWidget(self.textchat_btn, 3, 1)

        main_layout.addLayout(buttons_layout)

        # Add the header image below the buttons
        header_label = QLabel(self)
        header_pixmap = QPixmap("header.png")  # Load the image
        if not header_pixmap.isNull():
            # Scale the image to fit the width of the window and increase height
            header_label.setPixmap(header_pixmap.scaled(self.width(), 300, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
            header_label.setAlignment(Qt.AlignCenter)
            header_label.setStyleSheet("margin: 0; padding: 0;")  # Remove any default margins or padding
            main_layout.addWidget(header_label)
        
        # Add spacer to push everything to the top
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        main_layout.addItem(spacer)

        self.setLayout(main_layout)

    def update_quote(self):
        new_quote = get_quote()
        self.quote_label.setText(new_quote)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UserHomePage("TestUser", None, None)
    window.show()
    sys.exit(app.exec_())