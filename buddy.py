import sys
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QListWidget, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Database setup
def create_database():
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    bio TEXT NOT NULL,
                    interests TEXT NOT NULL
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS chats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user1_id INTEGER NOT NULL,
                    user2_id INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )''')
    conn.commit()
    conn.close()

# Insert dummy data into the database
def insert_dummy_data():
    users = [
        ("Alice", "I love hiking and reading.", "hiking, reading, yoga"),
        ("Bob", "I enjoy coding and playing guitar.", "coding, music, gaming"),
        ("Charlie", "I'm a foodie and love traveling.", "food, travel, photography"),
        ("Diana", "I'm passionate about fitness and health.", "fitness, health, nutrition"),
        ("Eve", "I love painting and gardening.", "art, gardening, nature")
    ]
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.executemany('''INSERT INTO users (name, bio, interests) VALUES (?, ?, ?)''', users)

    # Insert dummy chat history
    chats = [
        (1, 2, "Hi Bob, how are you?", "2023-10-01 10:00:00"),
        (2, 1, "Hey Alice, I'm good! How about you?", "2023-10-01 10:05:00"),
        (1, 2, "I'm doing great, thanks!", "2023-10-01 10:10:00"),
        (1, 3, "Hi Charlie, what's up?", "2023-10-02 11:00:00"),
        (3, 1, "Not much, just planning my next trip!", "2023-10-02 11:05:00"),
        (1, 4, "Hey Diana, how's your fitness journey going?", "2023-10-03 12:00:00"),
        (4, 1, "It's going great! Just hit a new PR at the gym.", "2023-10-03 12:05:00")
    ]
    c.executemany('''INSERT INTO chats (user1_id, user2_id, message, timestamp)
                     VALUES (?, ?, ?, ?)''', chats)
    conn.commit()
    conn.close()

# Fetch all users except the current user
def fetch_users(current_user_id):
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id != ?", (current_user_id,))
    users = c.fetchall()
    conn.close()
    return users

# Perform similarity search
def find_similar_users(current_user_profile, all_users):
    # Combine bio and interests for similarity calculation
    profiles = [f"{user[2]} {user[3]}" for user in all_users]
    profiles.insert(0, f"{current_user_profile[2]} {current_user_profile[3]}")

    # Use TF-IDF and cosine similarity
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(profiles)
    similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    # Get top 3 similar users
    top_indices = similarities.argsort()[-3:][::-1]
    top_users = [all_users[i] for i in top_indices]
    return top_users

# Fetch chat history between two users
def fetch_chat_history(user1_id, user2_id):
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute('''SELECT * FROM chats WHERE (user1_id = ? AND user2_id = ?) OR (user1_id = ? AND user2_id = ?)
                 ORDER BY timestamp''', (user1_id, user2_id, user2_id, user1_id))
    chat_history = c.fetchall()
    conn.close()
    return chat_history

# Save a new message to the database
def save_message(user1_id, user2_id, message):
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('''INSERT INTO chats (user1_id, user2_id, message, timestamp)
                 VALUES (?, ?, ?, ?)''', (user1_id, user2_id, message, timestamp))
    conn.commit()
    conn.close()

# Main application window
class ChatApp(QMainWindow):
    def __init__(self, stacked_widget, main_app):
        super().__init__()
        self.stacked_widget = stacked_widget  # Store the stacked widget
        self.main_app = main_app  # Store the main application reference
        self.current_user_id = 1  # Replace with the logged-in user's ID
        self.current_user_profile = self.fetch_user_profile(self.current_user_id)
        self.init_ui()

    def fetch_user_profile(self, user_id):
        conn = sqlite3.connect("chat.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        profile = c.fetchone()
        conn.close()
        return profile

    def init_ui(self):
        self.setWindowTitle("Chat with Buddies")
        self.setGeometry(100, 100, 800, 600)

        # Main layout
        main_layout = QHBoxLayout()

        # Left panel for buddy list
        left_panel = QVBoxLayout()
        left_panel.setContentsMargins(10, 10, 10, 10)

        # Title
        title = QLabel("Top 3 Buddies")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #000000;")
        left_panel.addWidget(title)

        # Find similar users
        all_users = fetch_users(self.current_user_id)
        self.similar_users = find_similar_users(self.current_user_profile, all_users)

        # Display top 3 similar users
        self.buddy_list = QListWidget()
        self.buddy_list.setStyleSheet("""
            QListWidget {
                font-size: 16px;
                background-color: #f5f5f5;
                border-radius: 10px;
                padding: 10px;
                color: #000000;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #ddd;
            }
            QListWidget::item:hover {
                background-color: #3498db;
                color: white;
            }
        """)
        for user in self.similar_users:
            self.buddy_list.addItem(f"{user[1]} - {user[3]}")
        left_panel.addWidget(self.buddy_list)

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
        left_panel.addWidget(back_button)

        # Add left panel to main layout
        main_layout.addLayout(left_panel, 1)

        # Right panel for chat interface
        right_panel = QVBoxLayout()
        right_panel.setContentsMargins(10, 10, 10, 10)

        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                font-size: 14px;
                background-color: #ffffff;
                border-radius: 10px;
                padding: 10px;
                color: #000000;
            }
        """)
        right_panel.addWidget(self.chat_display)

        # Message input
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        self.message_input.setStyleSheet("""
            QTextEdit {
                font-size: 14px;
                background-color: #ffffff;
                border-radius: 10px;
                padding: 10px;
                color: #000000;
            }
        """)
        right_panel.addWidget(self.message_input)

        # Send button
        send_button = QPushButton("Send")
        send_button.setStyleSheet("""
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
        send_button.clicked.connect(self.send_message)
        right_panel.addWidget(send_button)

        # Add right panel to main layout
        main_layout.addLayout(right_panel, 2)

        # Set layout
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Connect buddy selection to chat display
        self.buddy_list.itemClicked.connect(self.load_chat_history)

        # Load chat history for the first buddy by default
        if self.similar_users:
            self.buddy_list.setCurrentRow(0)  # Select the first buddy
            self.load_chat_history()

    def load_chat_history(self):
        selected_item = self.buddy_list.currentItem()
        if not selected_item:
            return

        selected_buddy_name = selected_item.text().split(" - ")[0]
        selected_buddy = next(user for user in self.similar_users if user[1] == selected_buddy_name)
        self.selected_buddy_id = selected_buddy[0]

        # Fetch and display chat history
        chat_history = fetch_chat_history(self.current_user_id, self.selected_buddy_id)
        self.chat_display.clear()
        for chat in chat_history:
            sender = "You" if chat[1] == self.current_user_id else selected_buddy_name
            self.chat_display.append(f"{sender}: {chat[3]}\n")

    def send_message(self):
        message = self.message_input.toPlainText()
        if not message:
            QMessageBox.warning(self, "Error", "Please type a message before sending.")
            return

        # Save message to database
        save_message(self.current_user_id, self.selected_buddy_id, message)

        # Update chat display
        self.chat_display.append(f"You: {message}\n")
        self.message_input.clear()

    def go_back(self):
        """Navigate back to the homepage."""
        self.stacked_widget.setCurrentWidget(self.main_app.home_page)

# Main application
if __name__ == "__main__":
    create_database()
    insert_dummy_data()  # Comment this line after first run to avoid duplicate data

    app = QApplication(sys.argv)
    window = ChatApp()
    window.show()
    sys.exit(app.exec_())