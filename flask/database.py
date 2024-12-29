from sqlalchemy import URL, create_engine
from sqlalchemy.orm import DeclarativeBase, class_mapper

from config import config

url_object = URL.create(
    "postgresql+psycopg2",
    username=config.DB_USERNAME,
    password=config.DB_PASSWORD,
    host=config.DB_HOST,
    database=config.DB_NAME,
    port=config.DB_PORT,
)

engine = create_engine(url_object, echo=True)


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
                        obj.as_dict() if hasattr(obj, "as_dict") else repr(obj)
                        for obj in related
                    ]
                else:
                    data[relationship.key] = (
                        related.as_dict() if hasattr(related, "as_dict") else repr(related)
                    )

        return data

Base.metadata.create_all(engine)
