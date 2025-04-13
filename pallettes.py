'''
    Define color pallettes for use in BingoBoard.py

    Each entry in pallettes defines a different set
    of colors to be used on the screen. Within each
    style, board_style defines the overall Background
    of the board, current_call_style defines the large
    number at the top right of the screen,
    uncalled_number_style gives the display of all the
    uncalled numbers in the main screen, called_number_style
    gives the display of each of the smaller called numbers
    once they've been in the large box at the top,
    button_style describes how the interface buttons are
    rendered, and slider_style describes how the slider
    will be displayed.
'''
from re import A
from webbrowser import BackgroundBrowser
from test.test_capi.test_getargs import LARGE
import numbers
pallettes = \
    {"default":
        {"board_style": "; ".join(("color: black",
            "background-color: dimgray",
            "margin: 10")),
         "current_call_style": " ; ".join(("color: black" ,
            "background-color: silver",
            "border-color: black",
            "border-radius: 8",
            "border: 8px ridge", )),
         "uncalled_number_style": "border: 2px solid",
         "called_number_style": " ; ".join(("color: black",
            "background: white",
            "border: 2px solid")),
         "button_style": ";",
         "slider_style": ";", },
     "blue":
        {"board_style": "; ".join(("color: darkblue",
            "background-color: cornflowerblue",
            "margin: 10")),
         "current_call_style": " ; ".join(("color: blue" ,
            "background-color: deepskyblue",
            "border-color: black",
            "border-radius: 8",
            "border: 8px ridge", )),
         "uncalled_number_style": "border: 2px solid",
         "called_number_style": " ; ".join(("color: black",
            "background: lightblue",
            "border: 2px solid")),
         "button_style": "background-color: lightcyan",
         "slider_style": "background-color: lightcyan", },
     "truly":
        {"board_style": "; ".join(("color: #231650",
            "background-color: #f3742b",
            "margin: 10")),
         "current_call_style": " ; ".join(("color: #231650" ,
            "background-color: #fed172",
            "border-color: black",
            "border-radius: 15",
            "border: 8px ridge", )),
         "uncalled_number_style": " ; ".join(("border: 2px solid",
             "background-color: #612e37")),
         "called_number_style": " ; ".join(("color: black",
            "background: #fed172",
            "border: 2px solid")),
         "button_style": "color: #231650, ; background-color: #f3742b",
         "slider_style": "color: #231650,", },
     "parade":
        {"board_style": "; ".join(("color: #3d9098",
            "background-color: #60beae",
            "margin: 10")),
         "current_call_style": " ; ".join(("color: #3d9098" ,
            "background-color: #f1efe3",
            "border-color: black",
            "border-radius: 15",
            "border: 8px ridge", )),
         "uncalled_number_style": " ; ".join(("border: 2px solid",
             "background-color: #60beae")),
         "called_number_style": " ; ".join(("color: black",
            "background: #e1e2c2",
            "border: 2px solid")),
         "button_style": "background-color: #e1e2c2",
         "slider_style": ";", },
     "patriotic":
        {"board_style": "; ".join(("color: #976050",
            "background-color: #c0e6ef",
            "margin: 10")),
         "current_call_style": " ; ".join(("color: #976050" ,
            "background-color: #f5f6f6",
            "border-color: black",
            "border-radius: 15",
            "border: 8px ridge", )),
         "uncalled_number_style": " ; ".join(("border: 2px solid",
             "background-color: #dcb48b")),
         "called_number_style": " ; ".join(("color: #ef6365",
            "background: #f0c6c6",
            "border: 2px solid")),
         "button_style": "background-color: #dcb48b",
         "slider_style": ";", },
     "flag":
        {"board_style": "; ".join(("color: #ffffff",
            "background-color: #0a3161",
            "margin: 10")),
         "current_call_style": " ; ".join(("color: #b31942" ,
            "background-color: #ffffff",
            "border-color: black",
            "border-radius: 15",
            "border: 8px ridge", )),
         "uncalled_number_style": "border: 2px solid",
         "called_number_style": " ; ".join(("color: #b31942",
            "background: #ffffff",
            "border: 2px solid")),
         "button_style": "background-color: #B31942",
         "slider_style": ";", },
    }

if __name__ == "__main__":
    import json
    print(json.dumps(pallettes, indent=4))
