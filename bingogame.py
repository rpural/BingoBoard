#! /usr/bin/env python3

import secrets  # A more random random number generator than the random module
import datetime

class BingoGame:
    '''
    The class represents a game of bingo: It tracks the drawn numbers and
    produces the game documentation at the end. It implements a generator
    so that the numbers can be used with next().

    The game is tracked strictly as numbers drawn, but there is a method
    to return the text version of the bingo call.

    Methods:
        __init__() starts a new game by generating a list of uncalled
        numbers.

        __next__() generates a random called number, tracks it, and returns it.

        ball_name(number) accepts an integer and returns a string with the ball name.

        called_numbers() returns the numbers called in the current game.

        game_log("filename") returns a string containing a time stamp and the called
        numbers, to optionally be written into a log. If filename is given,
        append line to the file. If filename is absent, return the line.

        __str__() returns a text of the current uncalled and called numbers.
    '''

    calls = {}
    # the associated letters for each number

    def __init__(self):
        '''
            Create a new Bingo game. Populate the potential
            calls list with the numbers from 1 through 75,
            and create an empty called numbers list.
            Populate the calls list with the letters associated
            with each number.
        '''
        self.uncalled_numbers = list(range(1, 76))
        # initially, the list of values, from 1 to 75

        self.called_numbers = []
        # initially, an empty list. will contain all the numbers called.

        for i in range(1, 16):
            self.calls[i] = "B"
            self.calls[i+15] = "I"
            self.calls[i+15*2] = "N"
            self.calls[i+15*3] = "G"
            self.calls[i+15*4] = "O"

    def __iter__(self):
        '''
            The object itself is an iterator. Defining __iter__()
            just implements the protocol required for an iterator.
        '''
        return self

    def __next__(self):
        '''
            Generate the next number to be called, remove from
            the uncalled list and add it to the called list.
            Return the number to be called.
        '''
        if len(self.uncalled_numbers) > 0:
            call = secrets.choice(self.uncalled_numbers)
            self.uncalled_numbers.remove(call)
            self.called_numbers.append(call)
            return call
        else:
            raise StopIteration

    def called_list(self):
        '''
            Return a list of all the numbers currently called
            using this instantiation of the object.
        '''
        return self.called_numbers

    def game_log(self, filename=None):
        '''
            For use at the end of a game, write a timestamp and the
            called numbers for the game to a log file if a filename
            is given. Otherwise, just return the log line to the
            caller.
        '''
        log_line = f"{[datetime.datetime.now().strftime("%m/%d/%Y-%H:%M")] + self.called_list()}"
        if filename:
            with open(filename, "a") as logfile:
                print(log_line, file=logfile)
        else:
            return log_line

    def __str__(self):
        '''
            Return the lists of called and uncalled numbers.
        '''
        return f'''
        called: {self.called_numbers}
        remaining: {self.uncalled_numbers}
        '''

    def __len__(self):
        '''
            Return the count of numbers that have been called.
            One use is to see if a log file needs to be written.
        '''
        return len(self.called_numbers)

    @classmethod
    def ball_name(cls, value):
        '''
            Given a number between 1 and 75, add the proper
            letter to make it into a Bingo ball name. For values
            out of range, just return the number as a string.
        '''
        return f"{cls.calls[value]}{value}" if 1 <= value <= 75 else \
            str(value)


if __name__ == "__main__":
    '''
        If run directly, test the various methods.
    '''
    game = BingoGame()

    i = 0
    for call in game: # call 10 numbers
        i += 1
        if i > 10:
            break
        print(BingoGame.ball_name(call))

    print(game)

    print(game.called_list())

    game = BingoGame()

    for call in game:
        print(BingoGame.ball_name(call), end=" ")

    print(game)
    print(game.game_log())

    print("Various calls to ball_name:",
        BingoGame.ball_name(1), BingoGame.ball_name(75),
        BingoGame.ball_name(0), BingoGame.ball_name(76))
