from database import Base


def serialize_list(
    objects: list[Base], *, include_relationships=False, exclude=tuple()
) -> list[dict]:
    return [
        {
            k: v
            for k, v in obj.as_dict(include_relationships=include_relationships).items()
            if k not in exclude
        }
        for obj in objects
    ]
