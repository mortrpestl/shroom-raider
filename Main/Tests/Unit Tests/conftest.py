import os

COUNTER = 1


def pytest_itemcollected(item):
    """
    Converts test display to a numbered, human-readable format.
    """
    global COUNTER
    if item.name.startswith("test_"):
        # Get the file base name, remove test_ and .py
        file_base = os.path.basename(item.fspath)
        file_base = file_base.replace("test_", "").replace(".py", "").capitalize()

        readable_name = item.name[5:].replace("_", " ").capitalize()

        item._nodeid = f"{'Unit Test ' + str(COUNTER).zfill(3):^19} | {file_base:^24} | {readable_name:<90}"

        COUNTER += 1
