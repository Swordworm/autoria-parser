from datetime import datetime
from functools import cached_property
import json
from logging import getLogger
import os
from typing import Any

from scrapy.commands import ScrapyCommand
from scrapy.utils.project import get_project_settings
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from app.database.models import Car

from app.utils import get_engine


class Exporter(ScrapyCommand):
    chunk_size: int = 1000

    def __init__(self):
        super().__init__()
        self.settings = get_project_settings()
        self.engine = get_engine(self.settings["DB_URL"])
        self.session = sessionmaker(self.engine)
        self.logger = getLogger(self.__class__.__name__)
        self.logger.setLevel(self.settings["LOG_LEVEL"])
        self.timestamp = datetime.now()

    @cached_property
    def export_path(self) -> str:
        subdir = self.timestamp.strftime("%d%m%Y%H%M%S")
        subdir_path = os.path.join(self.settings["EXPORT_DIR"], subdir)
        os.makedirs(subdir_path, exist_ok=True)
        return subdir_path

    def short_desc(self) -> str:
        return "Export cars data"

    def run(self, args, opts):
        self.logger.info(f"Starting export to {self.export_path}")
        offset = 0

        with self.session() as session:
            while True:
                stmt = select(Car).limit(self.chunk_size).offset(offset)
                cars = session.execute(stmt).scalars().all()
                if not cars:
                    self.logger.info("Export completed")
                    break

                self.export_cars(cars, offset)

                offset += self.chunk_size

    def export_cars(self, cars: list[Car], offset: int) -> None:
        cars_dicts = [self.car_to_dict(car) for car in cars]

        export_file_path = os.path.join(
            self.export_path, f"exported_cars_{offset}_{offset+self.chunk_size}.json"
        )
        with open(export_file_path, mode="w+", encoding="utf-8") as f:
            json.dump(cars_dicts, f, indent=4, ensure_ascii=False)

    def car_to_dict(self, car: Car) -> dict[str, Any]:
        return {
            "url": car.url,
            "title": car.title,
            "price_usd": car.price_usd,
            "odometer": car.odometer,
            "username": car.username,
            "image_url": car.image_url,
            "images_count": car.images_count,
            "car_number": car.car_number,
            "car_vin": car.car_vin,
            "phone_number": car.phone_number,
            "created_at": str(car.created_at),
        }
