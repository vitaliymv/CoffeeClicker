import json
import sys
from PyQt5.QtCore import QPropertyAnimation, QPoint, Qt, QTimer
from PyQt5.QtWidgets import QLabel, QWidget, QProgressBar, QPushButton, QApplication, QMessageBox, QListWidget
import random
from storage import save_to_file, load_from_file

ACHIEVEMENTS_FILE = "achievements.json"

class AchievementsWindow(QWidget):
    def __init__(self, achievements_data):
        super().__init__()
        self.setWindowTitle("Achievements")
        self.setFixedSize(400, 400)
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e2f;
                color: white;
                font-size: 15px;
            }
            QListWidget {
                background-color: #2a2a40;
                border-radius: 10px;
                padding: 5px
            }            
        """)
        self.list_widget = QListWidget(self)
        self.list_widget.setGeometry(10, 10, 390, 390)
        for name, status in achievements_data.items():
            icon = "✅" if status else "❌"
            self.list_widget.addItem(f"{icon} {name}")

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
        self.auto_speed = 1000

        self.exp = 0
        self.level = 1
        self.exp_to_next = 20
        self.upgrade_click_price = 5
        self.upgrade_auto_price = 10
        self.upgrade_speed_price = 50

        if save:
            self.money = save["money"]
            self.income_per_click = save["income_per_click"]
            self.auto_income = save["auto_income"]
            self.exp = save["exp"]
            self.level = save["level"]
            self.exp_to_next = save["exp_to_next"]
            self.upgrade_click_price = save["upgrade_click_price"]
            self.upgrade_auto_price = save["upgrade_auto_price"]
            self.upgrade_speed_price = save["upgrade_speed_price"]
            self.auto_speed = save["auto_speed"]

        self.achievements = {
            "Earn 50 money": False,
            "Earn 100 money": False,
            "Earn 500 money": False,
            "Level 5": False,
            "Level 10": False,
            "Level 15": False,
            "10 click power": False,
            "25 click power": False,
            "50 click power": False,
            "Buy auto income": False,
            "Buy 5 auto income": False,
            "Buy 10 auto income": False,
        }
        self.load_achievements()
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
        self.timer.start(self.auto_speed)

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
                "upgrade_speed_price": self.upgrade_speed_price,
                "auto_speed": self.auto_speed
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
        self.setFixedSize(500, 500)

        self.label = QLabel(self)
        self.label.setGeometry(50, 20, 400, 40)
        self.label.setAlignment(Qt.AlignCenter)

        self.ac_btn = QPushButton("🏆", self)
        self.ac_btn.setGeometry(10, 10, 50, 50)
        self.ac_btn.clicked.connect(self.open_achievements)

        self.progress = QProgressBar(self)
        self.progress.setGeometry(50, 80, 450, 40)

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

        self.upgrade_auto_speed_btn = QPushButton("⚡️auto", self)
        self.upgrade_auto_speed_btn.setGeometry(370, 150, 100, 60)
        self.upgrade_auto_speed_btn.clicked.connect(self.upgrade_speed)

        self.label_speed_price = QLabel(self)
        self.label_speed_price.setGeometry(370, 220, 100, 30)
        self.label_speed_price.setAlignment(Qt.AlignCenter)
        self.label_speed_price.setText(str(self.upgrade_speed_price))

        self.crystal_btn = QPushButton("💎", self)
        self.crystal_btn.setGeometry(50, 360, 50, 50)
        self.crystal_btn.clicked.connect(self.collect_crystal)
        self.crystal_btn.hide()
        self.update_ui()

    def upgrade_speed(self):
        if self.money >= self.upgrade_speed_price and self.auto_speed >= 100:
            self.money -= self.upgrade_speed_price
            self.auto_speed -= 20
            self.upgrade_speed_price *= 1.3
            self.upgrade_speed_price = round(self.upgrade_speed_price)
            self.update_ui()

    def update_ui(self):
        self.label.setText(
            f"💰 {self.money} | ☕ {self.income_per_click} | 🤵🏻 {self.auto_income} | ⭐ {self.level} | ⚡️ {self.auto_speed}"
        )
        self.progress.setMaximum(self.exp_to_next)
        self.progress.setValue(self.exp)
        self.label_click_price.setText(str(self.upgrade_click_price))
        self.label_auto_price.setText(str(self.upgrade_auto_price))
        self.label_speed_price.setText(str(self.upgrade_speed_price))

        if self.level < 3:
            self.upgrade_click_btn.setEnabled(False)
            self.upgrade_click_btn.setText("From Lv.3")
        else:
            self.upgrade_click_btn.setEnabled(True)
            self.upgrade_click_btn.setText("⬆️ click +1")

        if self.level < 5:
            self.upgrade_auto_btn.setEnabled(False)
            self.upgrade_auto_btn.setText("From Lv.5")
        else:
            self.upgrade_auto_btn.setEnabled(True)
            self.upgrade_auto_btn.setText("🤵🏻 auto +1")

        if self.level < 7:
            self.upgrade_auto_speed_btn.setEnabled(False)
            self.upgrade_auto_speed_btn.setText("From Lv.7")
        else:
            self.upgrade_auto_speed_btn.setEnabled(True)
            self.upgrade_auto_speed_btn.setText("⚡️auto")

        if self.auto_speed <= 100:
            self.upgrade_auto_speed_btn.setEnabled(False)
            self.label_speed_price.setText("MAX")

    def sell_coffee(self):
        self.money += self.income_per_click
        self.add_exp(1)
        for _ in range(6):
            ParticleBurst(self, self.coffee_btn.x() + 40, self.coffee_btn.y() + 20)
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
        self.check_achievements()

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
            self.upgrade_auto_price = round(self.upgrade_auto_price)
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

    def load_achievements(self):
        try:
            with open(ACHIEVEMENTS_FILE, "r") as file:
                self.achievements = json.load(file)
        except FileNotFoundError:
            return

    def save_achievements(self):
        with open(ACHIEVEMENTS_FILE, "w") as file:
            json.dump(self.achievements, file, indent=4)

    def open_achievements(self):
        self.ac_window = AchievementsWindow(self.achievements)
        self.ac_window.show()

    def unlock(self, name):
        if self.achievements[name]:
            return

        self.achievements[name] = True
        self.save_achievements()
        label = QLabel(f"🏅 {name} taken", self)
        label.adjustSize()
        label.move(150, 300)
        label.show()
        QTimer.singleShot(2000, label.deleteLater)

    def check_achievements(self):
        if self.money >= 50:
            self.unlock("Earn 50 money")
        if self.money >= 100:
            self.unlock("Earn 100 money")
        if self.money >= 500:
            self.unlock("Earn 500 money")
        if self.level >= 5:
            self.unlock("Level 5")
        if self.level >= 10:
            self.unlock("Level 10")
        if self.level >= 15:
            self.unlock("Level 15")
        if self.income_per_click >= 10:
            self.unlock("10 click power")
        if self.income_per_click >= 25:
            self.unlock("25 click power")
        if self.income_per_click >= 50:
            self.unlock("50 click power")
        if self.auto_income >= 1:
            self.unlock("Buy auto income")
        if self.auto_income >= 5:
            self.unlock("Buy 5 auto income")
        if self.auto_income >= 10:
            self.unlock("Buy 10 auto income")

app = QApplication(sys.argv)
window = CoffeeManager()
window.show()
sys.exit(app.exec_())
