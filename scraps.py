import random
import json

def placeidx(place):
    if place == 4:
        return 0
    if place == 5:
        return 1
    if place == 6:
        return 2
    if place == 8:
        return 3
    if place == 9:
        return 4
    if place == 10:
        return 5

class State(object):
    def __init__(self):
        self.bankroll = 0
        self.pass_line = 0
        self.pass_line_odds = 0
        self.dont_pass = 0
        self.come = 0
        self.come_points = [0, 0, 0, 0, 0]
        self.come_odds = [0, 0, 0, 0, 0]
        self.dont_come = 0
        self.place_bets = [0, 0, 0, 0, 0, 0]
        self.place_bets_on = [False, False, False, False, False, False]
        self.field = 0
        self.point = None
        self.roll = 0
        self.shooter_rolls = 0
        self.total_rolls = 0

    def __repr__(self):
        return json.dumps(
            {
                "bankroll": self.bankroll,
                "pass_line": self.pass_line,
                "pass_line_odds": self.pass_line_odds,
                "dont_pass": self.dont_pass,
                "place_bets": self.place_bets,
                "field": self.field,
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


# Always bet the pass line, nothing else.
class PassLineOnlyStrategy(Strategy):
    def __init__(self):
        super().__init__()
        self.initial_state.pass_line = 5
        self.initial_state.bankroll = 295

    def play(self, state):
        if not state.point and state.pass_line == 0:
            state.bankroll = state.bankroll - 5
            state.pass_line = 5
        return state


# Always bet the max odds on a 3/4/5 table.
class PassLineMaxOddsStrategy(Strategy):
    def __init__(self):
        super().__init__()
        self.initial_state.pass_line = 5
        self.initial_state.bankroll = 295

    def play(self, state):
        if not state.point and state.pass_line == 0:
            state.pass_line = 5
            state.bankroll = state.bankroll - 5
        elif state.pass_line_odds == 0:
            bet = 0
            if state.point in [4, 10]:
                bet = 15
            elif state.point in [5, 9]:
                bet = 20
            elif state.point in [6, 8]:
                bet = 25
            state.pass_line_odds = bet
            state.bankroll = state.bankroll - bet
        return state


class HedgeSixEightStrategy(Strategy):
    def __init__(self):
        super().__init__()
        self.initial_state.dont_pass = 10
        self.initial_state.bankroll = 290

    def play(self, state):
        # Bet the dont pass at 2x
        if not state.point and state.dont_pass == 0:
            state.dont_pass = 10
            state.bankroll = state.bankroll - 10
        # Place the Six
        if state.place_bets[2] == 0:
            state.place_bets[2] = 6
            state.bankroll = state.bankroll - 6
        # Place the Eight
        if state.place_bets[3] == 0:
            state.place_bets[3] = 6
            state.bankroll = state.bankroll - 6
        return state

class IronCrossStrategy(Strategy):
    def __init__(self):
        super().__init__()
        self.initial_state.pass_line = 5
        self.initial_state.bankroll = 295

    def play(self, state):
        if not state.point and state.pass_line == 0:
            state.pass_line = 5
            state.bankroll = state.bankroll - 5
        # Take down the place bet for the current point
        if state.point and state.point in [5,6,8]:
            state.bankroll = state.bankroll + state.place_bets[placeidx(state.point)]
            state.place_bets[placeidx(state.point)] = 0
        # Place 5,6,8 as long as that number isn't the point
        for place in [5,6,8]:
            if state.point and state.point != place and state.place_bets[placeidx(place)] == 0:
                bet = 6
                if place == 5:
                    bet = 5
                state.place_bets[placeidx(place)] = bet
                state.bankroll = state.bankroll - bet
        # Bet the field if point is set
        if state.point and state.field == 0:
            state.field = 5
            state.bankroll = state.bankroll - 5
        # Bet 2x odds on pass line
        if state.point and state.pass_line_odds == 0:
            state.pass_line_odds = 10
            state.bankroll = state.bankroll - 10
        return state


class Game(object):
    def __init__(self, strategy, rolls=100, log=False):
        self.strategy = strategy
        self.state = strategy.initial_state
        self.rolls = rolls
        self.log = log

    def roll(self):
        return random.randint(1, 6) + random.randint(1, 6)

    def report(self):
        print(self.state)

    def run(self):
        for _ in range(self.rolls):
            self.run_one()
            if self.log:
                self.report()

    def run_one(self):
        self.state.roll = self.roll()

        # PAY FIELD BETS
        if self.state.field > 0:
            if self.state.roll in [2,3,4,9,10,11]:
                self.state.bankroll = self.state.bankroll + self.state.field * 2
            if self.state.roll in [2,12]:
                self.state.bankroll = self.state.bankroll + self.state.field * 3
            self.state.field = 0
        #
        # COME OUT ROLL
        #
        if self.state.point == None:
            if self.state.roll in [7, 11]:
                self.state.bankroll = self.state.bankroll + self.state.pass_line * 2
                self.state.pass_line = 0
                self.state.dont_pass = 0
            elif self.state.roll in [2, 3]:
                self.state.pass_line = 0
                self.state.bankroll = self.state.bankroll + self.state.dont_pass * 2
                self.state.dont_pass = 0
            elif self.state.roll in [12]:
                self.state.pass_line = 0
            else:
                # PUCK IS ON
                self.state.point = self.state.roll
        #
        # ROLLED POINT
        #
        elif self.state.roll == self.state.point:
            # PAY OUT PLACE BETS
            if self.state.roll in [4,10] and self.state.place_bets[placeidx(self.state.roll)] > 0:
                self.state.bankroll = (
                    self.state.bankroll + self.state.place_bets[placeidx(self.state.roll)] / 5 * 9
                )
            if self.state.roll in [5,9] and self.state.place_bets[placeidx(self.state.roll)] > 0:
                self.state.bankroll = (
                    self.state.bankroll + self.state.place_bets[placeidx(self.state.roll)] / 5 * 7
                )
            if self.state.roll in [6,8] and self.state.place_bets[placeidx(self.state.roll)] > 0:
                self.state.bankroll = (
                    self.state.bankroll + self.state.place_bets[placeidx(self.state.roll)] / 6 * 7
                )

            # PASS LINE PAYS 1:1
            self.state.bankroll = self.state.bankroll + self.state.pass_line * 2

            # 4,10 PASS ODDS PAYS 2:1
            if self.state.point in [4, 10]:
                self.state.bankroll = (
                    self.state.bankroll
                    + self.state.pass_line_odds
                    + self.state.pass_line_odds * 2
                )
            # 5,9 PASS ODDS PAYS 3:2
            elif self.state.point in [5, 9]:
                self.state.bankroll = (
                    self.state.bankroll
                    + self.state.pass_line_odds
                    + self.state.pass_line_odds / 2 * 3
                )
            # 6,8 PASS ODDS PAYS 6:5
            elif self.state.point in [6, 8]:
                self.state.bankroll = (
                    self.state.bankroll
                    + self.state.pass_line_odds
                    + self.state.pass_line_odds / 5 * 6
                )
            self.state.pass_line = 0
            self.state.pass_line_odds = 0
            # DONT PASS LOSES
            self.state.dont_pass = 0
            # PUCK IS OFF
            self.state.point = None
        #
        # ROLLED 7, PUCK ON (SEVEN OUT)
        #
        elif self.state.roll == 7:
            # TAKE DOWN ALL PLACE BETS
            self.state.place_bets = [0, 0, 0, 0, 0, 0]
            # TAKE DOWN PASS LINE BET & PASS ODDS
            self.state.pass_line = 0
            self.state.pass_line_odds = 0
            # DONT PASS WINS
            self.state.bankroll = self.state.bankroll + self.state.dont_pass * 2
            self.state.dont_pass = 0
            # PUCK IS OFF
            self.state.point = None
        # PUCK IS ON, DID NOT ROLL 7 OR POINT
        else:
            # PAY OUT PLACE BETS
            if self.state.roll == 4 and self.state.place_bets[0] > 0:
                self.state.bankroll = (
                    self.state.bankroll + self.state.place_bets[0] / 5 * 9
                )
            if self.state.roll == 10 and self.state.place_bets[5] > 0:
                self.state.bankroll = (
                    self.state.bankroll + self.state.place_bets[5] / 5 * 9
                )
            if self.state.roll == 5 and self.state.place_bets[1] > 0:
                self.state.bankroll = (
                    self.state.bankroll + self.state.place_bets[1] / 5 * 7
                )
            if self.state.roll == 9 and self.state.place_bets[4] > 0:
                self.state.bankroll = (
                    self.state.bankroll + self.state.place_bets[4] / 5 * 7
                )
            if self.state.roll == 6 and self.state.place_bets[2] > 0:
                self.state.bankroll = (
                    self.state.bankroll + self.state.place_bets[2] / 6 * 7
                )
            if self.state.roll == 8 and self.state.place_bets[3] > 0:
                self.state.bankroll = (
                    self.state.bankroll + self.state.place_bets[3] / 6 * 7
                )
        # RUN OUR STRATEGY
        self.state = self.strategy.play(self.state)


#
# MAIN
#
trials = 1000
sum_bankroll = 0
for _ in range(trials):
    strategy = PassLineOnlyStrategy()
    game = Game(strategy, log=False)
    game.run()
    sum_bankroll = sum_bankroll + game.state.bankroll
print(f"PassLineOnly Avg Final Bankroll: {sum_bankroll / trials}")

trials = 1000
sum_bankroll = 0
for _ in range(trials):
    strategy = PassLineMaxOddsStrategy()
    game = Game(strategy, log=False)
    game.run()
    sum_bankroll = sum_bankroll + game.state.bankroll
print(f"PassLineMaxOdds Avg Final Bankroll: {sum_bankroll / trials}")

trials = 1000
sum_bankroll = 0
for _ in range(trials):
    strategy = HedgeSixEightStrategy()
    game = Game(strategy, log=False)
    game.run()
    sum_bankroll = sum_bankroll + game.state.bankroll
print(f"HedgeSixEight Avg Final Bankroll: {sum_bankroll / trials}")

trials = 1000
sum_bankroll = 0
for _ in range(trials):
    strategy = IronCrossStrategy()
    game = Game(strategy, log=False)
    game.run()
    sum_bankroll = sum_bankroll + game.state.bankroll
print(f"IronCross Avg Final Bankroll: {sum_bankroll / trials}")
