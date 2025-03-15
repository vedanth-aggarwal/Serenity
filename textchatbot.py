import sys, re
from openai import OpenAI
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLineEdit,
                             QPushButton, QVBoxLayout, QWidget, QLabel,
                             QScrollArea, QSizePolicy, QHBoxLayout)
client = OpenAI(api_key="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")

class ChatBubble(QWidget):
    def __init__(self, text, is_user, title):
        super().__init__()
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Maximum)

        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel(title)
        title_label.setObjectName("title")

        bubble_layout = QHBoxLayout()
        bubble_layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel()
        label.setText(text)
        label.setWordWrap(True)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        label.setTextFormat(Qt.RichText)  # Enable HTML formatting

        # Set the user or bot bubble colors
        if is_user:
            label.setObjectName("user-bubble")
            # Set user bubble styles
            label.setStyleSheet(f"""
                QLabel#user-bubble {{
                    background-color: white; 
                    color: #333333; 
                    border: 1px solid #FFFFFF;
                    border-radius: 15px; 
                    padding: 10px;
                }}
            """)
        else:
            label.setObjectName("bot-bubble")
            # Set bot bubble styles
            label.setStyleSheet(f"""
                QLabel#bot-bubble {{
                    background-color: #E8D8FF;
                    color: #5E2D91; 
                    border: 1px solid #E8D8FF; 
                    border-radius: 15px; 
                    padding: 10px;
                }}
            """)

        if is_user:
            title_label.setAlignment(Qt.AlignRight)
            outer_layout.addWidget(title_label)
            bubble_layout.addStretch()
            bubble_layout.addWidget(label)
        else:
            outer_layout.addWidget(title_label)
            bubble_layout.addWidget(label)
            bubble_layout.addStretch()

        outer_layout.addLayout(bubble_layout)
        self.setLayout(outer_layout)

class ChatbotApp(QMainWindow):
    def __init__(self, stacked_widget, main_app):
        super().__init__()
        self.stacked_widget = stacked_widget  # Store the stacked widget
        self.main_app = main_app  # Store the main application reference
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Chatbot UI")
        self.setGeometry(100, 100, 800, 600)

        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        # Chat display box with scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.addStretch()  # Ensure correct stretch behavior
        self.scroll_area.setWidget(self.chat_widget)

        layout.addWidget(self.scroll_area)

        # Input and send button layout
        input_layout = QHBoxLayout()
        self.text_input = QLineEdit(self)
        self.text_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.text_input)

        send_button = QPushButton("Send", self)
        send_button.clicked.connect(self.send_message)
        input_layout.addWidget(send_button)
        layout.addLayout(input_layout)

        # Back button
        back_button = QPushButton("Back to Home", self)
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
        layout.addWidget(back_button)

        central_widget.setLayout(layout)

        # Load stylesheet
        self.load_stylesheet()

    def load_stylesheet(self):
        with open('styles.qss', 'r') as file:
            stylesheet = file.read()
        self.setStyleSheet(stylesheet)

    def send_message(self):
        user_input = self.text_input.text().strip()

        if user_input:
            # u_msg is user_message
            u_msg = ChatBubble(f"{user_input}", True, "You")
            self.chat_layout.insertWidget(self.chat_layout.count() - 1, u_msg)

            try:
                completion = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a mental health assistant. Provide supportive and empathetic responses. Make responses brief and deeply connect with individual and engage them with leading questions"},
                        {"role": "user", "content": user_input}
                    ]
                )
                bot_response = completion.choices[0].message.content.strip()
            except Exception as e:
                bot_response = f"Error: {str(e)}"

            # Convert bot response to HTML (handle bold, italic, and underline)
            formatted_response = self.convert_markdown_to_html(bot_response)

            # Display bot message after user message
            ai_msg = ChatBubble(f"{formatted_response}", False, "AI")
            self.chat_layout.insertWidget(self.chat_layout.count() - 1, ai_msg)

            # Clear the input
            self.text_input.clear()

            # Scroll to the bottom of the chat
            v_scroll = self.scroll_area.verticalScrollBar()
            QtCore.QTimer.singleShot(100, lambda: v_scroll.setValue(v_scroll.maximum()))

    def convert_markdown_to_html(self, text):
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)  # Bold
        text = re.sub(r'__(.*?)__', r'<i>\1</i>', text)      # Italic
        text = re.sub(r'\*(.*?)\*', r'<u>\1</u>', text)      # Underline
        text = text.replace("\n", "<br>")                   # New line
        return text

    def go_back(self):
        """Navigate back to the homepage."""
        self.stacked_widget.setCurrentWidget(self.main_app.home_page)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    chatbot_app = ChatbotApp(None, None)
    chatbot_app.show()
    sys.exit(app.exec_())