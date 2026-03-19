#! /usr/bin/env python3

from PyQt5.QtWidgets import ( QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QHBoxLayout,
    QMainWindow,
    QInputDialog,
    QSizePolicy, )

from PyQt5.QtCore import Qt, QSize, QTimer, QThread
from PyQt5.QtCore import pyqtSignal as Signal
from PyQt5.QtCore import pyqtSlot as Slot

from PyQt5.QtGui import QFont, QFontMetrics, QImage, QPixmap

import cv2
from cv2_enumerate_cameras import enumerate_cameras
import imutils

import datetime
import argparse
import json

import bingogame # local to project

from palettes import palettes, load_palettes # local to project

BingoBoard_version = "7.0"


class CameraThread(QThread):
    frame_signal = Signal(QImage)

    def list_cameras(self):
        cameras = enumerate_cameras()
        result = [cam.index for cam in cameras]
        return result


    def __init__(self):
        super().__init__()
        self.cameras = self.list_cameras()
        self.old_camera = -1
        self.camera_index = 0
        self.cap = None

    def run(self):
        self.cap = cv2.VideoCapture(self.cameras[self.camera_index])
        self.old_camera = self.camera_index
        while True:
            self.cap = cv2.VideoCapture(self.cameras[self.camera_index])
            _, frame = self.cap.read()
            frame = self.cvimage_to_label(frame)
            self.frame_signal.emit(frame)
            self.cap.release()

    def switch_camera(self):
        """[TODO]:
        Next three lines limits camera index to 0 or 1, as the isOpened()
        function fails to work on a non-existant camera, but VideoCapture()
        doesn't appear to return anything useful in that situation.
        """
        self.cap.release()
        base_index = self.camera_index
        while True:
            self.camera_index += 1
            if self.camera_index >= len(self.cameras):
                self.camera_index = 0
            self.cap = cv2.VideoCapture(self.cameras[self.camera_index])
            if self.cap and self.cap.isOpened():
                self.cap.release()
                break
            if self.camera_index == base_index:
                return None
        self.run()

    def cvimage_to_label(self, image):
        image = imutils.resize(image, width=280)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = QImage(image, image.shape[1], image.shape[0], QImage.Format_RGB888)
        return image


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

    def find_font_size(self, box_size, font_name, test_text, margin=30):
        '''
        Given a fixed size box or width and a specified font, find the
        largest font that could be used to render a given text.

        box_size: the width of the box in pixels
        font_name: the font to be used for the text
        test_text: the sample text to be fitted. Should represent the widest expected
        margin: the amount of pixels to be subtracted from the box_size
        '''
        font_size = 12
        font = QFont(font_name, font_size)
        width = 0
        while width < (box_size - margin):
            font_size += 3
            font = QFont(font_name, font_size)
            metrics = QFontMetrics(font)
            width = metrics.width(test_text)
        font_size -= 3
        print(f"font selected: ({font_name}, {font_size})")
        return font_size

    def __init__(self, palette_name="default", automatic=False):
        '''
        This method creates the layout of the main window.

        If palette_name is given, it will be used to initialize
        the window colors to be used.

        If called with automatic=True, the window will
        include controls for automatic calling of numbers,
        including a slider to control the time between
        calls, and a button to start and stop the automatic
        calling.
        '''
        super().__init__()

        # Get the initial window size
        window_size = self.screen().size()
        print(f"initial size - {window_size}")
        self.window_width = window_size.width()
        self.window_height = window_size.height()

        self.scale_large_box = int(0.15 * self.window_width)
        self.scale_large_text = int(0.05 * self.window_width)
        self.scale_small_box = int(0.054 * self.window_width)
        self.scale_small_text = int(0.023 * self.window_width)
        self.scale_large_text = self.find_font_size(self.scale_large_box, "Times New Roman", "G89")
        self.scale_small_text = self.find_font_size(self.scale_small_box, "Helvetica", "89")
        print(f"scales: ({self.scale_large_box}, {self.scale_large_text}), ({self.scale_small_box}, {self.scale_small_text})")

        palette = palettes[palette_name]
        self.board_style = palette["board_style"]
        self.current_call_style = palette["current_call_style"]
        self.called_number_style = palette["called_number_style"]
        self.uncalled_number_style = palette["uncalled_number_style"]
        self.button_style = palette["button_style"]
        self.slider_style = palette["slider_style"]

        self.camera_index = 0
        self.camera_zoom = 0.0

        self.value_labels = [None,]
        self.current_game = bingogame.BingoGame()

        self.setWindowTitle("Bingo Board")
        print(f"first resize - {self.screen().size()}")
        # self.resize(self.screen().size())
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
        self.screen_title.setFont(QFont('Times New Roman',25))
        self.screen_title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.screen_title.setAlignment(Qt.AlignLeft)
        lay_col.addWidget(self.screen_title)

        # Game title at top center of screen
        self.game_title = QLabel(game_title_text)
        self.game_title.setFont(QFont('Arial', 50))
        self.game_title.setAlignment(Qt.AlignCenter)
        self.game_title.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.game_title.setAlignment(Qt.AlignCenter)
        self.game_title.setWordWrap(True)
        # self.game_title.setFixedWidth(1000)
        lay_col.addWidget(self.game_title)

        lay_row.addLayout(lay_col)
        # lay_row.addWidget(self.game_title)

        # Currently called number at top of screen
        self.current_call = QLabel("")
        self.current_call.setFixedWidth(self.scale_large_box)
        self.current_call.setFixedHeight(self.scale_large_box)
        self.current_call.setFont(QFont('Times New Roman', self.scale_large_text))
        self.current_call.setAlignment(Qt.AlignCenter)
        # [LINK] current_call_style
        self.current_call.setStyleSheet(self.current_call_style)
        lay_row.addWidget(self.current_call)

        if camera:
            # Bingo ball camera
            self.camera_feed = QLabel("")
            self.camera_feed.setFixedWidth(self.scale_large_box)
            self.camera_feed.setFixedHeight(self.scale_large_box)
            self.camera_feed.setStyleSheet(
                "color: black ; background-color: silver ; border-color: black ; border-radius: 8 ; border: 8px ridge"
            )
            lay_row.addWidget(self.camera_feed)

            camera_controls = QVBoxLayout()
            self.camera_slider = QSlider(Qt.Vertical)
            self.camera_slider.valueChanged[int].connect(self.changeCameraZoom)
            camera_controls.addWidget(self.camera_slider)
            self.switch_camera = QPushButton("📹")
            self.switch_camera.setStyleSheet("padding: 5px ; " + self.button_style)
            self.switch_camera.clicked.connect(self.changeCameraIndex)
            camera_controls.addWidget(self.switch_camera)

            self.camera_thread = CameraThread()
            self.camera_thread.frame_signal.connect(self.setImage)

            lay_row.addLayout(camera_controls)
        lay_rows.addLayout(lay_row)


        for base, row in enumerate(("B","I","N","G","O")):
            lay_row = QHBoxLayout()
            row_label = QLabel(row)
            row_label.setFixedSize(self.scale_small_box, self.scale_small_box)
            row_label.setFont(QFont('Arial', self.scale_small_text))
            row_label.setStyleSheet(f"background-color: {('lightblue','red','white','lightgreen','lightyellow')[base]} ; border: 2px solid")
            row_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            lay_row.addWidget(row_label)
            for i in range(base*15+1, base*15+16):
                call = QPushButton(f"{i:02}")
                call.setFixedSize(self.scale_small_box, self.scale_small_box)
                call.setFont(QFont('Arial', self.scale_small_text))
                call.setStyleSheet("border: 2px solid")
                call.clicked.connect(self.call_clicked)
                lay_row.addWidget(call)
                self.value_labels.append(call)
            lay_row.setSpacing(10)
            lay_rows.addLayout(lay_row)

        lay_row = QHBoxLayout()
        lay_row.setSpacing(30)

        spacing = QLabel(" ")
        spacing.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        lay_row.addWidget(spacing)
        self.change_title = QPushButton("Edit")
        self.change_title.setStyleSheet("width: 50px ; " + self.button_style)
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
            self.timing.setStyleSheet("width: 50px ; " + self.button_style)
            layout.addWidget(self.timing)
            self.call_time = 0
            lay_row.addLayout(layout)

            layout = QHBoxLayout()
            self.pause = QPushButton("Call")
            self.pause.setStyleSheet("width: 50px ; " + self.button_style)
            layout.addWidget(self.pause)
            self.paused = True
            lay_row.addLayout(layout)

            self.slider.sliderMoved.connect(self.slider_position)
            self.slider.valueChanged.connect(self.slider_position)
            self.pause.clicked.connect(self.pause_toggle)

        self.clear = QPushButton("Clear")
        self.clear.setStyleSheet("width: 50px ; " + self.button_style)
        self.clear.clicked.connect(self.clear_board)
        lay_row.addWidget(self.clear)
        self.done = QPushButton("Exit")
        self.done.setStyleSheet("width: 50px ; " + self.button_style)
        self.done.clicked.connect(self.done_with_game)
        lay_row.addWidget(self.done)
        lay_row.setSpacing(30)
        lay_rows.addLayout(lay_row)
        lay_rows.setSpacing(10)

        self.call_timer = QTimer()
        self.call_timer.timeout.connect(self.call_timer_pop)
        self.call_time = 0

        if camera:
            self.camera_thread.start()

    def resizeEvent(self, event):
        self.window_width = event.size().width()
        self.window_height = event.size().height()
        # self.resize(self.window_width, self.window_height)
        print(f"Resized to: {self.window_width}x{self.window_height}")
        super().resizeEvent(event)

    def changeCameraZoom(self, value):
        self.camera_zoom = value

    def changeCameraIndex(self):
        self.camera_thread.switch_camera()

    def new_title(self):
        '''
        This method displays a dialog box to enter a new
        game title, which will be displayed at the bottom of
        the screen. This can be used for a greeting, or to
        announce a type of game (Four Corners, Blackout, etc.)
        '''
        text, ok = QInputDialog.getText(self, 'Game',
            'Enter new game description:')
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
            window.value_labels[call_value].setStyleSheet(
                self.uncalled_number_style)
            window.current_call.setText("")
            self.current_game.called_numbers.remove(call_value)
        else:
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
            self.current_game.game_log(logfile_name, game=self.game_title.text())
        self.current_game = bingogame.BingoGame()
        # reset the board
        for i in range(1, 76):
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
        self.clear_board()
        exit(0)

    @Slot(QImage)
    def setImage(self, image):
        self.camera_feed.setPixmap(
            QPixmap.fromImage(image).scaled(
                QSize(
                    int(280 * (1 + self.camera_zoom / 100)),
                    int(280 * (1 + self.camera_zoom / 100)),
                ),
                aspectRatioMode=Qt.KeepAspectRatioByExpanding,
            )
        )


