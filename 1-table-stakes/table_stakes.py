
import pandas as pd
import numpy as np
import datetime as dt
import subprocess as sp
import warnings

from pathlib import Path
from typing import List, Dict, Union

class QvrRuntimeError(Exception):
    """ Exception raised when NoSuchBucket or NoSuchKey are encountered from S3. """
    pass

def is_palindrome(word: str) -> bool:
    """ Returns true if a word reads the same backward as forward. """
    return word.lower() == word.lower()[::-1]
    
def filter_word_list(words: List[str], allow_list: List[str]) -> List[str]:
    """ Returns a filtered list of words. """
    return [word for word in words if word in allow_list]

def calculate_mode(l: List[Union[int, float, str]]) -> List[Union[int, float, str]]:
    """ Returns a list of the most frequently occurring values (i.e. the modes), unless:
        1. the data is empty;
        2. the distribution is completely uniform;

        ...in which case there is no mode and an empty list is returned. 
    """

    max = 0
    freq_count = {}
    for element in l:
        if element not in freq_count:
            freq_count[element] = 1  
        else:
            freq_count[element] += 1
        
        if max < freq_count[element]:
            max = freq_count[element]
    
    mode = [k for k,v in freq_count.items() if v == max]

    if not l:
        warnings.warn("Data empty; no mode.", UserWarning)
    elif max == 1 and len(freq_count) >= 1:
        warnings.warn("Distribution completely uniform; no mode.", UserWarning)
        mode.clear()

    return mode


def calculate_mode_deprecated(l: List[Union[int, float, str]]) -> Union[int, float, str]:
    """ Calculates unimodal mode. 
        - Does not handle uniform distribution edge case
        - Return value unimodal and order dependent    
    """

    max = None
    count = {}
    for x in l:
        if x not in count:
            count[x] = 0
        count[x] += 1

        if not max or count[x] > count[max]:
            max = x

    return max

def put_to_s3(file: str, s3_bucket: str):
    """ Copy file to AWS S3 via CLI. """
    try:
        output = sp.check_output(["aws", "s3", "cp", file, f"s3://{s3_bucket}/{file}"], stderr=sp.STDOUT, shell=True)
        return output

    except sp.CalledProcessError as e:
        error_message = e.output if isinstance(e.output, str) else e.output.decode("utf-8")
        if "NoSuchKey" in error_message:
            raise QvrRuntimeError("An error occurred (NoSuchKey)...the specified key does not exist.")
        elif "NoSuchBucket" in error_message: 
            raise QvrRuntimeError("An error occurred (NoSuchBucket)...the specified bucket does not exist.")
        else:
            return error_message

def missed_midterm(df: pd.DataFrame) -> bool:
    """ Check to see if a given student missed the midterm """
    return pd.isnull(df["midterm_score"])

def missed_final(df: pd.DataFrame) -> bool:
    """ Check to see if a given student missed the final """
    return pd.isnull(df["final_score"])

def missed_both_exams(df: pd.DataFrame) -> bool:
    """ Check to see if a given student missed both the midterm AND final """
    return pd.isnull(df["midterm_score"]) and pd.isnull(df["final_score"])

def zero_participation(df: pd.DataFrame) -> bool:
    """ Check to see if a given student received zero for participation """
    return df["participation_score"] == 0

def assign_grade(df: pd.DataFrame) -> str:
    """ Given a composite score and all flags checking for idiosyncratic factors, assign each student a grade """
    if df["zero_participation"] == True:
        return "F"
    elif df["missed_both_exams"] == True:
        return "F"
    elif df["composite_score"] <= 35:
        return "F"
    elif 35 < df["composite_score"] <= 59:
        return "D"
    elif 59 < df["composite_score"] <= 69:
        return "C"
    elif 69 < df["composite_score"] <= 89:
        return "B"
    else:
        return "A"

def pad_distribution(actual_distribution: Dict[str, int]) -> Dict[str, int]:
    """ For the actual grade distribution, pad any gaps with zero """
    model_distribution = {
        "A": 0,
        "B": 0,
        "C": 0,
        "D": 0,
        "F": 0
    }
    return {**model_distribution, **actual_distribution}

def get_raw_scores(class_roster: List[str], exam_attendance_rate: float = np.random.randint(100)/100) -> pd.DataFrame:
    """ Return a dataframe containing the raw scores of the class.

        - class_roster = list of student names
        - exam_attendance_rate = number between 0 and 1 that determines the probability a student takes a midterm or final

    """
    # Create an empty DataFrame
    df = pd.DataFrame(columns=["midterm_percentage", "final_percentage", "participation"],
                      index=class_roster
                      ).rename_axis("students")

    # Assign random values to midterm_percentage and final_percentage; although not specified, exam scores are assumed to be continuous
    df[["midterm_percentage", "final_percentage"]] = np.random.uniform(low=0, high=100, size=(len(df), 2))

    # Use a mask to randomly determine whether a student missed an exam
    missed_exam = np.random.random(df.shape) < (1-exam_attendance_rate)
    df.mask(missed_exam, inplace=True)

    # Assign random values to participation; although not specified, participation scores are assumed to be discrete
    df["participation"] =  np.random.randint(low=0, high=10, size=len(df))

    # Reset index to meet format specifications
    df.reset_index(level="students", inplace=True)

    return df

