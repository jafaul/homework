from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, class_mapper

from .config import config

engine = create_engine(config.DB_URL, echo=True)


class Base(DeclarativeBase):

    def as_dict(self, include_relationships: bool = False):

        data = {
            column.key: getattr(self, column.key)
            for column in class_mapper(self.__class__).columns
        }

        if include_relationships:
            for relationship in class_mapper(self.__class__).relationships:
                related = getattr(self, relationship.key)
                if relationship.uselist:
                    data[relationship.key] = [
                        obj.as_dict() for obj in related
                    ]
                else:
                    data[relationship.key] = related.as_dict()

        return data


# Base.metadata.create_all(engine)
