from pathlib import Path

from _pytest.nodes import Item

COUNTER = 1


def pytest_itemcollected(item: Item) -> None:
    """Convert test display to a numbered, human-readable format."""
    global COUNTER  # noqa: PLW0603
    if item.name.startswith("test_"):
        file_base = Path(item.fspath).name
        file_base = file_base.replace("test_", "").replace(".py", "").capitalize()

        readable_name = item.name[5:].replace("_", " ").capitalize()

        item._nodeid = (  # noqa: SLF001
            f"{'Unit Test ' + str(COUNTER).zfill(3):^19} | "
            f"{file_base:^24} | "
            f"{readable_name:<90}"
        )

        COUNTER += 1
