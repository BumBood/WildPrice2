from pydantic import BaseModel, field_validator

parsing_list = [
    ["Женские блузки и рубашки", "bl_shirts", "cat=8126"],
    ["Женские брюки", "pants", "cat=8127"],
    ["Женская верхняя одежда", "outwear1", "cat=63010"],
    ["Женские джемперы, водолазки и кардиганы", "jumpers_cardigans", "cat=8130"],
    ["Женские джинсы", "jeans", "cat=8131"],
    ["Женские комбинезоны", "overalls", "cat=8133"],
    ["Женские костюмы", "costumes", "cat=8134"],
    ["Женские лонгсливы", "sweatshirts_hoodies", "cat=9411"],
    ["Женские пиджаки, жилеты и жакеты", "blazers_wamuses", "cat=8136"],
    ["Женские платья и сарафаны", "dresses", "cat=8137"],
    ["Женские толстовки, свитшоты и худи", "sweatshirts_hoodies", "cat=8140"],
    ["Женские туники", "sweatshirts_hoodies", "cat=8141"],
    ["Женские футболки и топы", "tops_tshirts1", "cat=8142"],
    ["Женские халаты", "women_bathrobes", "cat=128996"],
    ["Женские шорты", "shorts", "cat=10567"],
    ["Женские юбки", "skirts", "cat=8143"],
    ["Детская обувь", "children_shoes", "cat=128330"],
    ["Мужская обувь", "men_shoes", "cat=751"],
    ["Аксессуары для обуви", "shoes_accessories1", "cat=62875"],
    ["Детская электроника", "electronic19", "cat=58513"],
    ["Мужские брюки", "men_clothes1", "cat=8144"],
    ["Мужская верхняя одежда", "men_clothes1", "cat=63011"],
    ["Мужские джемперы, водолазки и кардиганы", "men_clothes2", "cat=8148"],
    ["Мужские джинсы", "men_clothes2", "cat=8149"],
    ["Мужские комбинезоны и полукомбинезоны", "men_clothes2", "cat=8152"],
    ["Мужские костюмы", "men_clothes2", "cat=8153"],
    ["Мужские лонгсливы", "men_clothes3", "cat=9412"],
    ["Мужские майки", "men_clothes3", "cat=129176"],
    ["Мужские пиджаки, жилеты и жакеты", "men_clothes3", "cat=8155"],
    ["Мужские пижамы", "men_clothes3", "cat=129258"],
    ["Мужские рубашки", "men_clothes3", "cat=8156"],
    ["Мужские толстовки, свитшоты и худи", "men_clothes4", "cat=8158"],
    ["Мужские футболки", "men_clothes6", "cat=8159"],
    ["Мужские футболки-поло", "men_clothes5", "cat=129257"],
    ["Мужские шорты", "men_clothes5", "cat=11428"],
]


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

    @field_validator("sizes")
    def convert_size(cls, raw_sizes: list) -> list:
        sizes = []
        for size in raw_sizes:
            sizes.append(size["name"])
        return sizes

    @field_validator("salePriceU")
    def convert_sale_price(cls, sale_price: int) -> float:
        if sale_price is not None:
            return sale_price / 100

    @field_validator("priceU")
    def convert_price(cls, price: int) -> float:
        if price is not None:
            return price / 100


class DBItem(BaseModel):
    id: int
    name: str
    salePriceU: float

    @field_validator("salePriceU")
    def convert_sale_price(cls, sale_price: int) -> float:
        if sale_price is not None:
            return sale_price / 100
