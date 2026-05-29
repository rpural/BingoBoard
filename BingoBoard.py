#! /usr/bin/env python3

import argparse
import datetime
import json

import cv2
import imutils
from PyQt5.QtCore import QSize, Qt, QThread, QTimer
from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtCore import pyqtSlot as Slot
from PyQt5.QtGui import QFont, QFontMetrics, QGuiApplication, QImage, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QDesktopWidget,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSlider,
    QVBoxLayout,
    QWidget,
)

import bingogame  # local to project
from palettes import load_palettes, palettes  # local to project

BingoBoard_version = "12.0"

large_box_dimention = 280  # default large box dimention


import faulthandler

faulthandler.enable()


class CameraThread(QThread):
    frame_signal = Signal(QImage)
    paused = False

    def __init__(self):
        super().__init__()
        self.cap = None

    def run(self):
        self.cap = cv2.VideoCapture(camera_index)
        # self.old_camera = self.camera_index
        while True:
            if not self.paused:
                _, frame = self.cap.read()
                frame = self.cvimage_to_label(frame)
                self.frame_signal.emit(frame)

    def cvimage_to_label(self, image):
        image = imutils.resize(image, width=large_box_dimention)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = QImage(image, image.shape[1], image.shape[0], QImage.Format_RGB888)
        return image


class UX_Experience:
    """
    Set the box sizes and font sizes for the large and small boxes on the screen,
    initially, and when the screen size changes.
    """

    @staticmethod
    def find_font_size(box_size, font_name, test_text, margin=30):
        """
        Given a fixed size box or width and a specified font, find the
        largest font point size that could be used to render a given text.

        box_size: the width of the box in pixels
        font_name: the font to be used for the text
        test_text: the sample text to be fitted. Should represent the widest expected
        margin: the amount of pixels to be subtracted from the box_size
        """
        font_size = 12
        font = QFont(font_name, font_size)
        width = 0
        while width < (box_size - margin):
            font_size += 1
            font = QFont(font_name, font_size)
            metrics = QFontMetrics(font)
            width = metrics.width(test_text)
        font_size -= 3
        # print(f">> font calc: {font_size}pt = ({test_text} in {box_size} = {width})")
        return font_size

    def __init__(self, parent):
        self.parent = parent
        self.screen = QGuiApplication.primaryScreen()
        self.screen = self.screen.availableGeometry()
        self.screen = (
            self.screen.width(),
            self.screen.height(),
        )  # these are the maximum bounds allowed
        self.window = (
            self.screen[0],
            self.screen[1],
        )  # initially match the screen size
        print(f">> initial = {self.window}")

        self._fontsize_cache = {}

    @property
    def large_box_size(self):
        box_width = self.window[0] / 5
        self._large_box_size = int(box_width)
        return self._large_box_size

    @property
    def small_box_size(self):
        box_width = self.window[0] / 20
        self._small_box_size = int(box_width)
        return self._small_box_size

    def small_box_font(self, font, test="89"):
        box = self.small_box_size
        font_size = self.find_font_size(box, font, test)
        # self._fontsize_cache[box] = font_size
        return QFont(font, font_size)

    def large_box_font(self, font, test="O89"):
        box = self.large_box_size
        font_size = self.find_font_size(box, font, test)
        # self._fontsize_cache[box] = font_size
        return QFont(font, font_size)

    def large_title_font(self, font, test="89"):
        box_font = self.small_box_font(font, test)
        box_font.setPointSize(int(box_font.pointSize() * 1.10))
        return box_font

    def small_title_font(self, font, test="89"):
        box_font = self.small_box_font(font, test)
        box_font.setPointSize(int(box_font.pointSize() * 0.75))
        return box_font

    def ball_count_font(self, font, test="89"):
        return self.small_box_font(font, test)

    def punchout_font(self, font, test="89"):
        box_font = self.small_box_font(font, test)
        box_font.setPointSize(int(box_font.pointSize() * 0.65))
        return box_font

    def start_resize(self, newsize):
        self.window = newsize
        print(
            f">> resize = {self.window} - large box = {self.parent.ux.large_box_size}, small box = {self.parent.ux.small_box_size}"
        )
        self.parent.current_call.setFixedWidth(self.parent.ux.large_box_size)
        self.parent.current_call.setFixedHeight(self.parent.ux.large_box_size)
        self.parent.current_call.setFont(
            self.parent.ux.large_box_font("Times New Roman")
        )
        try:
            self.parent.camera_feed.setFixedWidth(self.parent.ux.large_box_size)
            self.parent.camera_feed.setFixedHeight(self.parent.ux.large_box_size)
        except NameError:
            ...

        for cel in self.parent.value_labels[1:]:
            cel.setFixedSize(
                self.parent.ux.small_box_size, self.parent.ux.small_box_size
            )
            cel.setFont(self.parent.ux.small_box_font("Arial"))

        self.parent.screen_title.setFont(self.parent.ux.small_title_font("Arial"))
        self.parent.game_title.setFont(self.parent.ux.large_title_font("Arial"))

        self.parent.punchout.setFont(self.parent.ux.punchout_font("Arial"))
        # print(f">> font sizes = ({self.parent.ux.large_box_font("Times New Roman", "G89")}, {self.parent.ux.small_box_font("Arial", "89")}, {self.parent.ux.large_title_font("Arial", "89")}, {self.parent.ux.small_title_font("Arial", "89")})")


