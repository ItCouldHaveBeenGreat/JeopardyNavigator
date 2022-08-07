import csv
import json
import pandas as pd
import gzip
import os.path
import time

csv_path = 'data/jeopardy.csv'
gzip_csv_path = 'data/jeopardy.csv.gz'

def use_pandas():
    dataframe = pd.read_json("data/jeopardy.json")
    dataframe.to_csv("data/jeopardy.csv")


def dehydrate():
    with open(csv_path, 'r', encoding='utf8') as in_file, open(gzip_csv_path, 'w') as out_file:
        out_file.write(gzip.compress(in_file.read()))


def hydrate_if_required():
    if not os.path.exists(csv_path):
        with open(gzip_csv_path, 'rb') as in_file, open(csv_path, 'w', encoding='utf8') as out_file:
            out_file.write(gzip.decompress(in_file.read()).decode('utf-8'))


def hydrate_dataframe():
    df = pd.read_csv(csv_path)
    # Filter dataframe to only include questions from after 2020
    df = df[(df['air_date'] > '2015-01-01') & (df['air_date'] < '2021-08-13')]
    pd.set_option('display.max_rows', 500)
    pd.set_option('display.min_rows', 500)
    pd.set_option('display.max_columns', 500)
    return df


def get_category_distribution(df):
    # Display an order list of category frequency
    print(df['category'].value_counts())


def query(df):
    # Pick a random category and a random air date
    seed_question = df.sample(n=1).iloc[0]
    questions = df[(df['air_date'] == seed_question.air_date) & (df['category'] == seed_question.category)]

    print('NEW ROUND')
    input('%s, %s' % (seed_question.category, seed_question.air_date))
    for index, question in questions.iterrows():
        print('-----------------------')
        print('QUESTION: %s: %s' % (question.value, question.answer)) # Unclear why this field is named this way...
        # time.sleep(question.answer.count(' ') * 0.33 + 1)
        input('GO!')
        input('ANSWER: %s' % question.question)  # Unclear why this field is named this way...


# Yes, I write java.
def main():
    # dehydrate() # this is busted
    df = hydrate_dataframe()
    # get_category_distribution(df)
    query(df)


main()
