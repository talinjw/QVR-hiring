
import pandas as pd
import datetime as dt

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


def grade_distribution(raw_scores):

    pass


def base64_from_hex(hex):

    pass
