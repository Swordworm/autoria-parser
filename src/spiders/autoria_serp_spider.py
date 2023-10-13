import json
import re
import sys
from typing import Any, Callable, Generator
from scrapy import Spider, Request
from scrapy.http import TextResponse
from furl import furl

from src.items import CarItem


class AutoriaSerpSpider(Spider):
    name: str = "autoria_serp_spider"
    allowed_domains: list[str] = ["auto.ria.com"]
    base_url: str = "https://auto.ria.com/uk/car/used/"
    mobile_phone_base_url: str = "https://auto.ria.com/users/phones/"
    start_page: int = 1

    def start_requests(self) -> Generator[Request, None, None]:
        yield self.build_serp_request(callback=self.parse_serp)

    def parse_serp(
        self,
        response: TextResponse,
        current_page: int,
        total_pages: int | None = None,
    ):
        try:
            car_urls = self._get_car_urls(response)

            for url in car_urls:
                yield self.build_car_request(url, self.parse_car)

            if current_page == self.start_page:
                updated_total_pages = self._get_total_pages(response)

                for page_number in range(1, updated_total_pages):
                    yield self.build_serp_request(
                        self.parse_serp,
                        current_page + page_number,
                        updated_total_pages,
                    )
            if current_page == total_pages:
                self.logger.info(f"Parsed all serp pages {total_pages}")

        except Exception as e:
            self.logger.warning(f"Unexpected exception parsing serp: {e}")

    def parse_car(
        self,
        response: TextResponse,
    ):
        try:
            car = self.get_car_data(response)

            security_data = self._get_security_data(response)

            yield self.build_phone_number_request(
                car=car,
                callback=self.parse_phone_number,
                car_id=self._get_car_id(response),
                hash=security_data["hash"],
                expires=security_data["expires"],
            )
        except Exception as e:
            self.logger.warning(
                f"Unexpected exception parsing car ({response.url}): {e}",
                exc_info=sys.exc_info(),
            )

    def parse_phone_number(self, response: TextResponse, car: dict[str, Any]):
        try:
            phone_number_data = response.json()
            car["phone_number"] = self._get_phone_number(phone_number_data)

            yield CarItem(car)
        except Exception as e:
            self.logger.warning(
                f"Unexpected exception parsing phone number ({response.url}): {e}",
                exc_info=sys.exc_info(),
            )

    def build_serp_request(
        self,
        callback: Callable,
        page_number: int | None = None,
        total_pages: int | None = None,
    ) -> Request:
        if page_number is None:
            page_number = self.start_page
        f_url = furl(self.base_url).add({"page": page_number})
        return Request(
            url=f_url.url,
            callback=callback,
            cb_kwargs={
                "current_page": page_number,
                "total_pages": total_pages,
            },
        )

    def build_car_request(self, url: str, callback: Callable) -> Request:
        return Request(
            url=url,
            callback=callback,
        )

    def build_phone_number_request(
        self,
        car: dict[str, Any],
        callback: Callable,
        car_id: str,
        hash: str,
        expires: str,
    ) -> Request:
        f_url = furl(self.mobile_phone_base_url)
        f_url /= car_id
        f_url.add({"hash": hash, "expires": expires})
        return Request(f_url.url, callback, cb_kwargs={"car": car})

    def get_car_data(self, response: TextResponse) -> dict[str, Any]:
        car_json_data = self._get_car_json(response)
        car_vin = car_json_data.get("vehicleIdentificationNumber")
        car_data = {
            "url": response.url,
            "title": car_json_data["name"],
            "price_usd": int(car_json_data["offers"]["price"]),
            "odometer": car_json_data["mileageFromOdometer"]["value"],
            "username": self._get_username(response),
            "image_url": self._get_image_url(response),
            "images_count": self._get_images_count(response),
            "car_number": self._get_car_number(response),
            "car_vin": car_vin or self._get_car_vin(response),
        }
        return car_data

    def _get_car_urls(self, response: TextResponse) -> list[str]:
        return response.xpath(
            '//div[@id="searchResults"]/section[contains(@class, ticket-item)]/div[@class="content-bar"]/a[@class="m-link-ticket"]/@href'
        ).getall()

    def _get_total_pages(self, response: TextResponse) -> int:
        total_pages = (
            response.xpath(
                '//div[@id="pagination"]/nav/span[contains(@class, "page-item") and contains(text(), "...")]/following-sibling::span/a/text()'
            )
            .get()
            .replace(" ", "")
        )
        return int(total_pages)

    def _get_car_json(self, response: TextResponse) -> dict[str, Any]:
        car_json_str = response.xpath('//script[@id="ldJson2"]/text()').get()
        return json.loads(car_json_str)

    def _get_username(self, response: TextResponse) -> str | None:
        path_variations = [
            '//section[@id="userInfoBlock"]/div/div[@class="seller_info_area"]/div[contains(@class, "seller_info_name")]/text()',
            '//section[@id="userInfoBlock"]/div/div[@class="seller_info_area"]/h4[@class="seller_info_name"]/a/text()',
        ]
        for path in path_variations:
            username = response.xpath(path).get()
            if username is not None:
                return username.strip()

        return None

    def _get_image_url(self, response: TextResponse) -> str | None:
        carousel_container = response.xpath(
            '//div[@id="photosBlock"]/div[contains(@class, "carousel")]'
        )
        image_url = carousel_container.xpath(
            './div/div[contains(@class, "photo")]/picture/source/@srcset'
        ).get()
        return image_url

    def _get_images_count(self, response: TextResponse) -> int:
        preview_container = response.xpath(
            '//div[@id="photosBlock"]/div[contains(@class, "preview-gallery")]'
        )
        images_count_str = preview_container.xpath(
            './div[@class="action_disp_all_block"]/a/text()'
        ).get()

        if images_count_str is not None:
            match = re.search(r"\d+", images_count_str)
            if match is None:
                raise ValueError(
                    f"Could not extract images count from {images_count_str}"
                )

            return int(match.group(0))

        carousel_container = response.xpath(
            '//div[@id="photosBlock"]/div[contains(@class, "carousel")]'
        )
        images = carousel_container.xpath(
            './div[contains(@class, "carousel-inner")]/div[contains(@class, "photo") and not(contains(@class, "phone-in-photo"))]'
        ).getall()
        return len(images)

    def _get_car_number(self, response: TextResponse) -> str | None:
        car_number_container = response.xpath(
            '//main[@class="auto-content"]/div/div[contains(@class, "vin-checked")]'
        )
        car_number = car_number_container.xpath(
            './/span[contains(@class, "state-num")]/text()'
        ).get()

        if car_number is not None:
            return car_number.strip()
        return None

    def _get_car_vin(self, response: TextResponse) -> str | None:
        car_vin_container = response.xpath(
            '//main[@class="auto-content"]/div/div[contains(@class, "vin-checked")]'
        )
        car_vin = car_vin_container.xpath('.//span[@class="label-vin"]/text()').get()

        if car_vin is not None and "xxxx" not in car_vin:
            return car_vin.strip()
        return None

    def _get_security_data(self, response: TextResponse) -> dict[str, str]:
        security_script = response.xpath("//script[@data-hash and @data-expires]")
        hash_value = security_script.xpath("./@data-hash").get()
        expires = security_script.xpath("./@data-expires").get()

        if None in [hash_value, expires]:
            raise ValueError("Could not extract hash or expiration time")

        return {"hash": hash_value, "expires": expires}

    def _get_car_id(self, response: TextResponse) -> str:
        car_id = response.xpath("//body/@data-auto-id").get()
        if car_id is None:
            raise ValueError("Could not extract car id from body")
        return car_id

    def _get_phone_number(self, data: dict[str, Any]) -> int:
        phone_number_str = data["formattedPhoneNumber"]

        matches = re.findall(r"\d", phone_number_str)

        if not matches:
            raise ValueError(f"Could not extract phone number from {phone_number_str}")

        if len(matches) < 6:
            raise ValueError(
                f"Could not extract phone number from {phone_number_str}, extracted {''.join(matches)}"
            )

        return int("38" + "".join(matches))
