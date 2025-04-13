#! /usr/bin/env python3

from PyQt5.QtWidgets import ( QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QHBoxLayout,
    QMainWindow,
    QInputDialog, )

from PyQt5.QtCore import Qt, QTimer

from PyQt5.QtGui import QFont

import datetime

import argparse

import bingogame # local to project

from pallettes import pallettes # local to project

BingoBoard_version = "5.0"

class BingoWindow (QMainWindow):
    '''
    This class creates and runs the BingoBoard window,
    displaying the called numbers, and including the
    buttons and other controls needed to run the game.
    It has two variations: Manual and Automatic.

    The Automatic mode includes controls for
    automatically calling random numbers, and
    a timer to control the time between calls.
    It can be paused and restarted.
    '''
    def __init__(self, pallette_name="default", automatic=False):
        '''
        This method creates the layout of the main window.

        If pallette_name is given, it will be used to initialize
        the window colors to be used.

        If called with automatic=True, the window will
        include controls for automatic calling of numbers,
        including a slider to control the time between
        calls, and a button to start and stop the automatic
        calling.
        '''
        super().__init__()

        pallette = pallettes[pallette_name]
        self.board_style = pallette["board_style"]
        self.current_call_style = pallette["current_call_style"]
        self.called_number_style = pallette["called_number_style"]
        self.uncalled_number_style = pallette["uncalled_number_style"]
        self.button_style = pallette["button_style"]
        self.slider_style = pallette["slider_style"]

        self.value_labels = [None,]
        self.current_game = bingogame.BingoGame()

        self.setWindowTitle("Bingo")
        self.resize(self.screen().size())
        self.setStyleSheet(self.board_style)

        lay_rows = QVBoxLayout()
        center = QWidget()
        center.setLayout(lay_rows)
        self.setCentralWidget(center)
        lay_row = QHBoxLayout()

        # Event / organization title at top of screen
        self.screen_title = QLabel(screen_title_text)
        self.screen_title.setFont(QFont('Times New Roman',
            60))
        self.screen_title.setAlignment(Qt.AlignCenter)
        lay_row.addWidget(self.screen_title)

        # Currently called number at top of screen
        self.current_call = QLabel("")
        self.current_call.setFixedWidth(280)
        self.current_call.setFont(QFont('Times New Roman',
            128))
        self.current_call.setAlignment(Qt.AlignCenter)
        # [LINK] current_call_style
        self.current_call.setStyleSheet(self.current_call_style)
        lay_row.addWidget(self.current_call)
        lay_rows.addLayout(lay_row)

        for base, row in enumerate(("B","I","N","G","O")):
            lay_row = QHBoxLayout()
            row_label = QLabel(row)
            row_label.setFont(QFont('Arial', 60))
            row_label.setStyleSheet(self.uncalled_number_style)
            # [LINK] uncalled_number_style
            row_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            lay_row.addWidget(row_label)
            for i in range(base*15+1, base*15+16):
                call = QPushButton(f"{i:02}")
                call.setFixedSize(100,100)
                call.setFont(QFont('Arial', 60))
                # [LINK] uncalled_number_style
                call.setStyleSheet(self.uncalled_number_style)
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
        self.game_title.setFixedWidth(1000)
        lay_row.addWidget(self.game_title)
        self.change_title = QPushButton("Edit")
        # [LINK] button_style
        self.change_title.setStyleSheet(self.button_style)
        lay_row.addWidget(self.change_title)
        self.change_title.clicked.connect(self.new_title)

        if automatic:
            layout = QHBoxLayout()
            prompt = QLabel("manual | ")
            layout.addWidget(prompt)
            self.slider = QSlider(Qt.Horizontal)
            self.slider.setMinimum(0)
            self.slider.setMaximum(60)
            self.slider.setSingleStep(5)
            # [LINK] slider_style
            self.slider.setStyleSheet(self.slider_style)
            layout.addWidget(self.slider)
            prompt = QLabel(" | 60 sec -> ")
            layout.addWidget(prompt)
            self.timing = QLabel("manual")
            width = self.timing.sizeHint().width()
            self.timing.setFixedWidth(width)
            self.timing.setAlignment(Qt.AlignHCenter)
            # [LINK] button_style
            self.timing.setStyleSheet(self.button_style)
            layout.addWidget(self.timing)
            self.call_time = 0
            lay_row.addLayout(layout)

            layout = QHBoxLayout()
            self.pause = QPushButton("Call")
            # [LINK] button_style
            self.pause.setStyleSheet(self.button_style)
            layout.addWidget(self.pause)
            self.paused = True
            lay_row.addLayout(layout)

            self.slider.sliderMoved.connect(self.slider_position)
            self.slider.valueChanged.connect(self.slider_position)
            self.pause.clicked.connect(self.pause_toggle)

        else:
            self.game_title.setFixedWidth(1500)

        self.clear = QPushButton("Clear")
        # [LINK] button_style
        self.clear.setStyleSheet(self.button_style)
        self.clear.clicked.connect(self.clear_board)
        lay_row.addWidget(self.clear)
        self.done = QPushButton("Exit")
        self.done.setStyleSheet(self.button_style)
        self.done.clicked.connect(self.done_with_game)
        lay_row.addWidget(self.done)
        lay_row.setSpacing(30)
        lay_rows.addLayout(lay_row)
        lay_rows.setSpacing(30)

        self.call_timer = QTimer()
        self.call_timer.timeout.\
            connect(self.call_timer_pop)
        self.call_time = 0

        self.show()

    def new_title(self):
        '''
        This method displays a dialog box to enter a new
        game title, which will be displayed at the bottom of
        the screen. This can be used for a greeting, or to
        announce a type of game (Four Corners, Blackout, etc.)
        '''
        text, ok = QInputDialog.getText(self, 'Game Title',
            'Enter new game title:')
        if ok:
            self.game_title.setText(text)

    def call_clicked(self):
        '''
        When a number is clicked on the board, this method
        is called. It will display the called number in
        the current call area, and change the style of the
        button to indicate that it has been called. It will
        also add the called number to the list of called
        numbers.
        '''
        cell = self.sender()
        called_number = int(cell.text())
        self.record_call(called_number)

    '''
    The following three methods are used to control the
    automatic mode
    '''
    def slider_position(self, t):
        '''
        This method is called when the slider is moved.
        It will set the time between calls based on the
        slider position. If the slider is at 0, it will
        indicate a manual (untimed), random game.
        Otherwise, it will set the time between calls
        to the slider value in seconds.
        '''
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
        '''
        When running a timed random game, this method
        is called by the timer. It will call the next
        number in the game, display it, and update
        the list of called numbers.
        '''
        call_value = next(self.current_game)
        # [LINK] called_number_style
        window.value_labels[call_value].\
            setStyleSheet(self.called_number_style)
        window.current_call.setText(self.current_game.\
            ball_name(call_value))

    def pause_toggle(self):
        '''
        This method is called when the pause button
        is clicked. It will toggle between pausing
        and starting the timer. If the game is
        paused, it will stop the timer and change
        the button text to "Start".
        '''
        if self.paused:
            if self.call_time == 0:  # if manual
                self.call_timer_pop()
            else:
                self.pause.setText("Pause")
                self.call_timer_pop()
                self.call_timer.start(
                    self.call_time * 1_000)  # time is seconds * 1
                self.paused = False
        else:  #pause clicked
            self.call_timer.stop()
            self.pause.setText("Start")
            self.paused = True

    def record_call(self, call_value):
        '''
        This method is called when a number is clicked
        on the board. It will change the style of the
        button to indicate that it has been called,
        display the called number in the current call
        area, and add the called number to the list of
        called numbers.
        '''
        if call_value in self.current_game.called_list():
            # [LINK] uncalled_number_style
            window.value_labels[call_value].setStyleSheet(
                self.uncalled_number_style)
            window.current_call.setText("")
            self.current_game.called_numbers.remove(call_value)
        else:
            # [LINK] called_number_style
            window.value_labels[call_value].setStyleSheet(
                self.called_number_style)
            window.current_call.setText(self.current_game.
                ball_name(int(call_value)))
            self.current_game.called_numbers.append(call_value)

    def clear_board(self):
        '''
        This method is called when the Clear button is
        clicked. It will end the current game, log the
        game if there are called numbers, Record the game
        to the log, and reset the board for a new game.
        '''
        self.call_timer.stop()  # end current game
        if len(self.current_game):
            self.current_game.game_log(logfile_name)
        self.current_game = bingogame.BingoGame()
        # reset the board
        for i in range(1, 76):
            # [LINK] uncalled_number_style
            window.value_labels[int(i)].setStyleSheet(
                self.uncalled_number_style)
            window.current_call.setText("")

    def done_with_game(self):
        '''
        This method is called when the Exit button is
        clicked. It will end the current game, log the
        game if there are called numbers, and exit the
        program.
        '''
        if len(self.current_game):
            self.current_game.game_log(logfile_name)
        exit(0)