class Game_dialog(QDialog):
    """
    This class implements a dialog box for entering the pot amount and
    game name for the current game. It returns three values:
        success - a boolean indicating if OK or Cancel was pressed
        pot     - The dollar amount of the pot
        game    - the name of the game being played

    If game is not found in the schedule, then it is a custom
    message to be displayed without a pot or description added

    Game description is a list, the first part of which is the
    added descriptive message, and the second part is a 0 or 1.
    The 1 would indicate a Punch-out game, and the final ball
    called will be added to the line at the bottom of the screen.
    """

    def __init__(self, parent):
        super().__init__(parent)
        game_font = parent.font()
        game_font.setPointSize(game_font.pointSize() + 10)
        self.setWindowTitle("Game Description")
        lay_rows = QVBoxLayout()
        self.setLayout(lay_rows)
        self.form = QFormLayout()
        self.pot = QLineEdit()
        self.pot.setFont(game_font)
        self.form.addRow("Pot Amount: $", self.pot)
        self.game = QComboBox()
        self.game.setFont(game_font)
        self.game.addItems(palettes["schedule"].keys())
        self.game.setEditable(True)
        self.form.addRow("Game:", self.game)
        lay_rows.addLayout(self.form)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.setFont(game_font)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        lay_rows.addWidget(self.buttons)

    def get_data(self):
        return self.pot.text(), self.game.currentText()

    @staticmethod
    def get_input(parent):
        dialog = Game_dialog(parent)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            pot, game = dialog.get_data()
            return (result, pot, game)
        else:
            return (result, " ", " ")


