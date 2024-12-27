from database import Base


def serialize_list(objects: list[Base], *, include_relationships=False) -> list[dict]:
    return [obj.as_dict(include_relationships=include_relationships) for obj in objects]