if __name__ == '__main__':
    '''
    The main program. It parses the command line arguments,
    creates the BingoWindow, and starts the application.
    '''
    parser = argparse.ArgumentParser(prog="BingobBoard",
        description="""Fullscreen (TV) display of a Bingo call board, along
        with controls for either manually called games or games called
        by automation in the program.

        For manual games, called numbers are chosen by clicking on the number
        on the screen.""",
        epilog="To run, type ./BingoBoard.py")

    # accept the name of a color pallette to use. Defaults to "default"
    parser.add_argument('-p', '--pallette',
        default="default",
        action="store",
        dest="pallette_name",
        metavar='"color pallette to use"',
        help=f"Choose a pre-defined color pallette to use on the display. Remains constant during program run. Choices are {list(pallettes.keys())}")

    # Accept a title for the top of the screen. This would normally be the
    # organization name, or event name.
    parser.add_argument('-s', '--screentitle',
        default="Knights of Columbus 3660",
        action="store",
        dest="screen_title_text",
        metavar='"top title or message"',
        help="Permanent title displayed on the upper left of the screen. Remains constant during program run.")

    # Accept a title for the bottom of the screen. This would normally be
    # the game type, or a message.
    parser.add_argument('-t', '--title',
        default="Bingo Night",
        action="store",
        dest="game_title_text",
        metavar='"bottom title or message"',
        help="Variable title displayed in the bottom of the screen. Can be changed via Edit button.")

    # Accept a flag for automatic or manual game.
    parser.add_argument('-a', '--automatic',
        action="store_true",
        dest="automatic",
        help="Controls manual or automatic game.")

    # Display the program version and exit.
    parser.add_argument('-v', '--version',
        action="version", version="%(prog)s " + BingoBoard_version)

    args = parser.parse_args()

    automatic = args.automatic
    screen_title_text = args.screen_title_text
    game_title_text = args.game_title_text

    # Create a logfile name based on the date.
    logfile_name = str(datetime.date.today()) + ".bingo.logfile"

    # Create the command loop, create the display, and start the app.
    app = QApplication([])

    window = BingoWindow(args.pallette_name, automatic)

    exit(app.exec_())
