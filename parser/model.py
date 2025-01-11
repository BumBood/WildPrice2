from pydantic import BaseModel, field_validator


class Item(BaseModel):
    id: int
    name: str
    salePriceU: float
    priceU: float
    discount: float = 0
    brand: str = ""
    reviewRating: float
    image_link: str = None
    feedbacks: int
    sizes: list = [1]

    @field_validator('sizes')
    def convert_size(cls, raw_sizes: list) -> list:
        sizes = []
        for size in raw_sizes:
            sizes.append(size["name"])
        return sizes

    @field_validator('salePriceU')
    def convert_sale_price(cls, sale_price: int) -> float:
        if sale_price is not None:
            return sale_price / 100

    @field_validator('priceU')
    def convert_price(cls, price: int) -> float:
        if price is not None:
            return price / 100


class DBItem(BaseModel):
    id: int
    name: str
    salePriceU: float

    @field_validator('salePriceU')
    def convert_sale_price(cls, sale_price: int) -> float:
        if sale_price is not None:
            return sale_price / 100
