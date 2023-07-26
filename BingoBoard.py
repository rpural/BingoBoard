# /usr/bin/env python3
import sys
from PyQt5.QtWidgets import ( QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMainWindow )

from PyQt5.QtCore import Qt

from PyQt5.QtGui import QFont

import datetime

class BingoBoard (QMainWindow):
    def __init__(self):
        self.value_labels = [None,]

        super().__init__()

        self.setWindowTitle("Bingo Board")
        self.resize(self.screen().size())

        lay_rows = QVBoxLayout()
        center = QWidget()
        center.setLayout(lay_rows)
        self.setCentralWidget(center)
        lay_row = QHBoxLayout()
        self.screen_title = QLabel(screen_title_text)
        self.screen_title.setFont(QFont('Times New Roman', 60))
        self.screen_title.setAlignment(Qt.AlignCenter)
        lay_row.addWidget(self.screen_title)
        self.game_title = QLabel(game_title_text)
        self.game_title.setFont(QFont('Arial', 60))
        self.game_title.setAlignment(Qt.AlignCenter)
        lay_row.addWidget(self.game_title)
        lay_rows.addLayout(lay_row)

        for base, row in enumerate(("B", "I", "N", "G", "O")):
            lay_row = QHBoxLayout()
            row_label = QLabel(row)
            row_label.setFont(QFont('Arial', 60))
            row_label.setStyleSheet("border: 2px solid")
            row_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            lay_row.addWidget(row_label)
            for i in range(base*15+1, base*15+16):
                call = QLabel(f"{i:02}")
                call.setFont(QFont('Arial', 60))
                call.setStyleSheet("border: 2px solid")
                call.setAlignment(Qt.AlignVCenter)
                lay_row.addWidget(call)
                self.value_labels.append(call)
            lay_row.setSpacing(10)
            lay_rows.addLayout(lay_row)

        lay_row = QHBoxLayout()
        lay_row.setSpacing(30)
        row_label = QLabel("Currently called:")
        row_label.setFont(QFont('Arial', 60))
        row_label.setAlignment(Qt.AlignRight)
        lay_row.addWidget(row_label)
        self.current_call = QLabel("")
        self.current_call.setFont(QFont('Arial', 60))
        self.current_call.setStyleSheet("border: 2px solid")
        lay_row.addWidget(self.current_call)
        spacer = QLabel("                                              ")
        spacer.setFont(QFont('Arial', 60))
        lay_row.addWidget(spacer)
        lay_row.setSpacing(30)
        lay_rows.addLayout(lay_row)
        lay_rows.setSpacing(30)

        self.show()


class Interactive_Window (QMainWindow):
    calls = {}
    called_numbers = list()
    called_numbers.append(datetime.datetime.now().strftime("%m/%d/%Y-%H:%M"))

    def __init__(self):
        super().__init__()

        for i in range(1,16):
            self.calls[i] = "B"
            self.calls[i+15] = "I"
            self.calls[i+15*2] = "N"
            self.calls[i+15*3] = "G"
            self.calls[i+15*4] = "O"

        window_layout = QVBoxLayout()
        layout = QHBoxLayout()
        prompt = QLabel("Enter game title: ")
        layout.addWidget(prompt)
        self.game_title_entry = QLineEdit()
        self.game_title_entry.setMaxLength(20)
        layout.addWidget(self.game_title_entry)
        self.game_title_commit = QPushButton("Set Title")
        layout.addWidget(self.game_title_commit)
        window_layout.addLayout(layout)
        layout = QHBoxLayout()
        prompt = QLabel("Enter called number: ")
        layout.addWidget(prompt)
        self.call = QLineEdit()
        self.call.setMaxLength(3)
        layout.addWidget(self.call)
        self.commit = QPushButton("Add")
        layout.addWidget(self.commit)
        self.clear = QPushButton("Clear")
        layout.addWidget(self.clear)
        self.exit_program = QPushButton("Exit")
        layout.addWidget(self.exit_program)
        window_layout.addLayout(layout)
        center = QWidget()
        center.setLayout(window_layout)
        self.setCentralWidget(center)

        self.game_title_entry.returnPressed.connect(self.commit_game_title)
        self.game_title_commit.clicked.connect(self.commit_game_title)
        self.call.returnPressed.connect(self.commit_call)
        self.commit.clicked.connect(self.commit_call)
        self.clear.clicked.connect(self.clear_board)
        self.exit_program.clicked.connect(self.done)

        self.show()

    def commit_game_title(self):
        call_value = self.game_title_entry.text()
        self.game_title_entry.setText("")
        window.game_title.setText(call_value)

    def commit_call(self):
        call_value = self.call.text()
        if not call_value.isdigit():
            call_value = call_value[1:]
        if call_value.isdigit():
            call_value = int(call_value)
            if call_value in self.called_numbers:
                window.value_labels[call_value].setStyleSheet("border: 2px solid")
                window.current_call.setText("")
                self.called_numbers.remove(call_value)
            else:
                window.value_labels[call_value].setStyleSheet("color: black; background: white; border: 2px solid")
                window.current_call.setText(self.ball(int(call_value)))
                self.called_numbers.append(call_value)
        self.call.setText("")

    def clear_board(self):
        with open("game.record","a") as record:
            print(self.called_numbers, file=record)
            self.called_numbers = list()
            self.called_numbers.append(datetime.datetime.now().strftime("%m/%d/%Y-%H:%M"))

        for i in range(1, 76):
            window.value_labels[int(i)].setStyleSheet("border: 2px solid")
            window.current_call.setText("")

    def done(self):
        if len(self.called_numbers) > 1:
            with open("game.record","a") as record:
                print(self.called_numbers, file=record)
        exit(0)

    def ball(self, number):
        return f"{self.calls[number]}{number:02}"



if __name__ == '__main__':
    if len(sys.argv) > 1:
        screen_title_text = sys.argv[1]
    else:
        screen_title_text = "Knights of Columbus 3660"
    game_title_text = "Bingo Night"
    app = QApplication([])
    window = BingoBoard()
    interactive = Interactive_Window()

    exit(app.exec())
w()

    exit(app.exec())
