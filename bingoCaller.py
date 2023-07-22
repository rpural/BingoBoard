import random

class Bingo_Call:
    '''
    class Bingo_Call:
        A class and object to generate random bingo number calls

        Methods:
            call_number() returns the next called number, as a string.

            called_list() returns a sorted list of all the numbers
                called so far, in sorted order

            ball(number) returns the ball string for a specific number.

            newGame() clears the called numbers list and "starts" a
                new game.
    '''
    calls = {}

    def __init__(self):
        self.called_numbers = []
        self.valid_numbers = list(range(1,76))
        for i in range(1,16):
            self.calls[i] = "B"
            self.calls[i+15] = "I"
            self.calls[i+15*2] = "N"
            self.calls[i+15*3] = "G"
            self.calls[i+15*4] = "O"
            print(i+15*4)

    def call_number(self):
        while True:
            new_number = random.choice(self.valid_numbers)
            self.called_numbers.append(new_number)
            self.valid_numbers.remove(new_number)
            return new_number

    def called_list(self):
        self.called_numbers.sort()
        return self.called_numbers[:]

    def ball(self, number):
        return f"{self.calls[number]}{number}"

    def new_game(self):
        self.called_numbers = []
        self.valid_numbers = list(range(1,76))

    def __str__(self):
        return f'''
called: {self.called_numbers}
remaining: {self.valid_numbers}
'''


if __name__ == '__main__':
    game = Bingo_Call()

    for _ in range(10):
        next_call = game.call_number()
        print(game.ball(next_call))

    print(game)

    game.new_game()

    for _ in range(5):
        next_call = game.call_number()
        print(game.ball(next_call))

    print(game)

    game.new_game()

for _ in range(75):
    next_call = game.call_number()

print(game)
