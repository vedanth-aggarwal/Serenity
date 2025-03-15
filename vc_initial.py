import sys
import os
import threading
import time
import speech_recognition as sr
from openai import OpenAI
from gtts import gTTS
import pygame
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QTextEdit
from PyQt5.QtCore import Qt

# Set your OpenAI API key here
client = OpenAI(api_key="")
# Ambient music file (ensure the file exists and is in .wav format)
AMBIENT_MUSIC = "ambient_music.wav"

class VoiceChatbotApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.ambient_music_playing = False
        self.init_audio()

    def init_ui(self):
        self.setWindowTitle("Mental Health Chatbot")
        self.setGeometry(100, 100, 400, 300)

        # Main layout
        layout = QVBoxLayout()

        # Text display for conversation
        self.conversation_display = QTextEdit()
        self.conversation_display.setReadOnly(True)
        layout.addWidget(self.conversation_display)

        # Start/Stop button
        self.start_stop_button = QPushButton("Start Listening")
        self.start_stop_button.clicked.connect(self.toggle_listening)
        layout.addWidget(self.start_stop_button)

        # Ambient music button
        self.music_button = QPushButton("Play Ambient Music")
        self.music_button.clicked.connect(self.toggle_ambient_music)
        layout.addWidget(self.music_button)

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

    def toggle_listening(self):
        if self.is_listening:
            self.is_listening = False
            self.start_stop_button.setText("Start Listening")
            self.conversation_display.append("Stopped listening.")
        else:
            self.is_listening = True
            self.start_stop_button.setText("Stop Listening")
            self.conversation_display.append("Started listening...")
            threading.Thread(target=self.listen_and_respond, daemon=True).start()

    def toggle_ambient_music(self):
        if self.ambient_music_playing:
            pygame.mixer.music.pause()
            self.music_button.setText("Play Ambient Music")
            self.ambient_music_playing = False
        else:
            pygame.mixer.music.play(-1)  # Loop indefinitely
            self.music_button.setText("Pause Ambient Music")
            self.ambient_music_playing = True

    def listen_and_respond(self):
        while self.is_listening:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
                self.conversation_display.append("Listening...")
                audio = self.recognizer.listen(source)

            try:
                user_input = self.recognizer.recognize_google(audio)
                self.conversation_display.append(f"You: {user_input}")
                response = self.get_chatbot_response(user_input)
                self.conversation_display.append(f"Chatbot: {response}")
                self.play_response(response)
            except sr.UnknownValueError:
                self.conversation_display.append("Sorry, I could not understand the audio.")
            except sr.RequestError:
                self.conversation_display.append("Speech recognition service failed.")

    def get_chatbot_response(self, user_input):
        try:
            completion = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a mental health assistant. Provide supportive and empathetic responses. Make responses brief and deeply connect with individual and engage them with leading questions"},
                    {"role": "user", "content": user_input}
                ]
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            return f"Error: {str(e)}"

    def play_response(self, text):
        tts = gTTS(text=text, lang='en')
        tts.save("response.mp3")
        pygame.mixer.music.load("response.mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VoiceChatbotApp()
    window.show()
    sys.exit(app.exec_())