class BingoWindow(QMainWindow):
    """
    This class creates and runs the BingoBoard window,
    displaying the called numbers, and including the
    buttons and other controls needed to run the game.
    It has two variations: Manual and Automatic.

    The Automatic mode includes controls for
    automatically calling random numbers, and
    a timer to control the time between calls.
    It can be paused and restarted.
    """

    def __init__(self, palette_name="default", automatic=False):
        """
        This method creates the layout of the main window.

        If palette_name is given, it will be used to initialize
        the window colors to be used.

        If called with automatic=True, the window will
        include controls for automatic calling of numbers,
        including a slider to control the time between
        calls, and a button to start and stop the automatic
        calling.
        """
        super().__init__()

        # [Debug] try out UX_Experience
        self.ux = UX_Experience(self)

        palette = palettes[palette_name]
        self.board_style = palette["board_style"]
        self.current_call_style = palette["current_call_style"]
        self.called_number_style = palette["called_number_style"]
        self.called_blink_style = palette["called_blink_style"]
        self.uncalled_number_style = palette["uncalled_number_style"]
        self.button_style = palette["button_style"]
        self.slider_style = palette["slider_style"]

        self.camera_zoom = 0.0

        self.value_labels = [
            None,
        ]
        self.current_game = bingogame.BingoGame()

        self.setWindowTitle("Bingo")
        self.setStyleSheet(self.board_style)

        lay_rows = QVBoxLayout()
        center = QWidget()
        center.setLayout(lay_rows)
        self.setCentralWidget(center)

        lay_row = QHBoxLayout()

        # Event / organization title and game message at top of screen
        lay_col = QVBoxLayout()
        # Organization title
        self.screen_title = QLabel(screen_title_text)
        self.screen_title.setFont(self.ux.small_title_font("Times New Roman"))
        self.screen_title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.screen_title.setAlignment(Qt.AlignLeft)
        lay_col.addWidget(self.screen_title)

        # Game title at top center of screen
        self.game_title = QLabel(game_title_text)
        self.game_title.setFont(self.ux.large_title_font("Arial"))
        self.game_title.setAlignment(Qt.AlignCenter)
        self.game_title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.game_title.setAlignment(Qt.AlignCenter)
        self.game_title.setWordWrap(True)
        lay_col.addWidget(self.game_title)

        lay_row.addLayout(lay_col)

        # Currently called number at top of screen
        self.current_call = QLabel("")
        self.current_call.setFixedWidth(self.ux.large_box_size)
        self.current_call.setFixedHeight(self.ux.large_box_size)
        self.current_call.setFont(self.ux.large_box_font("Times New Roman"))
        self.current_call.setAlignment(Qt.AlignCenter)
        # current_call_style
        self.current_call.setStyleSheet(self.current_call_style)
        lay_row.addWidget(self.current_call)

        if camera:
            # Bingo ball camera
            self.camera_feed = QLabel("")
            self.camera_feed.setFixedWidth(self.ux.large_box_size)
            self.camera_feed.setFixedHeight(self.ux.large_box_size)
            self.camera_feed.setStyleSheet(
                "color: black ; background-color: silver ; border-color: black ; border-radius: 8 ; border: 8px ridge"
            )
            lay_row.addWidget(self.camera_feed)

            camera_controls = QVBoxLayout()
            self.camera_slider = QSlider(Qt.Vertical)
            self.camera_slider.valueChanged[int].connect(self.changeCameraZoom)
            camera_controls.addWidget(self.camera_slider)

            self.camera_thread = CameraThread()
            self.camera_thread.frame_signal.connect(self.setImage)

            lay_row.addLayout(camera_controls)
        lay_rows.addLayout(lay_row)

        for base, row in enumerate(("B", "I", "N", "G", "O")):
            lay_row = QHBoxLayout()
            row_label = QLabel(row)
            row_label.setFixedSize(self.ux.small_box_size, self.ux.small_box_size)
            row_label.setFont(self.ux.small_box_font("Times New Roman"))
            row_label.setStyleSheet(
                f"background-color: {('lightblue', 'red', 'white', 'lightgreen', 'yellow')[base]} ; border: 2px solid"
            )
            row_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            lay_row.addWidget(row_label)
            for i in range(base * 15 + 1, base * 15 + 16):
                call = QPushButton(f"{i:02}")
                call.setFixedSize(self.ux.small_box_size, self.ux.small_box_size)
                call.setFont(self.ux.small_box_font("Arial"))
                call.setStyleSheet(self.uncalled_number_style)
                call.clicked.connect(self.call_clicked)
                lay_row.addWidget(call)
                self.value_labels.append(call)
                # lay_row.setSpacing(10)
            lay_rows.addLayout(lay_row)

        lay_row = QHBoxLayout()
        # lay_row.setSpacing(15)

        self.ball_count = QLabel("[ 0 ]")
        self.ball_count.setStyleSheet("width: 75px")
        self.ball_count.setFont(self.ux.ball_count_font("Arial"))
        lay_row.addWidget(self.ball_count)

        spacing = QLabel(" ")
        spacing.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        lay_row.addWidget(spacing)
        label = QLabel("punch-out:")
        label.setFont(self.ux.punchout_font("Arial"))
        lay_row.addWidget(label)
        self.punchout = QLabel("")
        self.punchout.setFont(self.ux.punchout_font("Arial"))
        lay_row.addWidget(self.punchout)
        self.punchout_game = 0

        spacing = QLabel(" ")
        spacing.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        lay_row.addWidget(spacing)
        font = self.font()
        font.setPointSize(font.pointSize() + 7)
        self.change_title = QPushButton("Edit")
        self.change_title.setFont(font)
        self.change_title.setStyleSheet("width: 95px ; " + self.button_style)
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
            self.slider.setStyleSheet(self.slider_style)
            layout.addWidget(self.slider)
            prompt = QLabel(" | 60 sec -> ")
            layout.addWidget(prompt)
            self.timing = QLabel("manual")
            width = self.timing.sizeHint().width()
            self.timing.setFixedWidth(width)
            self.timing.setAlignment(Qt.AlignHCenter)
            self.timing.setStyleSheet("width: 95px ; " + self.button_style)
            layout.addWidget(self.timing)
            self.call_time = 0
            lay_row.addLayout(layout)

            layout = QHBoxLayout()
            self.pause = QPushButton("Call")
            self.pause.setFont(font)
            self.pause.setStyleSheet("width: 95px ; " + self.button_style)
            layout.addWidget(self.pause)
            self.paused = True
            lay_row.addLayout(layout)

            self.slider.sliderMoved.connect(self.slider_position)
            self.slider.valueChanged.connect(self.slider_position)
            self.pause.clicked.connect(self.pause_toggle)
        else:
            self.punchout_button = QPushButton("Punch-out")
            self.punchout_button.setFont(font)
            self.punchout_button.setStyleSheet("width: 125px ; " + self.button_style)
            self.punchout_button.clicked.connect(self.add_punchout)
            lay_row.addWidget(self.punchout_button)

        self.record = QPushButton("Record")
        self.record.setFont(font)
        self.record.setStyleSheet("width: 125px ; " + self.button_style)
        self.record.clicked.connect(self.record_board)
        lay_row.addWidget(self.record)

        self.clear = QPushButton("Clear")
        self.clear.setFont(font)
        self.clear.setStyleSheet("width: 95px ; " + self.button_style)
        self.clear.clicked.connect(self.clear_board)
        lay_row.addWidget(self.clear)

        self.done = QPushButton("Exit")
        self.done.setFont(font)
        self.done.setStyleSheet("width: 95px ; " + self.button_style)
        self.done.clicked.connect(self.done_with_game)
        lay_row.addWidget(self.done)
        lay_rows.addLayout(lay_row)

        self.call_timer = QTimer()
        self.call_timer.timeout.connect(self.call_timer_pop)
        self.call_time = 0

        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self.blink_button_switch)
        self.blink_button = None
        self.blink_button_style = self.called_blink_style

        if camera:
            self.camera_thread.start()

    def blink_button_switch(self):
        if self.blink_button:
            self.blink_button.setStyleSheet(self.blink_button_style)
            if self.blink_button_style is self.called_blink_style:
                self.blink_button_style = self.called_number_style
            else:
                self.blink_button_style = self.called_blink_style

    def resizeEvent(self, event):
        self.camera_thread.paused = True
        super().resizeEvent(event)
        self.ux.start_resize((event.size().width(), event.size().height()))
        self.window_width = event.size().width()
        self.window_height = event.size().height()
        self.camera_thread.paused = False

    def changeCameraZoom(self, value):
        self.camera_zoom = value

    def add_punchout(self):
        current = self.current_call.text()
        if len(current) > 1:
            if len(self.punchout.text().split()) == 4:
                divider = "\n"
            else:
                divider = " "
            self.punchout.setText(self.punchout.text() + divider + current)

    def new_title(self):
        """
        This method displays a dialog box to enter a new
        game title, which will be displayed at the bottom of
        the screen. This can be used for a greeting, or to
        announce a type of game (Four Corners, Blackout, etc.)
        """
        ok, pot, game = Game_dialog.get_input(self)
        if ok == QDialog.Accepted:
            description = ""
            if pot:
                try:
                    description = f"${int(pot)} - "
                except ValueError as e:
                    print(e)
                    description = f"{pot} - "
            description += game
            punchout = 0
            try:
                addl = palettes["schedule"][game][0]
                punchout = palettes["schedule"][game][1]
                description += "\n" + addl
            except KeyError:
                ...
            self.game_title.setText(description)
            self.punchout_game = punchout

    def call_clicked(self):
        """
        When a number is clicked on the board, this method
        is called. It will display the called number in
        the current call area, and change the style of the
        button to indicate that it has been called. It will
        also add the called number to the list of called
        numbers.
        """
        cell = self.sender()
        called_number = int(cell.text())
        self.record_call(called_number)
        self.ball_count.setText("[ " + str(len(self.current_game)) + " ]")

    """
    The following three methods are used to control the
    automatic mode
    """

    def slider_position(self, t):
        """
        This method is called when the slider is moved.
        It will set the time between calls based on the
        slider position. If the slider is at 0, it will
        indicate a manual (untimed), random game.
        Otherwise, it will set the time between calls
        to the slider value in seconds.
        """
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
        """
        When running a timed random game, this method
        is called by the timer. It will call the next
        number in the game, display it, and update
        the list of called numbers.
        """
        call_value = next(self.current_game)
        # [LINK] called_number_style
        window.value_labels[call_value].setStyleSheet(self.called_number_style)
        window.current_call.setText(self.current_game.ball_name(call_value))

    def pause_toggle(self):
        """
        This method is called when the pause button
        is clicked. It will toggle between pausing
        and starting the timer. If the game is
        paused, it will stop the timer and change
        the button text to "Start".
        """
        if self.paused:
            if self.call_time == 0:  # if manual
                self.call_timer_pop()
            else:
                self.pause.setText("Pause")
                self.call_timer_pop()
                self.call_timer.start(self.call_time * 1_000)  # time is seconds * 1
                self.paused = False
        else:  # pause clicked
            self.call_timer.stop()
            self.pause.setText("Start")
            self.paused = True

    def record_call(self, call_value):
        """
        This method is called when a number is clicked
        on the board. It will change the style of the
        button to indicate that it has been called,
        display the called number in the current call
        area, and add the called number to the list of
        called numbers.
        """
        if call_value in self.current_game.called_list():
            window.value_labels[call_value].setStyleSheet(self.uncalled_number_style)
            self.current_game.called_numbers.remove(call_value)
            if window.value_labels[call_value] is self.blink_button:
                window.current_call.setText("")
                self.blink_timer.stop()
                self.blink_button = None
        else:
            window.value_labels[call_value].setStyleSheet(self.called_number_style)
            window.current_call.setText(self.current_game.ball_name(int(call_value)))
            self.current_game.called_numbers.append(call_value)
            if self.blink_button:
                self.blink_button.setStyleSheet(self.called_number_style)
            self.blink_button = window.value_labels[call_value]
            self.blink_timer.start(500)

    def record_board(self):
        self.call_timer.stop()  # end current game
        if len(self.current_game):
            self.current_game.game_log(logfile_name, game=self.game_title.text())
        self.record.setText("Record ✅")
        if self.punchout_game:
            self.add_punchout()
        self.record_timer = QTimer()
        self.record_timer.timeout.connect(self.record_timer_pop)
        self.record_timer.start(5000)

    def record_timer_pop(self):
        self.record_timer.stop()
        self.record.setText("Record")

    def clear_board(self):
        """
        This method is called when the Clear button is
        clicked. It will end the current game, log the
        game if there are called numbers, Record the game
        to the log, and reset the board for a new game.
        """
        self.call_timer.stop()  # end current game
        if len(self.current_game):
            self.current_game.game_log(logfile_name, game=self.game_title.text())
        if self.punchout_game:
            self.add_punchout()
        self.current_game = bingogame.BingoGame()
        # reset the board
        self.blink_timer.stop()
        self.blink_button = None
        for i in range(1, 76):
            window.value_labels[int(i)].setStyleSheet(self.uncalled_number_style)
            window.current_call.setText("")
        window.ball_count.setText("[ 0 ]")

    def done_with_game(self):
        """
        This method is called when the Exit button is
        clicked. It will end the current game, log the
        game if there are called numbers, and exit the
        program.
        """
        self.record_board()
        exit(0)

    @Slot(QImage)
    def setImage(self, image):
        self.camera_feed.setPixmap(
            QPixmap.fromImage(image).scaled(
                QSize(
                    int(large_box_dimention * (1 + self.camera_zoom / 100)),
                    int(large_box_dimention * (1 + self.camera_zoom / 100)),
                ),
                aspectRatioMode=Qt.KeepAspectRatioByExpanding,
            )
        )


