from collections.abc import Sequence

from _pytest.nodes import Item


def pytest_collection_modifyitems(items: Sequence[Item]) -> None:
    """Modify collected test items to display only the human-readable parametrize ID."""
    for item in items:
        if hasattr(item, "callspec"):
            item._nodeid = str(item.callspec.id)  # noqa: SLF001
