#! /usr/bin/env python3
import sys
from PyQt5.QtWidgets import ( QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QHBoxLayout,
    QMainWindow )

from PyQt5.QtCore import Qt, QTimer

from PyQt5.QtGui import QFont

import datetime

import argparse

import bingogame # local to project

BingoBoard_version = "4.0"

class BingoWindow (QMainWindow):
    def __init__(self, automatic=False):
        self.value_labels = [None,]
        self.called_numbers = list()

        self.calls = {}
        for i in range(1,16):
            self.calls[i] = "B"
            self.calls[i+15] = "I"
            self.calls[i+15*2] = "N"
            self.calls[i+15*3] = "G"
            self.calls[i+15*4] = "O"


        super().__init__()

        print(f"automatic = {automatic}")

        self.setWindowTitle("Bingo")
        self.resize(self.screen().size())

        lay_rows = QVBoxLayout()
        center = QWidget()
        center.setLayout(lay_rows)
        self.setCentralWidget(center)
        lay_row = QHBoxLayout()

        # Event / organization title at top of screen
        self.screen_title = QLabel(screen_title_text)
        self.screen_title.setFont(QFont('Times New Roman', 60))
        self.screen_title.setAlignment(Qt.AlignCenter)
        lay_row.addWidget(self.screen_title)

        # Currently called number at top of screen
        self.current_call = QLabel("")
        self.current_call.setFixedWidth(280)
        self.current_call.setFont(QFont('Times New Roman', 128))
        self.current_call.setAlignment(Qt.AlignCenter)
        self.current_call.setStyleSheet("color: black ; background-color: silver ; border-color: black ; border-radius: 8 ; border: 8px ridge")
        lay_row.addWidget(self.current_call)
        lay_rows.addLayout(lay_row)

        for base, row in enumerate(("B", "I", "N", "G", "O")):
            lay_row = QHBoxLayout()
            row_label = QLabel(row)
            row_label.setFont(QFont('Arial', 60))
            row_label.setStyleSheet("border: 2px solid")
            row_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            lay_row.addWidget(row_label)
            for i in range(base*15+1, base*15+16):
                call = QPushButton(f"{i:02}")
                call.setFixedSize(100,100)
                call.setFont(QFont('Arial', 60))
                call.setStyleSheet("border: 2px solid")
                call.clicked.connect(self.call_clicked)
                #call.setAlignment(Qt.AlignVCenter)
                lay_row.addWidget(call)
                self.value_labels.append(call)
            lay_row.setSpacing(10)
            lay_rows.addLayout(lay_row)

        lay_row = QHBoxLayout()
        lay_row.setSpacing(30)

        # Game title at bottom of screen
        self.game_title = QLabel(game_title_text)
        self.game_title.setFont(QFont('Arial', 40))
        self.game_title.setAlignment(Qt.AlignCenter)
        lay_row.addWidget(self.game_title)

        if automatic:
            spacer = QLabel("                                           ")
            spacer.setFont(QFont('Arial', 60))
            lay_row.addWidget(spacer)

            layout = QHBoxLayout()
            prompt = QLabel("manual | ")
            layout.addWidget(prompt)
            self.slider = QSlider(Qt.Horizontal)
            self.slider.setMinimum(0)
            self.slider.setMaximum(60)
            self.slider.setSingleStep(5)
            layout.addWidget(self.slider)
            prompt = QLabel(" | 60 sec -> ")
            layout.addWidget(prompt)
            self.timing = QLabel("manual")
            width = self.timing.sizeHint().width()
            self.timing.setFixedWidth(width)
            self.timing.setAlignment(Qt.AlignHCenter)
            layout.addWidget(self.timing)
            self.call_time = 0
            lay_row.addLayout(layout)

            layout = QHBoxLayout()
            self.pause = QPushButton("Call")
            layout.addWidget(self.pause)
            self.paused = True
            lay_row.addLayout(layout)

            self.slider.sliderMoved.connect(self.slider_position)
            self.slider.valueChanged.connect(self.slider_position)
            self.pause.clicked.connect(self.pause_toggle)

        else:
            spacer = QLabel("                                                                  ")
            spacer.setFont(QFont('Arial', 60))
            lay_row.addWidget(spacer)

        self.clear = QPushButton("Clear")
        self.clear.clicked.connect(self.clear_board)
        lay_row.addWidget(self.clear)
        self.done = QPushButton("Exit")
        self.done.clicked.connect(self.done_with_game)
        lay_row.addWidget(self.done)
        lay_row.setSpacing(30)
        lay_rows.addLayout(lay_row)
        lay_rows.setSpacing(30)

        self.call_timer = QTimer()
        self.call_timer.timeout.connect(self.call_timer_pop)
        self.call_time = 0

        self.current_game = bingogame.BingoGame()

        self.show()

    def ball(self, number):
        return f"{self.calls[number]}{number:02}"


    def call_clicked(self):
        cell = self.sender()
        called_number = int(cell.text())
        self.record_call(called_number)

    def slider_position(self, t):
        self.call_time = t
        if t == 0:
            self.pause.setText("Call")
            self.timing.setText("manual")
            self.paused = True
        else:
            self.timing.setText(str(t))
        if self.paused:
            self.pause.setText("Start")
        else:
            self.pause.setText("Pause")

    def call_timer_pop(self):
        call_value = next(self.current_game)
        window.value_labels[call_value].setStyleSheet("color: black; background: white; border: 2px solid")
        window.current_call.setText(self.current_game.ball_name(call_value))
        with open('/tmp/bingo.game', "w") as t:
            t.write(f"{self.current_game.called_list()}")

    def pause_toggle(self):
        if self.paused:
            if self.call_time == 0:  # if manual
                self.call_timer_pop()
            else:
                self.pause.setText("Pause")
                self.call_timer_pop()
                self.call_timer.start(self.call_time * 1_000)  # time is seconds * 1
                self.paused = False
        else:  #pause clicked
            self.call_timer.stop()
            self.pause.setText("Start")
            self.paused = True

    def record_call(self, call_value):
        if call_value in self.called_numbers:
            window.value_labels[call_value].setStyleSheet("border: 2px solid")
            window.current_call.setText("")
            self.called_numbers.remove(call_value)
        else:
            window.value_labels[call_value].setStyleSheet("color: black; background: white; border: 2px solid")
            window.current_call.setText(self.ball(int(call_value)))
            self.called_numbers.append(call_value)
        with open('/tmp/bingo.game', "w") as t:
            print(f"{self.called_numbers}", file=t)


    def clear_board(self):
        self.call_timer.stop()  # end current game
        if len(self.current_game):
            self.current_game.game_log(logfile_name)
        self.current_game = bingogame.BingoGame()
        # reset the board
        for i in range(1, 76):
            window.value_labels[int(i)].setStyleSheet("border: 2px solid")
            window.current_call.setText("")

    def done_with_game(self):
        if len(self.current_game):
            self.current_game.game_log(logfile_name)
        exit(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="BingobBoard",
        description="""Fullscreen (TV) display of a Bingo call board, along
        with a control panel for either manually called games or games called
        by automation in the program.""",
        epilog="To run, type ./BingoBoard.py")

    parser.add_argument('-s', '--screentitle',
        default="Knights of Columbus 3660",
        action="store",
        dest="screen_title_text",
        metavar='"top left title"',
        help="Permanent title displayed on the upper left of the screen. Remains constant during program run.")

    parser.add_argument('-t', '--title',
        default="Bingo Night",
        action="store",
        dest="game_title_text",
        metavar='"top right message"',
        help="Variable title displayed in the upper right of the screen. Can be changed via control pane.")

    parser.add_argument('-a', '--automatic',
        action="store_true",
        dest="automatic",
        help="Controls manual or automatic game.")

    parser.add_argument('-v', '--version',
        action="version", version="%(prog)s " + BingoBoard_version)

    args = parser.parse_args()

    automatic = args.automatic
    screen_title_text = args.screen_title_text
    game_title_text = args.game_title_text

    logfile_name = str(datetime.date.today()) + ".bingo.logfile"

    app = QApplication([])

    window = BingoWindow(automatic)

    exit(app.exec_())
