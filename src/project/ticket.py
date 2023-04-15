from .entity import Entity


class Ticket(Entity):
    def __init__(self):
        super(Ticket, self).__init__()
        self.products = []


class TicketItem(Entity):
    def __init__(self):
        self.product = None
        self.discount = None
        self.units = None