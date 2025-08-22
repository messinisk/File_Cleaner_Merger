import os
import tempfile
from behave import given, when, then
from pure_core import duplicate_detector

@given('υπάρχει ένας φάκελος με αρχεία "notes.txt", "__init__.py", ".gitignore", "report.xlsx"') # pyright: ignore[reportCallIssue]
def step_impl(context): # pyright: ignore[reportRedeclaration]
    context.test_dir = tempfile.mkdtemp()
    files = ["notes.txt", "__init__.py", ".gitignore", "report.xlsx"]
    for fname in files:
        with open(os.path.join(context.test_dir, fname), "w") as f:
            f.write(f"Test content for {fname}")

    context.all_files = files

@when('εκτελείται η collect_file_info στον φάκελο') # pyright: ignore[reportCallIssue]
def step_impl(context): # pyright: ignore[reportRedeclaration]  # noqa: F811
    context.result = duplicate_detector.collect_file_info(context.test_dir)

@then('η λίστα πρέπει να περιέχει μόνο τα "notes.txt" και "report.xlsx"') # pyright: ignore[reportCallIssue]
def step_impl(context): # pyright: ignore[reportRedeclaration]  # noqa: F811
    result_names = [f["name"] for f in context.result]
    assert "notes.txt" in result_names
    assert "report.xlsx" in result_names
    # επιβεβαιώνουμε ότι τα άλλα δεν υπάρχουν
    assert "__init__.py" not in result_names
    assert ".gitignore" not in result_names

@then('τα αρχεία "__init__.py" και ".gitignore" πρέπει να αγνοηθούν') # pyright: ignore[reportCallIssue]
def step_impl(context):  # noqa: F811
    # τα αγνοημένα αρχεία δεν πρέπει να υπάρχουν στο αποτέλεσμα
    result_names = [f["name"] for f in context.result]
    ignored_files = ["__init__.py", ".gitignore"]
    for fname in ignored_files:
        assert fname not in result_names
