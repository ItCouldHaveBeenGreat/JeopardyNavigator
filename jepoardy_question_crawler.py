import csv
import json
from enum import Enum

import pandas as pd
import gzip
import os.path
import random
import threading
import time
import tkinter.font as font
import tkinter as tk

csv_path = 'data/jeopardy.csv'
gzip_csv_path = 'data/jeopardy.csv.gz'


def pick_random_category(df):
    attempts = 0
    while attempts < 1000:
        seed_question = df.sample(n=1).iloc[0]
        questions_df = df[(df['air_date'] == seed_question.air_date) & (df['category'] == seed_question.category)]
        if len(questions_df) == 5:
            questions = questions_df.to_dict('records')
            # Fix values and daily doubles (values are adjusted if they were actually daily doubles in real life)
            for i, question in enumerate(questions):
                question['value'] = (i+1)*200
                question['daily_double'] = False
            return questions


class Game:
    """A simple example class"""
    class State(Enum):
        YOUR_TURN_TO_CHOOSE = 1
        READING_QUESTION = 2
        GO = 3
        CHECKING_ANSWER = 4
        REVEALING_ANSWER_PENDING = 5
        BOT_IS_CHOOSING = 6
        WAITING_FOR_BET = 7

    active_player = 1 # 1 is human, 2 and 3 are bots; 3 is defending champion
    active_question = (None, None) # an index tuple is dumb... but in a hurry
    has_question_been_used = []
    money_tallies = []
    state = State.YOUR_TURN_TO_CHOOSE
    categories = []

    question_buttons = []
    buzzer_cue_widgets = []
    money_widgets = []
    correct_widget = None
    incorrect_widget = None
    status_widget = None
    root = None

    BUZZ_LIGHT_WIDTH = 150
    BUZZ_LIGHT_HEIGHT = 1000
    BUTTON_WIDTH = 260
    BUTTON_HEIGHT = 150
    FRAME_HEIGHT = BUTTON_HEIGHT * 6
    WRAP_LENGTH = 250

    def __init__(self, question_dataframe):
        # Choose 6 categories of 5 questions
        # TODO: Choose distinct categories?
        self.categories.append(pick_random_category(question_dataframe))
        self.categories.append(pick_random_category(question_dataframe))
        self.categories.append(pick_random_category(question_dataframe))
        self.categories.append(pick_random_category(question_dataframe))
        self.categories.append(pick_random_category(question_dataframe))
        self.categories.append(pick_random_category(question_dataframe))

        # Select 1/2 questions to be a daily double in accordance to DD probability table

        # Instantiate bot players

        # Construct UI
        self.root = tk.Tk()
        self.root.configure(bg='black')
        self.IMPACT_FONT = font.Font(root=self.root, family='Impact', size=24, weight=font.BOLD)
        self.IMPACT_MEDIUM_FONT = font.Font(root=self.root, family='Impact', size=28, weight=font.BOLD)
        self.IMPACT_LARGE_FONT = font.Font(root=self.root, family='Impact', size=36, weight=font.BOLD)
        self.QUESTION_FONT = font.Font(root=self.root, family='Roman', size=12)

        self.__build_status_widget(self.root)
        self.__build_money_widgets(self.root)
        self.__build_buzzer_widgets(self.root)
        self.__build_question_buttons(self.root)
        self.__build_answer_widgets(self.root)

        # Start UI Loop in a thread
        ui_thread = threading.Thread(target = self.root.mainloop())
        ui_thread.start()


    def __handle_status_button_press(self):
        print("You did it!!")
        print(self.state)
        if self.state == self.State.GO:
            # The player has answered before any of the bots
            # Update the button to display the answer
            category_index = self.active_question[0]
            question_index = self.active_question[1]
            question = self.categories[category_index][question_index]
            button = self.question_buttons[category_index][question_index]
            button.configure(text=question['question'])
            print("You did it!!")

            # Check if they got the answer right
            # RIGHT: Add money, colorize button, set to YOUR_TURN_TO_CHOOSE
            # WRONG: Subtract money, poll bots in random order and transfer to


    def __handle_correct_button_press(self):
        print('TODO')


    def __handle_incorrect_button_press(self):
        print('TODO')


    def __handle_question_button_press(self, category_index, question_index):
        # TODO: Fast fail if we're in the wrong state
        if self.state == self.State.YOUR_TURN_TO_CHOOSE:
            self.__transition_question_reveal_to_go(category_index, question_index)


    def __transition_question_reveal_to_go(self, category_index, question_index):
        # Map from parameter to button
        question = self.categories[category_index][question_index]
        button = self.question_buttons[category_index][question_index]

        # TODO: Fast fail if button has been used

        # Display the question and start the timer...
        button.configure(text=question['answer'], font=self.QUESTION_FONT)
        self.state = self.State.READING_QUESTION
        self.active_question = (category_index, question_index)
        self.status_widget.configure(text='READING QUESTION')
        self.root.update_idletasks()

        # TODO: Calibrate the mean time to be as close to the show as possible while still leaving it random enough
        #       to force reactions
        wait_time = random.random() * 3 + question['answer'].count(' ') * 0.33 + 3
        print('Waiting for... %s' % wait_time)

        # TODO: Dump this into a thread
        time.sleep(wait_time)

        # TODO: Consider creating functions for each state transition
        self.state = self.State.GO
        self.status_widget.configure(text='GO!')
        for widget in self.buzzer_cue_widgets:
            widget.configure(bg='white')
        self.root.update_idletasks()
        # TODO: Trigger bot threads to see if they beat to the punch


    def __build_question_buttons(self, root):
        null_image = tk.PhotoImage(width=0, height=0)
        for i, category in enumerate(self.categories):
            category_name = category[0]['category']
            category_frame = tk.Frame(
                master=root,
                relief=tk.RAISED,
                borderwidth=1,
                width=self.BUTTON_WIDTH,
                height=self.FRAME_HEIGHT
            )
            category_frame.grid(row=2, column=i + 1)
            button = tk.Button(
                master=category_frame,
                image=null_image,
                compound="center",
                width=self.BUTTON_WIDTH,
                height=self.BUTTON_HEIGHT,
                bg="darkblue",
                fg="white",
                font=self.IMPACT_FONT,
                wraplength=self.WRAP_LENGTH,
            )
            button.configure(text="%s" % category_name)  # Using an image to fix the button size is terrible
            button.pack()
            self.question_buttons.append([])
            self.has_question_been_used.append([])

            for j, question in enumerate(category):
                category_frame.grid(row=j + 3, column=i + 1)
                button = tk.Button(
                    master=category_frame,
                    image=null_image,
                    compound="center",
                    width=self.BUTTON_WIDTH,
                    height=self.BUTTON_HEIGHT,
                    bg="darkblue",
                    fg="gold",
                    font=self.IMPACT_FONT,
                    wraplength=self.WRAP_LENGTH,
                    command=lambda cat_index=i, q_index=j: self.__handle_question_button_press(cat_index, q_index),
                )
                button.configure(text="$%s" % question['value'])  # Using an image to fix the button size is terrible

                self.question_buttons[i].append(button)
                self.has_question_been_used[i].append(False)
                button.pack()


    def __build_money_widgets(self, root):

        colors = ['lightgreen', 'lightblue', 'pink2']
        for i, color in enumerate(colors):
            money_frame = tk.Frame(
                master=root,
                background="darkblue",
                width=self.BUTTON_WIDTH * 3,
                height=self.BUTTON_HEIGHT,
            )
            money_frame.grid(row=1, column=i+2, columnspan=2)
            money_text = tk.Label(
                master=money_frame,
                text="0$",
                width=10,
                height=2,
                fg=color,
                bg="darkblue",
                font=self.IMPACT_FONT,
            )
            money_text.pack()
            self.money_widgets.append(money_text)


    def __build_status_widget(self, root):
        status_frame = tk.Frame(
            master=root,
            background="white",
        )
        status_frame.grid(row=0, column=0, columnspan=6)
        status_button = tk.Button(
            master=status_frame,
            text="YOUR TURN TO CHOOSE",
            width=62,
            height=2,
            fg="black",
            bg="gold",
            font=self.IMPACT_FONT,
            wraplength=1000,
            command=lambda: self.__handle_status_button_press()
        )
        status_button.pack()
        self.status_widget = status_button


    def __build_answer_widgets(self, root):
        correct_frame = tk.Frame(
            master=root,
            background="white",
        )
        correct_frame.grid(row=0, column=1)
        correct_button = tk.Button(
            master=correct_frame,
            text="RIGHT",
            width=3,
            height=2,
            fg="black",
            bg="gold",
            font=self.IMPACT_FONT,
            command=lambda: self.__handle_correct_button_press()
        )
        correct_button.pack()

        incorrect_frame = tk.Frame(
            master=root,
            background="white",
        )
        incorrect_frame.grid(row=0, column=2)
        incorrect_button = tk.Button(
            master=incorrect_frame,
            text="WRONG",
            width=3,
            height=2,
            fg="black",
            bg="gold",
            font=self.IMPACT_FONT,
            command=lambda: self.__handle_incorrect_button_press()
        )
        incorrect_button.pack()


    def __build_buzzer_widgets(self, root):
        left_buzz_light = tk.Frame(
            master=root,
            relief=tk.RAISED,
            borderwidth=1,
            height=self.BUZZ_LIGHT_HEIGHT,
            width=self.BUZZ_LIGHT_WIDTH,
            background="black",
        )
        left_buzz_light.grid(row=1, column=0, rowspan=7)
        self.buzzer_cue_widgets.append(left_buzz_light)
        right_buzz_light = tk.Frame(
            master=root,
            relief=tk.RAISED,
            borderwidth=1,
            height=self.BUZZ_LIGHT_HEIGHT,
            width=self.BUZZ_LIGHT_WIDTH,
            background="black",
        )
        right_buzz_light.grid(row=1, column=7, rowspan=7)
        self.buzzer_cue_widgets.append(right_buzz_light)



