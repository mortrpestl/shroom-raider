
#! AI was prompted to ask with finding which attributes pertain to parameter

def pytest_collection_modifyitems(items):
    """
    Modify collected test items so that only the human-readable parametrize ID is shown.
    """
    for item in items:
        # Check if the test was parametrized
        if hasattr(item, "callspec"):
            item._nodeid = str(item.callspec.id)  # set nodeid to your id param
