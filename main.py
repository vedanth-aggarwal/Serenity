import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from loginregister import WelcomePage, LoginWindow, RegisterWindow
from homepage import UserHomePage  # Import the UserHomePage class
from reflection import ReflectionPage  # Import the ReflectionPage class
from voicechatbot import VoiceChatbotApp  # Import the Chatbot class
from tracker import MoodTrackerApp  # Import the MoodTrackerApp class
from textchatbot import ChatbotApp  # Import the ChatbotApp class
from counsellor import CounsellorApp  # Import the CounsellorApp class
from buddy import ChatApp  # Import the ChatApp class

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Serenity - Mental Health App")
        self.setGeometry(100, 100, 800, 600)

        # Create a stacked widget to manage pages
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Initialize pages
        self.welcome_page = WelcomePage(self.stacked_widget, self)
        self.login_window = LoginWindow(self.stacked_widget, self)
        self.register_window = RegisterWindow(self.stacked_widget)
        self.home_page = None
        self.reflection_page = ReflectionPage(self.stacked_widget, self)
        self.chatbot_page = None
        self.mood_tracker_page = None
        self.counsellor_page = None
        self.chat_page = None  # Chat page will be initialized when needed
        self.textbot = None
        # Add pages to the stacked widget
        self.stacked_widget.addWidget(self.welcome_page)
        self.stacked_widget.addWidget(self.login_window)
        self.stacked_widget.addWidget(self.register_window)
        self.stacked_widget.addWidget(self.reflection_page)

        # Start with the welcome page
        self.stacked_widget.setCurrentIndex(0)

    def show_homepage(self, username=None):
        """Switch to the homepage after successful login or from reflection page."""
        if not self.home_page:
            self.home_page = UserHomePage(username, self.stacked_widget, self)
            self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.setCurrentWidget(self.home_page)

    def show_reflection_page(self):
        """Switch to the reflection page."""
        self.stacked_widget.setCurrentWidget(self.reflection_page)

    def show_chatbot_page(self):
        """Switch to the chatbot page."""
        if not self.chatbot_page:
            self.chatbot_page = VoiceChatbotApp(self.stacked_widget, self)
            self.stacked_widget.addWidget(self.chatbot_page)
        self.stacked_widget.setCurrentWidget(self.chatbot_page)

    def show_mood_tracker_page(self):
        """Switch to the mood tracker page."""
        if not self.mood_tracker_page:
            self.mood_tracker_page = MoodTrackerApp(self.stacked_widget, self)
            self.stacked_widget.addWidget(self.mood_tracker_page)
        self.stacked_widget.setCurrentWidget(self.mood_tracker_page)

    def show_counsellor_page(self):
        """Switch to the counsellor page."""
        if not self.counsellor_page:
            self.counsellor_page = CounsellorApp(self.stacked_widget, self)
            self.stacked_widget.addWidget(self.counsellor_page)
        self.stacked_widget.setCurrentWidget(self.counsellor_page)

    def show_chat_page(self):
        """Switch to the chat page."""
        if not self.chat_page:
            self.chat_page = ChatApp(self.stacked_widget, self)
            self.stacked_widget.addWidget(self.chat_page)
        self.stacked_widget.setCurrentWidget(self.chat_page)

    def show_chat_page2(self):
        """Switch to the chat page."""
        if not self.textbot:
            self.textbot = ChatbotApp(self.stacked_widget, self)
            self.stacked_widget.addWidget(self.textbot)
        self.stacked_widget.setCurrentWidget(self.textbot)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())