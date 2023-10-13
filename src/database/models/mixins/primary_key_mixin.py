from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import BIGINT


class PrimaryKeyMixin:
    id = Column("id", BIGINT(), primary_key=True, autoincrement=True)