if __name__ == "__main__":
    """
    The main program. It parses the command line arguments,
    creates the BingoWindow, and starts the application.
    """

    palettes = load_palettes("palettes.json")
    palette_list = ", ".join([i for i in palettes.keys() if i != "schedule"])

    parser = argparse.ArgumentParser(
        prog="BingobBoard",
        description="""Fullscreen (TV) display of a Bingo call board, along
        with controls for either manually called games or games called
        by automation in the program.

        For manual games, called numbers are chosen by clicking on the number
        on the screen.""",
        epilog="To run, type './BingoBoard.py', followed by your selected options.",
    )

    # accept the name of a color palette to use. Defaults to "default"
    parser.add_argument(
        "-p",
        "--palette",
        default="default",
        action="store",
        dest="palette_name",
        metavar='"color palette to use"',
        help=f"Choose a pre-defined color palette to use on the display. Remains constant during program run. Choices are {palette_list}",
    )

    # Accept a title for the top of the screen. This would normally be the
    # organization name, or event name.
    parser.add_argument(
        "-s",
        "--screentitle",
        default="Knights of Columbus 3660",
        action="store",
        dest="screen_title_text",
        metavar='"organization title or message"',
        help="Permanent title displayed on the upper left of the screen. Remains constant during program run.",
    )

    # Accept a title for the bottom of the screen. This would normally be
    # the game type, or a message.
    parser.add_argument(
        "-t",
        "--title",
        default="Welcome",
        action="store",
        dest="game_title_text",
        metavar='"game title or message"',
        help="Title displayed iinitially in the top of the screen. Can be changed via Edit button.",
    )

    parser.add_argument(
        "-c",
        "--camera",
        action="store_true",
        dest="camera",
        help="Include bingo ball camera next to current number called.",
    )

    parser.add_argument(
        "-i",
        "--index",
        action="store",
        dest="camera_index",
        help="Index of camera to be used.",
    )

    # Accept a flag for automatic or manual game.
    parser.add_argument(
        "-a",
        "--automatic",
        action="store_true",
        dest="automatic",
        help="Controls manual or automatic game.",
    )

    # Display the program version and exit.
    parser.add_argument(
        "-v", "--version", action="version", version="%(prog)s " + BingoBoard_version
    )

    args = parser.parse_args()

    automatic = args.automatic
    camera = args.camera
    if camera:
        camera_index = int(args.camera_index)
    screen_title_text = args.screen_title_text
    game_title_text = args.game_title_text

    # Create a logfile name based on the date.
    logfile_name = str(datetime.date.today()) + ".bingo.logfile"

    # Create the command loop, create the display, and start the app.
    app = QApplication([])

    window = BingoWindow(args.palette_name, automatic)
    window.show()

    exit(app.exec_())
