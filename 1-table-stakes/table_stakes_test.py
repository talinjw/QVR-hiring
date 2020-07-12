import datetime as dt
import pandas as pd
import numpy as np

import warnings

import unittest
from unittest import TestCase
from unittest.mock import patch
from subprocess import CalledProcessError

import table_stakes

class TestIsPalindrome(TestCase):

    def test_is_palindrome_case_true(self):
        self.assertTrue(table_stakes.is_palindrome("tattarrattat"))

    def test_is_palindrome_case_false(self):
        self.assertFalse(table_stakes.is_palindrome("not palindrome"))

    def test_is_palindrome_case_insensitive(self):
        self.assertTrue(table_stakes.is_palindrome("HaNnah"))

class TestFilterWordList(TestCase):

    def test_filter_word_list(self):
        filtered_list = table_stakes.filter_word_list(words=["word_1", "word_2"], allow_list=["word_2"])
        self.assertEqual(filtered_list, ["word_2"])

class TestCalculateMode(TestCase):

    def setUp(self):
        warnings.simplefilter("ignore", category=UserWarning)

    def test_calculate_mode_unimodal(self):
        mode = table_stakes.calculate_mode(l=[-1, 1, 2, 2, 3])
        self.assertCountEqual(mode, [2])

    def test_calculate_mode_multimodal(self):
        mode = table_stakes.calculate_mode(l=[-3, -3, -1, 2, 5.5, 5.5, 7, 9, 9])
        self.assertCountEqual(mode, [-3, 5.5, 9])

    def test_calculate_mode_set_of_one(self):
        mode = table_stakes.calculate_mode(l=[1])
        self.assertCountEqual(mode, [])

    def test_calculate_mode_uniform_distribution(self):
        mode = table_stakes.calculate_mode(l=[1, 2, 3, 4])
        self.assertCountEqual(mode, [])

    def test_calculate_mode_empty_dataset(self):
        mode = table_stakes.calculate_mode(l=[])
        self.assertCountEqual(mode, [])

    def test_calculate_mode_nominal(self):
        mode = table_stakes.calculate_mode(l=["AB", "AB", "AC", "AC", "AD"])
        self.assertCountEqual(mode, ["AB", "AC"])

    def test_calculate_mode_order_agnostic(self):
        mode = table_stakes.calculate_mode(l=["B", "B", -1, -1, "A", "A", 1, 1])
        self.assertCountEqual(mode, ["A", 1, "B", -1])  

class TestPutToS3(TestCase):

    @patch("subprocess.check_output", return_value="upload: .\test.csv to s3://test_bucket/test.csv", autospec=True)
    def test_put_to_s3_with_output(self, mock_subprocess):
        result = table_stakes.put_to_s3(file="test.csv", s3_bucket="test_bucket")
        self.assertEqual(result, mock_subprocess.return_value)
 
    @patch("subprocess.check_output")
    def test_put_to_s3_with_key_error(self, mock_subprocess):
        mock_subprocess.side_effect = CalledProcessError(returncode=255, cmd="any cmd will do", output="NoSuchKey")
        with self.assertRaises(table_stakes.QvrRuntimeError):
            table_stakes.put_to_s3(file="test.csv", s3_bucket="test_bucket")

    @patch("subprocess.check_output")
    def test_put_to_s3_with_bucket_error(self, mock_subprocess):
        mock_subprocess.side_effect = CalledProcessError(returncode=255, cmd="any cmd will do", output="NoSuchBucket")
        with self.assertRaises(table_stakes.QvrRuntimeError):
            table_stakes.put_to_s3(file="test.csv", s3_bucket="test_bucket")

