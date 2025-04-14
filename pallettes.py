'''
    Define color pallettes for use in BingoBoard.py

    Each entry in pallettes defines a different set
    of colors to be used on the screen. Within each
    style, "board" defines the overall Background
    of the board, "current" defines the large
    number at the top right of the screen,
    "uncalled" gives the display of all the
    uncalled numbers in the main screen, "called"
    gives the display of each of the smaller called numbers
    once they've been in the large box at the top,
    "button" describes how the interface buttons are
    rendered, and "slider" describes how the slider
    will be displayed.
'''

from re import A


pallettes = \
    {"default":
        {"board": "; ".join(("color: black",
            "background-color: dimgray",
            "margin: 10")),
         "current": " ; ".join(("color: black" ,
            "background-color: silver",
            "border-color: black",
            "border-radius: 8",
            "border: 8px ridge", )),
         "uncalled": "border: 2px solid",
         "called": " ; ".join(("color: black",
            "background: white",
            "border: 2px solid")),
         "button": ";",
         "slider": ";", },
     "blue":
        {"board": "; ".join(("color: darkblue",
            "background-color: cornflowerblue",
            "margin: 10")),
         "current": " ; ".join(("color: blue" ,
            "background-color: deepskyblue",
            "border-color: black",
            "border-radius: 8",
            "border: 8px ridge", )),
         "uncalled": "border: 2px solid",
         "called": " ; ".join(("color: black",
            "background: lightblue",
            "border: 2px solid")),
         "button": "background-color: lightcyan",
         "slider": "background-color: lightcyan", },
     "truly":
        {"board": "; ".join(("color: #231650",
            "background-color: #f3742b",
            "margin: 10")),
         "current": " ; ".join(("color: #231650" ,
            "background-color: #fed172",
            "border-color: black",
            "border-radius: 15",
            "border: 8px ridge", )),
         "uncalled": " ; ".join(("border: 2px solid",
             "background-color: #612e37")),
         "called": " ; ".join(("color: black",
            "background: #fed172",
            "border: 2px solid")),
         "button": "color: #231650, ; background-color: #f3742b",
         "slider": "color: #231650,", },
     "parade":
        {"board": "; ".join(("color: #3d9098",
            "background-color: #60beae",
            "margin: 10")),
         "current": " ; ".join(("color: #3d9098" ,
            "background-color: #f1efe3",
            "border-color: black",
            "border-radius: 15",
            "border: 8px ridge", )),
         "uncalled": " ; ".join(("border: 2px solid",
             "background-color: #60beae")),
         "called": " ; ".join(("color: black",
            "background: #e1e2c2",
            "border: 2px solid")),
         "button": "background-color: #e1e2c2",
         "slider": ";", },
     "patriotic":
        {"board": "; ".join(("color: #976050",
            "background-color: #c0e6ef",
            "margin: 10")),
         "current": " ; ".join(("color: #976050" ,
            "background-color: #f5f6f6",
            "border-color: black",
            "border-radius: 15",
            "border: 8px ridge", )),
         "uncalled": " ; ".join(("border: 2px solid",
             "background-color: #dcb48b")),
         "called": " ; ".join(("color: #ef6365",
            "background: #f0c6c6",
            "border: 2px solid")),
         "button": "background-color: #dcb48b",
         "slider": ";", },
     "flag":
        {"board": "; ".join(("color: #ffffff",
            "background-color: #0a3161",
            "margin: 10")),
         "current": " ; ".join(("color: #b31942" ,
            "background-color: #ffffff",
            "border-color: black",
            "border-radius: 35",
            "border: 8px ridge", )),
         "uncalled": "border: 2px solid",
         "called": " ; ".join(("color: #b31942",
            "background: #ffffff",
            "border: 2px solid")),
         "button": "background-color: #B31942",
         "slider": ";", },
     "nature":
        {"board": "; ".join(("color: black",
            "background-color: #A4B465",
            "margin: 10")),
         "current": " ; ".join(("color: #626F47" ,
            "background-color: #FEFAE0",
            "border-color: black",
            "border-radius: 35",
            "border: 8px ridge", )),
         "uncalled": "border: 2px solid",
         "called": " ; ".join(("color: black",
            "background: #FFCF50",
            "border: 2px solid")),
         "button": "background-color: #626F47 ; color: white",
         "slider": ";", },
     "xmas":
        {"board": "; ".join(("color: #5CB338",
            "background-color: #FFC145",
            "margin: 10")),
         "current": " ; ".join(("color: #FB4141" ,
            "background-color: #ECE852",
            "border-color: black",
            "border-radius: 35",
            "border: 8px ridge", )),
         "uncalled": "border: 2px solid",
         "called": " ; ".join(("color: FB4141",
            "background: #ECE852",
            "border: 2px solid")),
         "button": "background-color: #5CB338 ; color: white",
         "slider": ";", },
    }

if __name__ == "__main__":
    import json
    print(json.dumps(pallettes, indent=4))
