def import_entities(names: set):
    """Imports all given entities

    Args:
        names: The classnames of entities to be imported

    Returns:
        A dictionary containing all the imported modules

    """
    imported = {}
    for name in names:
        module = __import__(f"Classes.Entities.{name}", fromlist=[name])
        entity_class = getattr(module, name)
        imported[name] = entity_class
    return imported
