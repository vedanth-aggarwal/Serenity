import sys
import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QSlider, QMessageBox
)
from PyQt5.QtCore import Qt

# Database setup
def create_database():
    conn = sqlite3.connect("mood_tracker.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS mood_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    mood_score INTEGER NOT NULL,
                    stress_score INTEGER NOT NULL,
                    energy_score INTEGER NOT NULL
                )''')
    conn.commit()
    conn.close()

# Insert dummy data with steady trends
def insert_dummy_data():
    conn = sqlite3.connect("mood_tracker.db")
    c = conn.cursor()
    for i in range(15):  # Last 15 days
        date = (datetime.now() - timedelta(days=14 - i)).strftime("%Y-%m-%d")  # Ensure dates are in order
        mood_score = min(10, max(1, 5 + i))  # Steady increase in mood
        stress_score = min(10, max(1, 8 - i))  # Steady decrease in stress
        energy_score = min(10, max(1, 4 + i))  # Steady increase in energy
        c.execute('''INSERT INTO mood_scores (user_id, date, mood_score, stress_score, energy_score)
                     VALUES (?, ?, ?, ?, ?)''', (1, date, mood_score, stress_score, energy_score))
    conn.commit()
    conn.close()

# Fetch mood scores for the last 15 days
def fetch_mood_scores(user_id):
    conn = sqlite3.connect("mood_tracker.db")
    c = conn.cursor()
    c.execute("SELECT date, mood_score, stress_score, energy_score FROM mood_scores WHERE user_id = ? ORDER BY date ASC LIMIT 15", (user_id,))
    scores = c.fetchall()
    conn.close()
    return scores

# Save a new mood score to the database
def save_mood_score(user_id, mood_score, stress_score, energy_score):
    conn = sqlite3.connect("mood_tracker.db")
    c = conn.cursor()
    date = datetime.now().strftime("%Y-%m-%d")
    c.execute('''INSERT INTO mood_scores (user_id, date, mood_score, stress_score, energy_score)
                 VALUES (?, ?, ?, ?, ?)''', (user_id, date, mood_score, stress_score, energy_score))
    conn.commit()
    conn.close()

# Plot mood scores
def plot_mood_scores(scores):
    dates = [score[0] for score in scores]
    mood_scores = [score[1] for score in scores]
    stress_scores = [score[2] for score in scores]
    energy_scores = [score[3] for score in scores]

    plt.figure(figsize=(10, 6))
    plt.plot(dates, mood_scores, label="Mood", marker='o', color='blue')
    plt.plot(dates, stress_scores, label="Stress", marker='o', color='red')
    plt.plot(dates, energy_scores, label="Energy", marker='o', color='green')
    plt.xlabel("Date")
    plt.ylabel("Score (1-10)")
    plt.title("Mood, Stress, and Energy Scores Over Last 15 Days")
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Main application window
class MoodTrackerApp(QMainWindow):
    def __init__(self, stacked_widget, main_app):
        super().__init__()
        self.stacked_widget = stacked_widget  # Store the stacked widget
        self.main_app = main_app  # Store the main application reference
        create_database()
        insert_dummy_data()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Mood Tracker")
        self.setGeometry(100, 100, 600, 500)
        self.setStyleSheet("background-color: #f0f4f8; color: #2c3e50;")

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Mood Tracker")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        main_layout.addWidget(title)

        # Questions and sliders
        self.questions = [
            "How would you rate your overall mood today?",
            "How would you rate your stress level today?",
            "How would you rate your energy level today?"
        ]

        self.sliders = []
        self.value_labels = []  # To store the labels displaying slider values
        for i, question in enumerate(self.questions):
            question_label = QLabel(question)
            question_label.setStyleSheet("font-size: 16px; color: #34495e;")
            main_layout.addWidget(question_label)

            # Label to display the slider value
            value_label = QLabel("5")  # Default value
            value_label.setAlignment(Qt.AlignCenter)
            value_label.setStyleSheet("font-size: 14px; color: #2c3e50;")
            main_layout.addWidget(value_label)
            self.value_labels.append(value_label)

            # Slider
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(1)
            slider.setMaximum(10)
            slider.setValue(5)
            slider.setTickPosition(QSlider.TicksBelow)
            slider.setTickInterval(1)
            slider.setStyleSheet("""
                QSlider::groove:horizontal {
                    background: #bdc3c7;
                    height: 8px;
                    border-radius: 4px;
                }
                QSlider::handle:horizontal {
                    background: #3498db;
                    width: 20px;
                    height: 20px;
                    margin: -6px 0;
                    border-radius: 10px;
                }
            """)
            slider.valueChanged.connect(lambda value, idx=i: self.update_slider_value(idx, value))
            self.sliders.append(slider)
            main_layout.addWidget(slider)

        # Submit button
        submit_button = QPushButton("Submit Scores")
        submit_button.setStyleSheet("""
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
        submit_button.clicked.connect(self.submit_scores)
        main_layout.addWidget(submit_button)

        # Plot button
        plot_button = QPushButton("Plot Mood Scores")
        plot_button.setStyleSheet("""
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
        plot_button.clicked.connect(self.plot_scores)
        main_layout.addWidget(plot_button)

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

    def update_slider_value(self, index, value):
        """Update the label above the slider with the current value."""
        self.value_labels[index].setText(str(value))

    def submit_scores(self):
        scores = [slider.value() for slider in self.sliders]
        user_id = 1  # Replace with the logged-in user's ID

        # Save scores to database
        save_mood_score(user_id, scores[0], scores[1], scores[2])

        QMessageBox.information(self, "Success", "Your mood scores have been submitted.")

    def plot_scores(self):
        user_id = 1  # Replace with the logged-in user's ID
        scores = fetch_mood_scores(user_id)
        if not scores:
            QMessageBox.warning(self, "Error", "No mood scores found.")
            return
        plot_mood_scores(scores)

    def go_back(self):
        """Navigate back to the homepage."""
        self.stacked_widget.setCurrentWidget(self.main_app.home_page)

# Main application
if __name__ == "__main__":
    create_database()
    insert_dummy_data()  # Comment this line after first run to avoid duplicate data

    app = QApplication(sys.argv)
    window = MoodTrackerApp(None, None)
    window.show()
    sys.exit(app.exec_())