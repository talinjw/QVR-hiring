
import pandas as pd
import datetime as dt
import subprocess as sp

def is_palindrome(word):

    return


def filter_word_list(words, allow_list):

    return


def calculate_mode(l):

    max = None
    count = {}
    for x in l:
        if x not in count:
            count[x] = 0
        count[x] += 1

        if not max or count[x] > count[max]:
            max = x

    return max


def put_to_s3(file, bucket):

    sp.check_output(['aws', 's3', 'cp', file, 's3://{0}/{1}'.format(bucket, file)])


def grade_distribution(raw_scores):

    pass
