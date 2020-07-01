# Table Stakes

Functions for this challenge live in ```table_stakes.py```; tests should live in ```table_stakes_test.py```. For each question, implement (or correct) the associated function and write unit tests for them. We are relying on your unit tests to show us how you define and go about implementing problems, so please try to be thorough.

## Hello World! (is my environment working?)

```is_palindrome``` returns True if a string ```word``` is the same forward as it is backwards. Implement this function, and write unit tests for it.


## Filtering an array (easy)

```filter_word_list``` takes a list of words ```words```, and filters out the ones that contain words in ```allow_list```.


## Misfiring mode (easy)

```calculate_mode``` returns the mode of a list of numbers. Write exhaustive unit tests for this function and correct any errors they reveal.

How would you avoid this category of error?


## Testing an external service (medium)

Your co-worker has not heard of ```boto```, and has shoddily implemented a call to copy a local file to S3 using the function ```put_to_s3```.

Enhance the function to ensure that the function raises a ```QvrRuntimeError``` when the following errors are encountered from S3.

* ```NoSuchKey```
* ```NoSuchBucket```

(S3 errors definitions can be found [here](https://docs.aws.amazon.com/AmazonS3/latest/API/ErrorResponses.html).)

All other errors should be ignored.

Additionally provide unit tests that mock out the ```subprocess``` module and ensure that the function can be tested without actually spawning a subprocess.


## Teacher's best friend (hard)

Given a pandas dataframe ```raw_scores``` containing test percentages (out of 100) and participation rating (out of 10) for a class of students, implement a function ```grade_distribution``` which returns a dataframe showing the class grade distribution. Grade bands are as follows:

* A: 90-100
* B: 70-89
* C: 60-69
* D: 35-59
* F: < 35

Assignment weightings are as follows:

* 40% final exam
* 20% midterm
* 40% class participation

Some oddities in our grading scheme:

* Students with 0 participation grades automatically receive an F for the class. Students are guaranteed to have a participation grade.
* Missing tests are represented by ```np.NaN```
* Students missing both final and midterm receive an F regardless of participation.
* For the purpose of calculating grades, students who miss either the midterm or the final receive 75% of the grade they got for the test they did take.

```raw_scores``` will have the following format:

```python
    raw_scores = pd.DataFrame([
        ['Alice',  [0-100], [0-100], [0-10]],
        ['Bob',    [0-100], [0-100], [0-10]],
        ['Calvin', [0-100], [0-100], [0-10]],
        ['Dora',   [0-100], [0-100], [0-10]],
        ['Evelyn', [0-100], [0-100], [0-10]],
        ['Farris', [0-100], [0-100], [0-10]],
        ['George', np.NaN,  np.NaN,  [0-10]]
    ], columns=['student', 'participation', 'midterm_percentage', 'final_percentage'])
```

The returned grade distribution should look like this:

```python
    expected_output = pd.DataFrame([
        ['A', XX],
        ['B', XX],
        ['C', XX],
        ['D', XX],
        ['F', XX]
    ], columns=['grade', 'count'])
```

... where ```XX``` is the number of students achieving that grade
