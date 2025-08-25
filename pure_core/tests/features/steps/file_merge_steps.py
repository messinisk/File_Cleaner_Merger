import os
import tempfile
from behave import given, when, then
from pure_core.file_sync_manager import merge_by_version_date, merge_random_conflict, delete_duplicates

@given('υπάρχουν δύο αρχεία "{file_a}" και "{file_b}" με διαφορετικές ημερομηνίες δημιουργίας') # pyright: ignore[reportCallIssue]
def step_impl(context, file_a, file_b): # pyright: ignore[reportRedeclaration]
    context.tempdir = tempfile.TemporaryDirectory()
    context.file_a_path = os.path.join(context.tempdir.name, file_a)
    context.file_b_path = os.path.join(context.tempdir.name, file_b)

    with open(context.file_a_path, "w") as f:
        f.write("Περιεχόμενο παλιού αρχείου")
    with open(context.file_b_path, "w") as f:
        f.write("Περιεχόμενο νέου αρχείου")

    # Αλλάζουμε την ημερομηνία δημιουργίας
    os.utime(context.file_a_path, (1000000, 1000000))
    os.utime(context.file_b_path, (2000000, 2000000))

@when('εκτελείται η merge_by_version_date για αυτά τα αρχεία') # pyright: ignore[reportCallIssue]
def step_impl(context): # pyright: ignore[reportRedeclaration]  # noqa: F811
    context.merge_result = merge_by_version_date(
        {"path": context.file_a_path}, {"path": context.file_b_path}
    )

@then('το αρχείο με την παλαιότερη ημερομηνία πρέπει να περιέχει το περιεχόμενο του νεότερου') # pyright: ignore[reportCallIssue]
def step_impl(context): # pyright: ignore[reportRedeclaration]  # noqa: F811
    with open(context.file_a_path, "r") as f:
        content = f.read()
    assert "Περιεχόμενο νέου αρχείου" in content

@then('το νεότερο αρχείο πρέπει να έχει διαγραφεί') # pyright: ignore[reportCallIssue]
def step_impl(context): # pyright: ignore[reportRedeclaration]  # noqa: F811
    assert not os.path.exists(context.file_b_path)

@given('υπάρχουν δύο αρχεία "{file1}" και "{file2}"') # pyright: ignore[reportCallIssue]
def step_impl(context, file1, file2): # pyright: ignore[reportRedeclaration]  # noqa: F811
    context.tempdir = tempfile.TemporaryDirectory()
    context.file1_path = os.path.join(context.tempdir.name, file1)
    context.file2_path = os.path.join(context.tempdir.name, file2)
    with open(context.file1_path, "w") as f:
        f.write("Περιεχόμενο 1")
    with open(context.file2_path, "w") as f:
        f.write("Περιεχόμενο 2")

@when('εκτελείται η merge_random_conflict για αυτά τα αρχεία') # type: ignore
def step_impl(context):  # pyright: ignore[reportRedeclaration] # noqa: F811
    context.merge_result = merge_random_conflict(
        {"path": context.file1_path}, {"path": context.file2_path}
    )

@then('ένα από τα δύο αρχεία πρέπει να περιέχει το περιεχόμενο του άλλου') # pyright: ignore[reportCallIssue]
def step_impl(context): # pyright: ignore[reportRedeclaration]  # noqa: F811
    content1 = open(context.file1_path).read() if os.path.exists(context.file1_path) else ""
    content2 = open(context.file2_path).read() if os.path.exists(context.file2_path) else ""
    combined = content1 + content2
    assert "Περιεχόμενο 1" in combined
    assert "Περιεχόμενο 2" in combined

@then('το άλλο αρχείο πρέπει να έχει διαγραφεί') # pyright: ignore[reportCallIssue]
def step_impl(context): # pyright: ignore[reportRedeclaration]  # noqa: F811
    assert os.path.exists(context.file1_path) != os.path.exists(context.file2_path)

@given('υπάρχουν τρία αρχεία με ίδιο περιεχόμενο "{file1}", "{file2}", "{file3}"') # pyright: ignore[reportCallIssue]
def step_impl(context, file1, file2, file3): # pyright: ignore[reportRedeclaration]  # noqa: F811
    context.tempdir = tempfile.TemporaryDirectory()
    context.files = []
    for fname in [file1, file2, file3]:
        fpath = os.path.join(context.tempdir.name, fname)
        with open(fpath, "w") as f:
            f.write("Διπλό περιεχόμενο")
        context.files.append({"path": fpath})

@when('εκτελείται η delete_duplicates για αυτά τα αρχεία') # pyright: ignore[reportCallIssue]
def step_impl(context): # pyright: ignore[reportRedeclaration]  # noqa: F811
    context.delete_result = delete_duplicates(context.files)

@then('πρέπει να μείνει μόνο το πρώτο αρχείο') # pyright: ignore[reportCallIssue]
def step_impl(context):  # noqa: F811
    remaining = [f["path"] for f in context.files if os.path.exists(f["path"])]
    assert remaining == [context.files[0]["path"]]
