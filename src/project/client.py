from .entity import Entity
from .ticket import Ticket

class Client(Entity):
    def __init__(self):
        super(Client, self).__init__()
        self.ticket = Ticket()