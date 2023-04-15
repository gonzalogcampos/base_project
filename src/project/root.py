from ..db import db

class Root(Entity):
    def __init__(self):
        super(Root, self).__init__()
        
        self.products = []
        self.clients = []

    def read_db(self):
        self.products = db.get('products')
        self.clients = db.get('clients')
