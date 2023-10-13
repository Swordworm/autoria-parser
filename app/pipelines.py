from logging import Logger, getLogger
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert

from app.database.models import Car
from app.items import CarItem
from app.utils import get_engine


class CarDBPipeline:
    def __init__(self, db_url: str, log_level: str = "INFO") -> None:
        self.engine = get_engine(db_url)
        self.session = sessionmaker(self.engine)
        self.logger = getLogger(self.__class__.__name__)
        self.logger.setLevel(log_level)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            db_url=crawler.settings.get("DB_URL"),
            log_level=crawler.settings.get("LOG_LEVEL"),
        )

    def process_item(self, item, spider) -> CarItem:
        with self.session() as session:
            car_dict = dict(item)

            insert_stmt = insert(Car).values(car_dict)
            upsert_stmt = insert_stmt.on_conflict_do_update(
                index_elements=[Car.url],
                set_={
                    "title": insert_stmt.excluded.title,
                    "price_usd": insert_stmt.excluded.price_usd,
                    "odometer": insert_stmt.excluded.odometer,
                    "username": insert_stmt.excluded.username,
                    "image_url": insert_stmt.excluded.image_url,
                    "images_count": insert_stmt.excluded.images_count,
                    "car_number": insert_stmt.excluded.car_number,
                    "car_vin": insert_stmt.excluded.car_vin,
                    "phone_number": insert_stmt.excluded.phone_number,
                },
            )
            session.execute(upsert_stmt)
            session.commit()
        self.logger.info(f"Saved to database {item['title']} {item['url']} ")

        return item
