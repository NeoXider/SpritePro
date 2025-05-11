# создай приложение для запоминания информации
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QGroupBox,
    QRadioButton,
)

app = QApplication([])
main_win = QWidget()
main_win.setWindowTitle("Memory Card")
lv_main = QVBoxLayout()

question = QLabel("Какой национальности не существует?")

group_answer = QGroupBox("Варианты ответов")

rb_1 = QRadioButton("Энцы")
rb_2 = QRadioButton("Смурфы")
rb_3 = QRadioButton("Чулымцы")
rb_4 = QRadioButton("Алеуты")

lv_btns_main = QVBoxLayout()
lh_btns = QHBoxLayout()
lh_btns = QHBoxLayout()

lh_btns.addWidget(rb_1)
lh_btns.addWidget(rb_2)
lh_btns.addWidget(rb_3)
lh_btns.addWidget(rb_4)

lv_btns_main.addLayout(lh_btns)
lv_btns_main.addLayout(lh_btns)

group_answer.setLayout(lv_btns_main)
lv_main.addWidget(question, alignment=Qt.AlignCenter)
lv_main.addWidget(group_answer, alignment=Qt.AlignCenter)
main_win.setLayout(lv_main)
main_win.show()
app.exec()
