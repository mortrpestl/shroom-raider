def import_entities(names: set):
    imported = {}
    for name in names:
        module = __import__(f"Classes.Entities.{name}", fromlist=[name])
        entity_class = getattr(module, name)
        imported[name] = entity_class
    return imported