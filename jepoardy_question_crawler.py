import csv
import json
import pandas as pd
import gzip
import os.path
import random
import time

csv_path = 'data/jeopardy.csv'
gzip_csv_path = 'data/jeopardy.csv.gz'


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
    df = df[(df['air_date'] > '2015-01-01') & (df['air_date'] < '2021-08-13')]

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
        time.sleep(question.answer.count(' ') * 0.25 + 1 + random.random() * 3)

        # Time how long it takes to buzz
        start_time = time.time()
        print('GO!', flush=True)
        wait_for_keypress()
        end_time = time.time()

        # Present answer
        print('ANSWER: %s' % question.question)  # Unclear why this field is named this way...
        print('SECONDS ELAPSED: %s' % round(end_time - start_time, 3), flush=True)


df = hydrate_dataframe()
print_category_distribution(df)
categories_of_interest = ['PHILOSOPHY', 'LITERARY CHARACTERS']
df = df[(df['category'].isin(categories_of_interest))]

while True:
    query(df)
