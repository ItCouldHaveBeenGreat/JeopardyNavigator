import csv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

input_path = 'data/jepoardy_games.csv'

def get_streaks(input_path):
    with open(input_path, 'r') as games_file:
        games_reader = csv.reader(games_file)
        current_winner = ''
        current_streak = 0
        previous_game = next(games_reader)
        streaks = {}
        for game in games_reader:
            # Whoever was in the previous game is the winner
            winners = list(set(previous_game[2:5]) & set(game[2:5]))

            if len(winners) == 0:
                # This just happens sometimes; count it as a streak end with a restart
                print('Zero winners detected between %s and %s; ending streak' % (previous_game, game))
                if current_winner != '':
                    streaks[current_winner] = current_streak
                    current_winner = ''
            elif current_winner == '':
                # If we're at the beginning, just set someone as a winner and get going!
                current_winner = winners[0]
                current_streak = 1
            elif current_winner != winners[0]:
                # End the current streak and start the new one
                streaks[current_winner] = current_streak
                current_winner = winners[0]
                current_streak = 1
            elif len(winners) > 1:
                # This means there's a tie. For simplicity, assume ties increment the current winner's streak
                print('Multiple winners detected between %s and %s; continuing previous winner streak' % (previous_game, game))
                current_streak = current_streak + 1
            else:
                # If the winner is also the current winner, increment streak and keep going
                current_streak = current_streak + 1

            # Advance state tracking because iterators are too confusing to deal with
            previous_game = game

        # Write final streak
        streaks[current_winner] = current_streak
        return streaks


streaks = get_streaks(input_path)
streak_length_by_frequency = pd.Series(streaks).value_counts().sort_index()

window = 6
greater_than_equal_to_length_occurrences = streak_length_by_frequency.iloc[::-1].cumsum().iloc[::-1]
print(greater_than_equal_to_length_occurrences)

next_win_chance = pd.Series(np.divide(greater_than_equal_to_length_occurrences.values[1 : window + 1], greater_than_equal_to_length_occurrences.values[0 : window]))
next_win_chance.index = range(1, len(next_win_chance) + 1)
print(next_win_chance)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16,8))

# Graph the distribution of streaks
bars = ax1.bar(streak_length_by_frequency.index, streak_length_by_frequency.values, color ='dodgerblue', width = 0.9)
ax1.bar_label(bars)
ax1.set(xlabel='Length of Streak', ylabel='Number of Occurrences')
ax1.set_title('Length of Streaks on Jepoardy')

# Graph the conditional probability of a N-streak winner winning
bars = ax2.bar(next_win_chance.index, next_win_chance.values, color ='dodgerblue', width = 0.9)
ax2.bar_label(bars)
ax2.set(xlabel='Length of Streak', ylabel='% Chance of Next Win')
ax2.set_title('Chance of Continuing Streak')

plt.show()
