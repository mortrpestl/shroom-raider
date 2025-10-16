def import_entities(names: set):
    """
    Imports specific classes whose names are in the given set parameter 
    """
    imported = {}
    for name in names:
        module = __import__(f"Classes.Entities.{name}", fromlist=[name])
        entity_class = getattr(module, name)
        imported[name] = entity_class
    return imported