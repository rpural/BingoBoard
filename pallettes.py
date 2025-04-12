# [LINK] current_call_style
# [LINK] uncalled_number_style
# [LINK] button_style
# [LINK] slider_style
# [LINK] called_number_style
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
     "red":
        {"board_style": "; ".join(("color: firebrick",
            "background-color: lightcoral",
            "margin: 10")),
         "current_call_style": " ; ".join(("color: firebrick" ,
            "background-color: ghostwhite",
            "border-color: black",
            "border-radius: 15",
            "border: 8px ridge", )),
         "uncalled_number_style": "border: 2px solid",
         "called_number_style": " ; ".join(("color: black",
            "background: hotpink",
            "border: 2px solid")),
         "button_style": "color: white ; background-color: darkred",
         "slider_style": "color: white ; background-color: darkred", },
    }

if __name__ == "__main__":
    import json
    print(json.dumps(pallettes, indent=4))