class TestClassGradeDistribution(TestCase):

    def test_get_raw_scores_meets_format_specification(self):
        class_roster = ["Alice", "Bob", "Calvin", "Dora", "Evelyn", "Farris", "George", "Talin", "Kamil"]
        exam_attendance_rate = 1
        raw_scores = table_stakes.get_raw_scores(class_roster=class_roster, exam_attendance_rate=exam_attendance_rate)
        
        midterm = raw_scores["midterm_percentage"]
        self.assertTrue((midterm.notnull().all()))
        self.assertTrue(len(midterm) == len(class_roster))
        self.assertTrue((midterm.between(0,100).all()))
        self.assertFalse((midterm < 0).all())
        self.assertFalse((midterm > 100).all())

        final = raw_scores["final_percentage"]
        self.assertTrue((final.notnull().all()))
        self.assertTrue(len(final) == len(class_roster))
        self.assertTrue((final.between(0,100).all()))
        self.assertFalse((final < 0).all())
        self.assertFalse((final > 100).all())

        participation = raw_scores["participation"]
        self.assertTrue(len(participation) == len(class_roster))
        self.assertTrue((participation.between(0,10).all()))
        self.assertFalse((participation < 0).all())
        self.assertFalse((participation > 10).all())

    def test_get_raw_scores_ensure_participation_rating(self):
        class_roster = ["Alice", "Bob", "Calvin", "Dora", "Evelyn", "Farris", "George", "Talin", "Kamil"]
        raw_scores_full_exam_attendance = table_stakes.get_raw_scores(class_roster=class_roster, exam_attendance_rate=1)
        raw_scores_zero_exam_attendance = table_stakes.get_raw_scores(class_roster=class_roster, exam_attendance_rate=0)
        raw_scores_random_exam_attendance = table_stakes.get_raw_scores(class_roster=class_roster)
        self.assertTrue((raw_scores_full_exam_attendance["participation"].notnull().all()))
        self.assertTrue((raw_scores_zero_exam_attendance["participation"].notnull().all()))
        self.assertTrue((raw_scores_random_exam_attendance["participation"].notnull().all()))

    def test_get_weighted_scores_ensure_that_zero_participation_gets_F(self):
        class_roster = ["Alice", "Bob", "Calvin", "Dora", "Evelyn", "Farris", "George", "Talin", "Kamil"]
        exam_attendance_rate = 1
        raw_scores = table_stakes.get_raw_scores(class_roster=class_roster, exam_attendance_rate=exam_attendance_rate)
        raw_scores["participation"] = 0
        weighted_scores = table_stakes.get_weighted_scores(raw_scores=raw_scores)
        self.assertTrue(((weighted_scores["participation_score"] == 0) & (weighted_scores["calculated_grade"] == "F")).all())

    def test_get_weighted_scores_ensure_that_missing_both_exams_gets_F_irrespective_of_participation(self):
        class_roster = ["Alice", "Bob", "Calvin", "Dora", "Evelyn", "Farris", "George", "Talin", "Kamil"]
        exam_attendance_rate = 0
        raw_scores = table_stakes.get_raw_scores(class_roster=class_roster, exam_attendance_rate=exam_attendance_rate)
        raw_scores["participation"] = 10
        weighted_scores = table_stakes.get_weighted_scores(raw_scores=raw_scores)
        self.assertTrue(((weighted_scores["midterm_score"].isnull()) & (weighted_scores["final_score"].isnull()) & (weighted_scores["calculated_grade"] == "F")).all())

    def test_get_weighted_scores_ensure_missing_midterm_score_equal_to_75_percent_of_final_and_then_normalized_by_midterm_assignment_weight(self):
        class_roster = ["Alice", "Bob", "Calvin", "Dora", "Evelyn", "Farris", "George", "Talin", "Kamil"]
        exam_attendance_rate = 1
        raw_scores = table_stakes.get_raw_scores(class_roster=class_roster, exam_attendance_rate=exam_attendance_rate)
        raw_scores["midterm_percentage"] = np.nan
        weighted_scores = table_stakes.get_weighted_scores(raw_scores=raw_scores)
        self.assertTrue(weighted_scores["midterm_score"].equals(weighted_scores["final_score"] * 0.75 / 40 * 20))

    def test_get_weighted_scores_ensure_missing_final_score_equal_to_75_percent_of_midterm_and_then_normalized_by_final_assignment_weight(self):
        class_roster = ["Alice", "Bob", "Calvin", "Dora", "Evelyn", "Farris", "George", "Talin", "Kamil"]
        exam_attendance_rate = 1
        raw_scores = table_stakes.get_raw_scores(class_roster=class_roster, exam_attendance_rate=exam_attendance_rate)
        raw_scores["final_percentage"] = np.nan
        weighted_scores = table_stakes.get_weighted_scores(raw_scores=raw_scores)
        self.assertTrue(weighted_scores["final_score"].equals(weighted_scores["midterm_score"] * 0.75 / 20 * 40))

    def test_get_weighted_scores_ensure_that_all_students_get_a_grade(self):
        class_roster = ["Alice", "Bob", "Calvin", "Dora", "Evelyn", "Farris", "George", "Talin", "Kamil"]      
        weighted_scores_full_attendance = table_stakes.get_weighted_scores(raw_scores=table_stakes.get_raw_scores(class_roster=class_roster, exam_attendance_rate=1))
        weighted_scores_zero_attendance = table_stakes.get_weighted_scores(raw_scores=table_stakes.get_raw_scores(class_roster=class_roster, exam_attendance_rate=0))
        weighted_scores_random_attendance = table_stakes.get_weighted_scores(raw_scores=table_stakes.get_raw_scores(class_roster=class_roster))
        self.assertTrue((weighted_scores_full_attendance["calculated_grade"].notnull().all()))
        self.assertTrue((weighted_scores_zero_attendance["calculated_grade"].notnull().all()))
        self.assertTrue((weighted_scores_random_attendance["calculated_grade"].notnull().all()))

    def test_get_grade_distribution_ensure_count_equal_to_number_of_weighted_scores(self):
        class_roster = ["Alice", "Bob", "Calvin", "Dora", "Evelyn", "Farris", "George", "Talin", "Kamil"]
        exam_attendance_rate = 1
        raw_scores = table_stakes.get_raw_scores(class_roster=class_roster, exam_attendance_rate=exam_attendance_rate)
        weighted_scores = table_stakes.get_weighted_scores(raw_scores=raw_scores)
        grade_distribution = table_stakes.get_grade_distribution(weighted_scores=weighted_scores)
        self.assertEqual(grade_distribution["count"].sum(), len(weighted_scores))

if __name__ == "__main__":
    unittest.main()