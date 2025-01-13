from pydantic import BaseModel, field_validator

parsing_list = [['Блузки и рубашки', 'bl_shirts', 'cat=8126'], ['Брюки', 'pants', 'cat=8127'],
                ['Верхняя одежда', 'outwear1', 'cat=63010'],
                ['Джемперы, водолазки и кардиганы', 'jumpers_cardigans', 'cat=8130'], ['Джинсы', 'jeans', 'cat=8131'],
                ['Комбинезоны', 'overalls', 'cat=8133'], ['Костюмы', 'costumes', 'cat=8134'],
                ['Лонгсливы', 'sweatshirts_hoodies', 'cat=9411'],
                ['Пиджаки, жилеты и жакеты', 'blazers_wamuses', 'cat=8136'],
                ['Платья и сарафаны', 'dresses', 'cat=8137'],
                ['Толстовки, свитшоты и худи', 'sweatshirts_hoodies', 'cat=8140'],
                ['Туники', 'sweatshirts_hoodies', 'cat=8141'], ['Футболки и топы', 'tops_tshirts1', 'cat=8142'],
                ['Халаты', 'women_bathrobes', 'cat=128996'], ['Шорты', 'shorts', 'cat=10567'],
                ['Юбки', 'skirts', 'cat=8143'],
                ['Детская', 'children_shoes', 'cat=128330'],
                ['Мужская', 'men_shoes', 'cat=751'],
                ['Аксессуары для обуви', 'shoes_accessories1', 'cat=62875'],
                ['Детская электроника', 'electronic19', 'cat=58513'],['Брюки', 'men_clothes1', 'cat=8144'],
                ['Верхняя одежда', 'men_clothes1', 'cat=63011'],
                ['Джемперы, водолазки и кардиганы', 'men_clothes2', 'cat=8148'], ['Джинсы', 'men_clothes2', 'cat=8149'],
                ['Комбинезоны и полукомбинезоны', 'men_clothes2', 'cat=8152'], ['Костюмы', 'men_clothes2', 'cat=8153'],
                ['Лонгсливы', 'men_clothes3', 'cat=9412'], ['Майки', 'men_clothes3', 'cat=129176'],
                ['Пиджаки, жилеты и жакеты', 'men_clothes3', 'cat=8155'], ['Пижамы', 'men_clothes3', 'cat=129258'],
                ['Рубашки', 'men_clothes3', 'cat=8156'], ['Толстовки, свитшоты и худи', 'men_clothes4', 'cat=8158'],
                ['Футболки', 'men_clothes6', 'cat=8159'], ['Футболки-поло', 'men_clothes5', 'cat=129257'],
                ['Шорты', 'men_clothes5', 'cat=11428'],
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
