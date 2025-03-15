import sys
import os
import threading
import time
import speech_recognition as sr
from openai import OpenAI
from gtts import gTTS
import pygame
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QTextEdit
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject

# Suppress macOS secure coding warning
os.environ['QT_MAC_WANTS_LAYER'] = '1'

# Set your OpenAI API key here
client = OpenAI(api_key="")
# Ambient music file (ensure the file exists and is in .wav format)
AMBIENT_MUSIC = "ambient_music.wav"

class Worker(QObject):
    response_signal = pyqtSignal(str)  # Signal to emit chatbot response

    def __init__(self):
        super().__init__()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = True  # Always listening

    def listen_and_respond(self):
        while self.is_listening:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
                self.response_signal.emit("Listening...")
                audio = self.recognizer.listen(source)

            try:
                user_input = self.recognizer.recognize_google(audio)
                self.response_signal.emit(f"You: {user_input}")
                self.process_response(user_input)
            except sr.UnknownValueError:
                self.response_signal.emit("Sorry, I could not understand the audio.")
            except sr.RequestError:
                self.response_signal.emit("Speech recognition service failed.")

    def process_response(self, user_input):
        # Start streaming the OpenAI response
        response_stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a mental health assistant. Provide supportive and empathetic responses. Be concise!"},
                {"role": "user", "content": user_input}
            ],
            stream=True  # Enable streaming
        )

        # Collect the full response
        full_response = ""
        for chunk in response_stream:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content

        # Emit the full response as a single paragraph
        self.response_signal.emit(f"Chatbot: {full_response}")

        # Convert the full response to speech and play it
        self.play_response(full_response)

    def play_response(self, text):
        # Use gTTS to generate audio
        tts = gTTS(text=text, lang='en')
        tts.save("response.mp3")

        # Play the audio using pygame
        pygame.mixer.music.load("response.mp3")
        pygame.mixer.music.play()

        # Wait for the audio to finish playing
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

class VoiceChatbotApp(QMainWindow):
    def __init__(self, stacked_widget, main_app):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.main_app = main_app
        self.init_ui()
        self.ambient_music_playing = False
        self.init_audio()

        # Worker thread for listening and responding
        self.worker = Worker()
        self.worker_thread = threading.Thread(target=self.worker.listen_and_respond, daemon=True)
        self.worker.response_signal.connect(self.update_conversation)

        # Start listening automatically
        self.worker_thread.start()

    def init_ui(self):
        self.setWindowTitle("Mental Health Chatbot")
        self.setGeometry(100, 100, 400, 300)

        # Main layout
        layout = QVBoxLayout()

        # Text display for conversation
        self.conversation_display = QTextEdit()
        self.conversation_display.setReadOnly(True)
        layout.addWidget(self.conversation_display)

        # Ambient music button
        self.music_button = QPushButton("Play Ambient Music")
        self.music_button.clicked.connect(self.toggle_ambient_music)
        layout.addWidget(self.music_button)

        # Back button
        self.back_button = QPushButton("Back to Home")
        self.back_button.clicked.connect(self.go_back)
        layout.addWidget(self.back_button)

        # Set layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def init_audio(self):
        pygame.mixer.init()
        if os.path.exists(AMBIENT_MUSIC):
            pygame.mixer.music.load(AMBIENT_MUSIC)
        else:
            self.conversation_display.append("Warning: Ambient music file not found!")

    def toggle_ambient_music(self):
        if self.ambient_music_playing:
            pygame.mixer.music.pause()
            self.music_button.setText("Play Ambient Music")
            self.ambient_music_playing = False
        else:
            pygame.mixer.music.play(-1)  # Loop indefinitely
            self.music_button.setText("Pause Ambient Music")
            self.ambient_music_playing = True

    def update_conversation(self, text):
        self.conversation_display.append(text)
        self.conversation_display.ensureCursorVisible()  # Auto-scroll

    def go_back(self):
        """Navigate back to the homepage."""
        self.stacked_widget.setCurrentWidget(self.main_app.home_page)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VoiceChatbotApp()
    window.show()
    sys.exit(app.exec_())