if __name__ == '__main__':
    '''
    The main program. It parses the command line arguments,
    creates the BingoWindow, and starts the application.
    '''

    palettes = load_palettes("palettes.json")

    parser = argparse.ArgumentParser(prog="BingobBoard",
        description="""Fullscreen (TV) display of a Bingo call board, along
        with controls for either manually called games or games called
        by automation in the program.

        For manual games, called numbers are chosen by clicking on the number
        on the screen.""",
        epilog="To run, type ./BingoBoard.py")

    # accept the name of a color palette to use. Defaults to "default"
    parser.add_argument('-p', '--palette',
        default="default",
        action="store",
        dest="palette_name",
        metavar='"color palette to use"',
        help=f"Choose a pre-defined color palette to use on the display. Remains constant during program run. Choices are {palettes.keys()}")

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

    parser.add_argument(
        "-c",
        "--camera",
        action="store_true",
        dest="camera",
        help="Include bingo ball camera instead of current number called.",
    )

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
    camera = args.camera
    screen_title_text = args.screen_title_text
    game_title_text = args.game_title_text

    # Create a logfile name based on the date.
    logfile_name = str(datetime.date.today()) + ".bingo.logfile"

    # Create the command loop, create the display, and start the app.
    app = QApplication([])

    window = BingoWindow(args.palette_name, automatic)
    # window.showFullScreen()
    # window.showMaximized()
    window.show()


    exit(app.exec_())
