import random
import json


class State(object):
    def __init__(self):
        self.bankroll = 0
        self.pass_line = 0
        self.pass_line_odds = 0
        self.come = 0
        self.come_points = [0, 0, 0, 0, 0]
        self.come_odds = [0, 0, 0, 0, 0]
        self.dont_come = 0
        self.place_bets = [0, 0, 0, 0, 0, 0]
        self.place_bets_on = [False, False, False, False, False, False]
        self.point = None
        self.roll = 0
        self.shooter_rolls = 0
        self.total_rolls = 0

    def __repr__(self):
        return json.dumps(
            {
                "bankroll": self.bankroll,
                "pass_line": self.pass_line,
                "roll": self.roll,
                "point": self.point,
            }
        )


class Strategy(object):
    def __init__(self):
        self.initial_state = State()
        self.states = []

    def play(self, state):
        return state


class PassLineOnlyStrategy(Strategy):
    def __init__(self):
        super().__init__()
        self.initial_state.pass_line = 5
        self.initial_state.bankroll = 295

    def play(self, state):
        if not state.point:
            state.bankroll = state.bankroll - 5
            state.pass_line = 5
        return state


class Game(object):
    def __init__(self, strategy, rolls=100):
        self.strategy = strategy
        self.state = strategy.initial_state
        self.rolls = rolls

    def roll(self):
        return random.randint(1, 6) + random.randint(1, 6)

    def report(self):
        print(self.state)

    def run(self):
        for _ in range(self.rolls):
            self.run_one()
            # self.report()

    def run_one(self):
        self.state.roll = self.roll()
        #
        # COME OUT ROLL
        #
        if self.state.point == None:
            if self.state.roll in (7, 11):
                self.state.bankroll = self.state.bankroll + self.state.pass_line
                self.state.pass_line = 0
            elif self.state.roll in (2, 3, 12):
                self.state.pass_line = 0
            else:
                # PUCK IS ON
                self.state.point = self.state.roll
        #
        # ROLLED POINT
        #
        elif self.state.roll == self.state.point:
            # PASS LINE PAYS 2:1
            self.state.bankroll = self.state.bankroll + self.state.pass_line * 2
            self.state.pass_line = 0
            # 4,10 PASS ODDS PAYS 2:1
            if self.state.point in (4, 10):
                self.state.bankroll = (
                    self.state.bankroll
                    + self.state.pass_line_odds
                    + self.state.pass_line_odds * 2
                )
            # 5,9 PASS ODDS PAYS 3:2
            elif self.state.point in (5, 9):
                self.state.bankroll = (
                    self.state.bankroll
                    + self.state.pass_line_odds
                    + self.state.pass_line_odds / 2 * 3
                )
            # 6,8 PASS ODDS PAYS 6:5
            elif self.state.point in (6, 8):
                self.state.bankroll = (
                    self.state.bankroll
                    + self.state.pass_line_odds
                    + self.state.pass_line_odds / 5 * 6
                )
            self.state.pass_line_odds = 0
            # PUCK IS OFF
            self.state.point = None
        #
        # ROLLED 7, PUCK ON
        #
        elif self.state.roll == 7:
            # TAKE DOWN ALL PLACE BETS
            self.state.place_bets = [0, 0, 0, 0, 0, 0]
            # TAKE DOWN PASS LINE BET & PASS ODDS
            self.state.pass_line = 0
            self.state.pass_line_odds = 0
            # PUCK IS OFF
            self.state.point = None
        # PUCK IS ON, DID NOT ROLL 7 OR POINT
        else:
            pass
        # RUN OUR STRATEGY
        self.state = self.strategy.play(self.state)


#
# MAIN
#
trials = 1000
sum_bankroll = 0
for _ in range(trials):
    strategy = PassLineOnlyStrategy()
    game = Game(strategy)
    game.run()
    sum_bankroll = sum_bankroll + game.state.bankroll
print(f"Avg Final Bankroll: {sum_bankroll / trials}")
