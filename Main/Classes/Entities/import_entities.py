import sys
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

# * RUFF CHECKED: No errors (12/10/2025)


def import_entities(names: set[str]) -> dict[str, type[Any]]:
    """Import all given entity classes from classes.entities.

    Args:
        names: The classnames of entities to be imported

    Returns:
        A dictionary containing all the imported classes

    """
    imported: dict[str, type[Any]] = {}
    for name in names:
        module_name = name
        module = __import__(f"classes.entities.{module_name}", fromlist=[name])
        entity_class = getattr(module, name[0].upper() + name[1:])
        imported[name] = entity_class
    return imported
