import csv
import random
import time

def printMatrix(pas):
    for i in range(3):
        for j in range(3):
            print(pas[3*i+j], end=' ')
        print('\n')

class TicTacToeGame():
    def __init__(self, paseczek, znaczek):
        self.state = paseczek
        self.player = znaczek
        self.winner = None

    def allowed_moves(self):
        states = []
        for i in range(len(self.state)):
            if self.state[i] == ' ':
                states.append(self.state[:i] + self.player + self.state[i+1:])
        return states

    def make_move(self, next_state):
        if self.winner:
            raise(Exception("Game already completed, cannot make another move!"))
        if not self.__valid_move(next_state):
            raise(Exception("Cannot make move {} to {} for player {}".format(
                    self.state, next_state, self.player)))

        self.state = next_state
        self.winner = self.predict_winner(self.state)
        if self.winner:
            self.player = None
        elif self.player == 'X':
            self.player = 'O'
        else:
            self.player = 'X'

    def playable(self):
        return ( (not self.winner) and any(self.allowed_moves()) )

    def predict_winner(self, state):
        lines = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
        winner = None
        for line in lines:
            line_state = state[line[0]] + state[line[1]] + state[line[2]]
            if line_state == 'XXX':
                winner = 'X'
            elif line_state == 'OOO':
                winner = 'O'
        return winner

    def __valid_move(self, next_state):
        allowed_moves = self.allowed_moves()
        if any(state == next_state for state in allowed_moves):
            return True
        return False

    def print_board(self):
        s = self.state
        print('     {} | {} | {} '.format(s[0],s[1],s[2]))
        print('    -----------')
        print('     {} | {} | {} '.format(s[3],s[4],s[5]))
        print('    -----------')
        print('     {} | {} | {} '.format(s[6],s[7],s[8]))


class Agent():
    def __init__(self, game_class, epsilon=0.1, alpha=0.5, value_player='X'):
        self.V = dict()
        self.NewGame = game_class
        self.epsilon = epsilon
        self.alpha = alpha
        self.value_player = value_player

    def state_value(self, game_state):
        return self.V.get(game_state, 0.0)

    def learn_game(self, num_episodes=1000):
        for episode in range(num_episodes):
            self.learn_from_episode()

    def learn_from_episode(self):
        game = self.NewGame(pasek, znak)
        _, move = self.learn_select_move(game)
        while move:
            move = self.learn_from_move(game, move)

    def learn_from_move(self, game, move):
        game.make_move(move)
        r = self.__reward(game)
        td_target = r
        next_state_value = 0.0
        selected_next_move = None
        if game.playable():
            best_next_move, selected_next_move = self.learn_select_move(game)
            next_state_value = self.state_value(best_next_move)
        current_state_value = self.state_value(move)
        td_target = r + next_state_value
        self.V[move] = current_state_value + self.alpha * (td_target - current_state_value)
        return selected_next_move

    def learn_select_move(self, game):
        allowed_state_values = self.__state_values( game.allowed_moves() )
        if game.player == self.value_player:
            best_move = self.__argmax_V(allowed_state_values)
        else:
            best_move = self.__argmin_V(allowed_state_values)

        selected_move = best_move
        if random.random() < self.epsilon:
            selected_move = self.__random_V(allowed_state_values)

        return (best_move, selected_move)

    def play_select_move(self, game):
        allowed_state_values = self.__state_values( game.allowed_moves() )
        if game.player == self.value_player:
            return self.__argmax_V(allowed_state_values)
        else:
            return self.__argmin_V(allowed_state_values)

    def demo_game(self, verbose=False):
        game = self.NewGame(pasek, znak)
        t = 0
        while game.playable():
            if verbose:
                print(" \nTurn {}\n".format(t))
                game.print_board()
            move = self.play_select_move(game)
            game.make_move(move)
            t += 1
        if verbose:
            print(" \nTurn {}\n".format(t))
            game.print_board()
        if game.winner:
            if verbose:
                print("\n{} is the winner!".format(game.winner))
            return game.winner
        else:
            if verbose:
                print("\nIt's a draw!")
            return '-'

    def round_V(self):
        # After training, this makes action selection random from equally-good choices
        for k in self.V.keys():
            self.V[k] = round(self.V[k],1)

    def save_v_table(self):
        with open('state_values.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['State', 'Value'])
            all_states = list(self.V.keys())
            all_states.sort()
            for state in all_states:
                writer.writerow([state, self.V[state]])

    def __state_values(self, game_states):
        return dict((state, self.state_value(state)) for state in game_states)

    def __argmax_V(self, state_values):
        max_V = max(state_values.values())
        chosen_state = random.choice([state for state, v in state_values.items() if v == max_V])
        return chosen_state

    def __argmin_V(self, state_values):
        min_V = min(state_values.values())
        chosen_state = random.choice([state for state, v in state_values.items() if v == min_V])
        return chosen_state

    def __random_V(self, state_values):
        return random.choice(list(state_values.keys()))

    def __reward(self, game):
        if game.winner == self.value_player:
            return 1.0
        elif game.winner:
            return -1.0
        else:
            return 0.0


def demo_game_stats(agent):
    results = [agent.demo_game() for i in range(10000)]
    game_stats = {k: results.count(k)/100 for k in ['X', 'O', '-']}
    print("    percentage results: {}".format(game_stats))


def show_result(agent):
    results = [agent.demo_game() for i in range(10000)]
    maksimum = max(results.count('X'), results.count('O'), results.count('-'))
    if maksimum == results.count('X'):
        return 1
    elif maksimum == results.count('O'):
        return -1
    elif maksimum == results.count('-'):
        return 0


if __name__ == '__main__':
    licznik = 0
    licznikWygranych = 0
    f = open("DaneTreningoweTest2.txt", "r")
    start = time.time()
    for _ in range(200):
        f.readline()
        liniaPasek = f.readline()
        pasek = ''
        for i in range(9):
            if liniaPasek[i] == '-':
                pasek += ' '
            else:
                pasek += liniaPasek[i]
        pasek+='E'
        liniaZnak = f.readline()
        znak = liniaZnak[0]
        liniaWyniku = f.readline()
        if liniaWyniku[0] == '0':
            wynik = 0
        elif liniaWyniku[0] == '1':
            wynik = 1
        elif liniaWyniku[0] == '-':
            wynik = -1

        printMatrix(liniaPasek)

        tic = TicTacToeGame(pasek, znak)
        agent = Agent(TicTacToeGame, epsilon=0.1, alpha=0.6)
        agent.learn_game(100)

        print("Zaczynal", znak)
        licznik +=1
        wyn = show_result(agent)
        if wyn == 1:
            print("Wygral X\n")
        elif wyn == -1:
            print("Wygral O\n")
        elif wyn == 0:
            print("Jest remis\n")

        if wyn == wynik:
            licznikWygranych += 1

        print("Ilosc plansz",licznik)
        print("Ilosc prawidlowo rozpoznanych plansz", licznikWygranych)
        print("Stosunek prawidłowo rozpoznaych plansz", licznikWygranych/licznik)

        print()

        agent.round_V()
        agent.save_v_table()
    end = time.time()
    print("Czas jaki zajal trening to", end-start)