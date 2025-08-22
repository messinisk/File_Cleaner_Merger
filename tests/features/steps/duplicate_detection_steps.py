import os
import tempfile
from behave import given, when, then   # <-- σωστό import
from pure_core import duplicate_detector


@given("υπάρχει ένας φάκελος με δύο αρχεία που έχουν το ίδιο περιεχόμενο") # pyright: ignore[reportCallIssue]
def step_given_duplicate_files(context):
    context.test_dir = tempfile.mkdtemp()
    file1 = os.path.join(context.test_dir, "a.txt")
    file2 = os.path.join(context.test_dir, "b.txt")
    with open(file1, "w") as f:
        f.write("hello world")
    with open(file2, "w") as f:
        f.write("hello world")
    context.files = [file1, file2]


@given("υπάρχει ένας άδειος φάκελος") # pyright: ignore[reportCallIssue]
def step_given_empty_dir(context):
    context.test_dir = tempfile.mkdtemp()


@when("εκτελείται η inspect_directory_state στον φάκελο") # pyright: ignore[reportCallIssue]
def step_when_inspect(context):
    context.result = duplicate_detector.inspect_directory_state(context.test_dir)


@then("πρέπει να επιστραφούν μεταδεδομένα και να εντοπιστεί ότι υπάρχει ομάδα διπλοτύπων") # pyright: ignore[reportCallIssue]
def step_then_duplicates_detected(context):
    assert len(context.result) == 2, f"Περίμενα 2 αρχεία, βρέθηκαν {len(context.result)}"
    grouped = duplicate_detector.group_files_by_hash(context.result)
    duplicates = [files for files in grouped.values() if len(files) > 1]
    assert len(duplicates) >= 1, "Δεν βρέθηκαν διπλότυπα"


@then("πρέπει να επιστραφεί κενή λίστα") # pyright: ignore[reportCallIssue]
def step_then_empty_list(context):
    assert context.result == [], f"Περίμενα [], βρέθηκε {context.result}"
