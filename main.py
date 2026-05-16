import sys
from PyQt5.QtCore import QPropertyAnimation, QPoint, Qt, QTimer
from PyQt5.QtWidgets import QLabel, QWidget, QProgressBar, QPushButton, QApplication, QMessageBox
import random
from storage import save_to_file, load_from_file

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
        save = load_from_file()
        self.money = 0
        self.income_per_click = 1
        self.auto_income = 0

        self.exp = 0
        self.level = 1
        self.exp_to_next = 20
        self.upgrade_click_price = 5
        self.upgrade_auto_price = 10

        if save:
            self.money = save["money"]
            self.income_per_click = save["income_per_click"]
            self.auto_income = save["auto_income"]
            self.exp = save["exp"]
            self.level = save["level"]
            self.exp_to_next = save["exp_to_next"]
            self.upgrade_click_price = save["upgrade_click_price"]
            self.upgrade_auto_price = save["upgrade_auto_price"]


        self.achievements = set()
        self.crystal_active = False
        self.init_ui()
        self.update_ui()
        self.crystal_dx = 4
        self.crystal_dy = 4
        self.crystal_move_timer = QTimer()
        self.crystal_move_timer.timeout.connect(self.move_crystal)

        self.crystal_timer = QTimer()
        self.crystal_timer.timeout.connect(self.spawn_crystal)
        self.crystal_timer.start(3000)

        self.timer = QTimer()
        self.timer.timeout.connect(self.game_loop)
        self.timer.start(1000)

    def closeEvent(self, a0):
        question = QMessageBox.question(
            self,
            "Message",
            "Are you sure to quit?",
            (QMessageBox.Yes | QMessageBox.No)
        )
        if question == QMessageBox.Yes:
            a0.accept()
            save = {
                "money": self.money,
                "income_per_click": self.income_per_click,
                "auto_income": self.auto_income,
                "exp": self.exp,
                "level": self.level,
                "exp_to_next": self.exp_to_next,
                "upgrade_click_price": self.upgrade_click_price,
                "upgrade_auto_price": self.upgrade_auto_price,
            }
            save_to_file(save)
        else:
            a0.ignore()


    def init_ui(self):
        self.setStyleSheet("""
            QWidget { background-color: #1e1e2f; color: white; font-size: 15px }
            QPushButton {
                background-color: #3a3a5f;
                border-radius: 12px;
                padding: 10px;
                font-size: 15px;
            }
            QPushButton:hover { background-color: #50507a; }
        """)
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
        self.label_click_price.setText(str(self.upgrade_click_price))
        self.label_click_price.setGeometry(155, 220, 100, 30)
        self.label_click_price.setAlignment(Qt.AlignCenter)

        self.label_auto_price = QLabel(self)
        self.label_auto_price.setText(str(self.upgrade_auto_price))
        self.label_auto_price.setGeometry(260, 220, 100, 30)
        self.label_auto_price.setAlignment(Qt.AlignCenter)

        self.upgrade_auto_btn = QPushButton("🤵🏻 auto +1", self)
        self.upgrade_auto_btn.setGeometry(260, 150, 100, 60)
        self.upgrade_auto_btn.clicked.connect(self.upgrade_auto)

        self.crystal_btn = QPushButton("💎", self)
        self.crystal_btn.setGeometry(50, 360, 50, 50)
        self.crystal_btn.clicked.connect(self.collect_crystal)
        self.crystal_btn.hide()
        self.update_ui()

    def update_ui(self):
        self.label.setText(
            f"💰 {self.money} | ☕ {self.income_per_click} | 🤵🏻 {self.auto_income} | ⭐ {self.level}"
        )
        self.progress.setMaximum(self.exp_to_next)
        self.progress.setValue(self.exp)
        self.label_click_price.setText(str(self.upgrade_click_price))
        self.label_auto_price.setText(str(self.upgrade_auto_price))

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
            self.money -= self.upgrade_click_price
            self.income_per_click += 1
            self.upgrade_click_price *= 1.3
            self.upgrade_click_price = round(self.upgrade_click_price)
            self.update_ui()

    def upgrade_auto(self):
        if self.money >= self.upgrade_auto_price:
            self.money -= self.upgrade_auto_price
            self.auto_income += 1
            self.upgrade_auto_price *= 1.3
            self.upgrade_auto_price = round(self.upgrade_click_price)
            self.update_ui()

    def hide_crystal(self):
        self.crystal_btn.hide()
        self.crystal_active = False
        self.crystal_move_timer.stop()

    def spawn_crystal(self):
        if not self.crystal_active and random.randint(1, 5) == 1:
            self.crystal_active = True

            x = random.randint(50, 350)
            y = random.randint(220, 450)
            self.crystal_btn.move(x, y)
            self.crystal_btn.show()

            self.crystal_dx = random.choice([-3, -2, 2, 3])
            self.crystal_dy = random.choice([-3, -2, 2, 3])
            self.crystal_move_timer.start(16)
            QTimer.singleShot(10000, self.hide_crystal)

    def move_crystal(self):
        if not self.crystal_active:
            return
        x = self.crystal_btn.x()
        y = self.crystal_btn.y()
        new_x = x + self.crystal_dx
        new_y = y + self.crystal_dy

        left = 0
        right = self.width() - self.crystal_btn.width()

        top = 220
        bottom = self.height() - self.crystal_btn.height()

        if new_x <= left or new_x >= right:
            self.crystal_dx *= -1
        if new_y <= top or new_y >= bottom:
            self.crystal_dy *= -1

        self.crystal_dx = max(-10, min(10, self.crystal_dx))
        self.crystal_dy = max(-10, min(10, self.crystal_dy))

        self.crystal_btn.move(x + self.crystal_dx, y + self.crystal_dy)

    def collect_crystal(self):
        self.money += random.randint(20, 50)
        for _ in range(20):
            ParticleBurst(self, self.crystal_btn.x(), self.crystal_btn.y())
        self.hide_crystal()
        self.update_ui()

app = QApplication(sys.argv)
window = CoffeeManager()
window.show()
sys.exit(app.exec_())

# tooltip for label, tooltip for button