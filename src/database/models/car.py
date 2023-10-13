from sqlalchemy import Column
from database.models.base import Base
from database.models.mixins import PrimaryKeyMixin, TimestampMixin
from sqlalchemy.dialects.postgresql import VARCHAR, INTEGER, BIGINT, TEXT, SMALLINT


class Car(PrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "cars"

    url = Column(VARCHAR(length=768), nullable=False, index=True, unique=True)
    title = Column(VARCHAR(length=255), nullable=False, index=False, unique=False)
    price_usd = Column(INTEGER(), nullable=False, index=False, unique=False)
    odometer = Column(BIGINT(), nullable=False, index=False, unique=False)
    username = Column(BIGINT(), nullable=True, index=False, unique=False)
    image_url = Column(TEXT(), nullable=True, index=False, unique=False)
    images_count = Column(SMALLINT(), nullable=False, index=False, unique=False)
    car_number = Column(VARCHAR(length=255), nullable=True, index=False, unique=False)
    car_vin = Column(VARCHAR(length=255), nullable=True, index=False, unique=False)
    phone_number = Column(BIGINT(), nullable=False, index=False, unique=False)
