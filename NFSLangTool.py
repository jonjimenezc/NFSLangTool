import sys
import ctypes
import winreg
import random
import os
import shutil

from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton,
    QLabel, QMessageBox, QVBoxLayout, QFileDialog
)
from PyQt6.QtCore import Qt, QTimer, QPointF
from PyQt6.QtGui import QPainter, QColor, QFont, QIcon

# ==============================
# ADMIN ELEVATION
# ==============================
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    params = " ".join([f'"{arg}"' for arg in sys.argv])
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, params, None, 1
    )
    sys.exit()

# ==============================
# RESOURCE PATH (EXE SUPPORT)
# ==============================
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ==============================
# REGISTRY FUNCTION
# ==============================
def set_language(language_value):
    try:
        key_path = r"SOFTWARE\WOW6432Node\EA GAMES\Need for Speed Most Wanted"
        key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
        winreg.SetValueEx(
            key,
            "Language",
            0,
            winreg.REG_SZ,
            language_value
        )
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(e)
        return False

# ==============================
# COPY SOUND FILES
# ==============================
def install_sound(folder_name):
    game_path = QFileDialog.getExistingDirectory(
        None,
        "Seleccione la carpeta del juego que contiene speed.exe"
    )
    if not game_path:
        return False

    base_source = resource_path(f"Assets/{folder_name}")
    inner_sound = os.path.join(base_source, "SOUND")

    if os.path.exists(inner_sound):
        source_root = inner_sound
    else:
        source_root = base_source

    if os.path.basename(game_path).upper() == "SOUND":
        target_sound = game_path
    else:
        target_sound = os.path.join(game_path, "SOUND")

    try:
        os.makedirs(target_sound, exist_ok=True)
        for item in os.listdir(target_sound):
            item_path = os.path.join(target_sound, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)

        for item in os.listdir(source_root):
            src = os.path.join(source_root, item)
            dst = os.path.join(target_sound, item)
            if os.path.isdir(src):
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
        return True
    except Exception as e:
        print(e)
        return False

# ==============================
# PARTICLE CLASS
# ==============================
class Particle:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.reset()

    def reset(self):
        self.x = random.randint(0, self.w)
        self.y = random.randint(0, self.h)
        self.dx = random.uniform(-0.15, 0.15)
        self.dy = random.uniform(-0.15, 0.15)
        self.size = random.uniform(1, 2)

    def move(self):
        self.x += self.dx
        self.y += self.dy
        if self.x <= 0 or self.x >= self.w:
            self.dx *= -1
        if self.y <= 0 or self.y >= self.h:
            self.dy *= -1

# ==============================
# MAIN WINDOW
# ==============================
class LangTool(QWidget):
    def __init__(self):
        super().__init__()
        
        # ID para barra de tareas
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("nfs.langtool.1.0")

        self.setWindowTitle("NFS Language Tool")
        self.setFixedSize(760, 520)

        # Icono dinámico
        self.setWindowIcon(QIcon(resource_path("icon.ico")))

        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.CustomizeWindowHint |
            Qt.WindowType.WindowMinimizeButtonHint |
            Qt.WindowType.WindowCloseButtonHint
        )

        self.particles = [
            Particle(self.width(), self.height())
            for _ in range(55)
        ]

        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_main = QFont("Montserrat", 20, QFont.Weight.DemiBold)

        title = QLabel("Change Game Language")
        title.setFont(font_main)
        title.setStyleSheet("color: white;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Cambiar idioma del juego")
        subtitle.setFont(QFont("Montserrat", 14))
        subtitle.setStyleSheet("color: #cfd8dc;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        button_style = """
        QPushButton {
            background-color: #111111;
            color: white;
            border-radius: 14px;
            border: 1px solid #2a2a2a;
            padding: 14px;
            font-size: 15px;
            font-weight: 600;
            min-width: 240px;
        }
        QPushButton:hover {
            background-color: #1c1c1c;
            border: 1px solid #4da3ff;
        }
        QPushButton:pressed {
            background-color: #0a0a0a;
        }
        """

        btn_es = QPushButton("Español")
        btn_es.setStyleSheet(button_style)
        btn_es.clicked.connect(self.set_spanish)

        btn_en = QPushButton("English")
        btn_en.setStyleSheet(button_style)
        btn_en.clicked.connect(self.set_english)

        btn_help = QPushButton("Cómo usar / How to use")
        btn_help.setStyleSheet(button_style)
        btn_help.clicked.connect(self.show_help)

        layout.addWidget(title)
        layout.addSpacing(10)
        layout.addWidget(subtitle)
        layout.addSpacing(40)
        layout.addWidget(btn_es, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(15)
        layout.addWidget(btn_en, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addSpacing(25)
        layout.addWidget(btn_help, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

    def show_help(self):
        text = (
            "INSTRUCCIONES / INSTRUCTIONS\n\n"
            "1. Presione el idioma que desea instalar.\n"
            "2. Busque la carpeta del juego.\n"
            "3. Seleccione la carpeta donde está speed.exe.\n"
            "4. Presione Aceptar.\n\n"
            "1. Press the language you want to install.\n"
            "2. Browse for the game folder.\n"
            "3. Select the folder where speed.exe is located.\n"
            "4. Press OK.\n"
        )
        msg = QMessageBox(self)
        msg.setWindowTitle("Cómo usar / How to use")
        msg.setText(text)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()

    def set_spanish(self):
        reg_ok = set_language("Spanish")
        snd_ok = install_sound("SOUND_ESP")
        if reg_ok and snd_ok:
            self.success_msg("Idioma cambiado correctamente a Español. Gracias por usar esta herramienta.")
        else:
            self.error_msg()

    def set_english(self):
        reg_ok = set_language("English Uk")
        snd_ok = install_sound("SOUND_ENG")
        if reg_ok and snd_ok:
            self.success_msg("Language successfully changed to English. Thank you for using this tool.")
        else:
            self.error_msg()

    def success_msg(self, text):
        msg = QMessageBox(self)
        msg.setWindowTitle("Success")
        msg.setText(text)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()

    def error_msg(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Error")
        msg.setText("No se pudo completar la operación.")
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.exec()

    def animate(self):
        for p in self.particles:
            p.move()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        for y in range(self.height()):
            ratio = y / self.height()
            r = int(2 * (1 - ratio))
            g = int(4 * (1 - ratio))
            b = int(12 + 60 * ratio)
            painter.setPen(QColor(r, g, b))
            painter.drawLine(0, y, self.width(), y)

        painter.setPen(QColor(255, 255, 255))
        for p in self.particles:
            painter.drawEllipse(QPointF(p.x, p.y), p.size, p.size)

# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    if not is_admin():
        run_as_admin()

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path("icon.ico")))

    window = LangTool()
    window.show()
    sys.exit(app.exec())