# TODO: Fix this
def dehydrate():
    with open(csv_path, 'r', encoding='utf8') as in_file, open(gzip_csv_path, 'w') as out_file:
        out_file.write(gzip.compress(in_file.read()))


# TODO: Fix this
def hydrate_if_required():
    if not os.path.exists(csv_path):
        with open(gzip_csv_path, 'rb') as in_file, open(csv_path, 'w', encoding='utf8') as out_file:
            out_file.write(gzip.decompress(in_file.read()).decode('utf-8'))


def flush_input():
    try:
        import sys, termios
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)
    except ImportError:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()


def hydrate_dataframe():
    df = pd.read_csv(csv_path)
    # Filter dataframe to only include questions from after 2015
    df = df[(df['air_date'] > '2021-01-01')]

    pd.set_option('display.max_rows', 500)
    pd.set_option('display.min_rows', 500)
    pd.set_option('display.max_columns', 500)
    return df


def print_category_distribution(df):
    # Display an order list of category frequency
    print('---------------------------------------------------')
    print(df['category'].value_counts())
    print('---------------------------------------------------')


def wait_for_keypress(prompt = ''):
    input(prompt)
    flush_input()


def query(df):
    # Pick a random category and a random air date
    seed_question = df.sample(n=1).iloc[0]
    questions = df[(df['air_date'] == seed_question.air_date) & (df['category'] == seed_question.category)]

    print('\n\n')
    print('---------------------------------')
    print('NEW ROUND')
    print('TOPIC: %s, %s' % (seed_question.category, seed_question.air_date), flush=True)
    print('---------------------------------')
    for index, question in questions.iterrows():
        # Present question when player signals readiness
        wait_for_keypress('--hit enter to continue--')
        print('-----------------------')
        print('QUESTION: %s: %s' % (question.value, question.answer)) # Unclear why this field is named this way...

        # Sleep for a semi-random interval
        #time.sleep(question.answer.count(' ') * 0.25 + 1 + random.random() * 3)

        # Time how long it takes to buzz
        start_time = time.time()
        print('GO!', flush=True)
        #wait_for_keypress()
        end_time = time.time()

        # Present answer
        print('ANSWER: %s' % question.question)  # Unclear why this field is named this way...
        print('SECONDS ELAPSED: %s' % round(end_time - start_time, 3), flush=True)


def simple_iteration():
    df = hydrate_dataframe()
    print_category_distribution(df)
    categories_of_interest = ['LITERATURE']
    df = df[(df['category'].isin(categories_of_interest))]

    while True:
        query(df)


df = hydrate_dataframe()
Game(df)
