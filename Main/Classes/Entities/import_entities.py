import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

def import_entities(names: set):
    """Imports all given entity classes from classes.entities.

    Args:
        names: The classnames of entities to be imported

    Returns:
        A dictionary containing all the imported classes
    """
    imported = {}
    for name in names:
        module_name = name.lower()
        module = __import__(f"classes.entities.{module_name}", fromlist=[name])
        entity_class = getattr(module, name)
        imported[name] = entity_class
    return imported
