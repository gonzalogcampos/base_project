from .entity import Entity


class Product(Entity):
    def __init__(self):
        super(Product, self).__init__()
        self.price_per_unit = 10.0
        self.name = "New Product"
        self.short_name = "new"