from sqlalchemy import Column, text
from sqlalchemy.dialects.postgresql import TIMESTAMP


class TimestampMixin:
    created_at = Column(
        "created_at",
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )
