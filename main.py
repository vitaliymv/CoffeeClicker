import sys

from PyQt5.QtCore import QPropertyAnimation, QPoint, Qt, QTimer
from PyQt5.QtWidgets import QLabel, QWidget, QProgressBar, QPushButton, QApplication
import random

class ParticleBurst(QLabel):
    def __init__(self, parent, x, y):
        super().__init__("✨", parent)

        self.setStyleSheet("font-size: 12px;")
        self.move(x, y)
        self.show()

        dx = random.randint(-30, 30)
        dy = random.randint(-60, -20)

        self.anim = QPropertyAnimation(self, b"pos")
        self.anim.setDuration(500)
        self.anim.setStartValue(QPoint(x, y))
        self.anim.setEndValue(QPoint(x + dx, y + dy))
        self.anim.finished.connect(self.deleteLater)
        self.anim.start()

class CoffeeManager(QWidget):
    def __init__(self):
        super().__init__()

        self.money = 0
        self.income_per_click = 1
        self.auto_income = 0

        self.exp = 0
        self.level = 1
        self.exp_to_next = 20

        self.achievements = set()
        self.crystal_active = False
        self.init_ui()

        self.upgrade_click_price = 5
        self.upgrade_auto_price = 10

        self.timer = QTimer()
        self.timer.timeout.connect(self.game_loop)
        self.timer.start(1000)

    def init_ui(self):
        self.setWindowTitle("Coffee Manager Clicker")
        self.setFixedSize(400, 500)

        self.label = QLabel(self)
        self.label.setGeometry(50, 20, 300, 40)
        self.label.setAlignment(Qt.AlignCenter)

        self.progress = QProgressBar(self)
        self.progress.setGeometry(50, 80, 315, 40)

        self.coffee_btn = QPushButton("☕🤎🥯🍪", self)
        self.coffee_btn.setGeometry(50, 150, 100, 60)
        self.coffee_btn.clicked.connect(self.sell_coffee)

        self.upgrade_click_btn = QPushButton("⬆️ click +1", self)
        self.upgrade_click_btn.setGeometry(155, 150, 100, 60)
        self.upgrade_click_btn.clicked.connect(self.upgrade_click)

        self.label_click_price = QLabel(self)
        # self.label_click_price.setText(str(self.upgrade_click_price))
        self.label_click_price.setGeometry(155, 315, 100, 30)

        self.upgrade_auto_btn = QPushButton("🤵🏻 auto +1", self)
        self.upgrade_auto_btn.setGeometry(260, 150, 100, 60)

        self.crystal_btn = QPushButton("💎", self)
        self.crystal_btn.setGeometry(50, 360, 50, 50)
        self.update_ui()

    def update_ui(self):
        self.label.setText(
            f"💰 {self.money} | ☕ {self.income_per_click} | 🤵🏻 {self.auto_income} | ⭐ {self.level}"
        )
        self.progress.setMaximum(self.exp_to_next)
        self.progress.setValue(self.exp)

    def sell_coffee(self):
        self.money += self.income_per_click
        self.add_exp(1)
        for _ in range(6):
            ParticleBurst(self, 75, 155)
        self.update_ui()

    def add_exp(self, amount):
        self.exp += amount
        if self.exp >= self.exp_to_next:
            rem = self.exp - self.exp_to_next
            self.exp = rem
            self.level += 1
            self.exp_to_next += 10
            self.income_per_click += 1

    def game_loop(self):
        self.money += self.auto_income
        if self.auto_income > 0:
            self.add_exp(1)
        self.update_ui()

    def upgrade_click(self):
        if self.money >= self.upgrade_click_price:
            self.money -= self.upgrade_click_btn
            self.income_per_click += 1
            self.upgrade_click_price *= 1.3
            self.upgrade_click_price = round(self.upgrade_click_price)

app = QApplication(sys.argv)
window = CoffeeManager()
window.show()
sys.exit(app.exec_())

# tooltip for label, tooltip for button