def get_weighted_scores(raw_scores: pd.DataFrame) -> pd.DataFrame:
    """ Return a dataframe containing normalized scores weighted by assignment

        Certain other rules unique to the grading scheme are also incorporated:
        - Students who received a zero in participation autmatically receive an F for the class
        - Students who missed both the final and midterm receive an F for the class, irrespective of participation
        - Student who miss either the midterm or the final, but not both, receives 75% of the grade they got for the exam they did take

    """

    # Normalize raw scores
    normalized_scores = raw_scores
    normalized_scores.set_index("students", inplace=True)
    normalized_scores[["midterm_percentage","final_percentage"]] = raw_scores[["midterm_percentage","final_percentage"]].div(100, axis=0)
    normalized_scores["participation"] = raw_scores["participation"].div(10, axis=0)

    # Weight by assignment
    weights = pd.DataFrame(
            data=[[20, 40, 40] for i in range(len(normalized_scores))],
            columns=["midterm_weight", "final_weight", "participation_weight"],
            index=normalized_scores.index.tolist()
        ).rename_axis("students")
   
    weighted_scores = normalized_scores.mul(weights.values)
    weighted_scores.columns = ["midterm_score", "final_score", "participation_score"]

    # Check for and apply idiosyncratic factors
    weighted_scores["missed_midterm"] = weighted_scores.apply(missed_midterm, axis=1)
    weighted_scores["missed_final"] = weighted_scores.apply(missed_final, axis=1)
    weighted_scores["missed_both_exams"] = weighted_scores.apply(missed_both_exams, axis=1)
    weighted_scores["zero_participation"] = weighted_scores.apply(zero_participation, axis=1)

    # A student who misses either the midterm or the final, but not both, receives 75% of the grade they got for the exam they did take
    weighted_scores["midterm_score"] = np.where((weighted_scores["missed_midterm"]) == True, (weighted_scores["final_score"] * 0.75 / 40) * 20, weighted_scores["midterm_score"])
    weighted_scores["final_score"] = np.where((weighted_scores["missed_final"])  == True, (weighted_scores["midterm_score"] * 0.75 / 20) * 40, weighted_scores["final_score"])

    # Calculate composite score
    weighted_scores.insert(loc=3, column="composite_score", value=weighted_scores[["midterm_score", "final_score", "participation_score"]].sum(axis=1))
    
    # Assign grade
    weighted_scores.insert(loc=len(weighted_scores.columns), column="calculated_grade", value=weighted_scores.apply(assign_grade, axis=1))
    
    return weighted_scores

def get_grade_distribution(weighted_scores: pd.DataFrame) -> pd.DataFrame:
    """ Return a dataframe containing the distribution of grades for a given class """

    # Generate distribution; pad with missing values
    grade_distribution = pd.DataFrame.from_dict(
            pad_distribution(weighted_scores["calculated_grade"].value_counts().to_dict()),
            orient="index",
            columns=["count"]
    ).rename_axis("grade").reset_index()

    return grade_distribution

if __name__ == "__main__":
    
    # Hello World! (is my environment working?)
    print(is_palindrome(word="hannah"))
    print(is_palindrome(word="test"))

    # Filtering an array (easy)
    print(filter_word_list(words=["A", "B", "C"], allow_list=["A", "B"]))

    # Misfiring mode (easy)
    print(calculate_mode(l=[1,1,2,2,3,3,4])) 
    print(calculate_mode(l=["C", "C", "B", "A", "A"])) 
    print(calculate_mode_deprecated(l=[1,2,3,4])) # Does not handle uniform distribution edgecase
    print(calculate_mode_deprecated(l=[2, 1, 3, 3, 2, 1])) # Unimodal return value order dependent
   
    # Testing an external service (medium)
    # print(put_to_s3(file="test.csv", s3_bucket="test_bucket")) # Test missing bucket error

    # Teacher's best friend (hard)
    raw_scores = get_raw_scores(class_roster=["Alice", "Bob", "Calvin", "Dora", "Evelyn", "Farris", "George", "Talin", "Kamil"], 
                                exam_attendance_rate=100)
    print(raw_scores)

    weighted_scores = get_weighted_scores(raw_scores)
    print(weighted_scores)

    expected_output = get_grade_distribution(weighted_scores)
    print(expected_output)
