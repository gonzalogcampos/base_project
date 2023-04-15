import os
import yaml

import log as Log
from settings import Settings


class _DatabaseMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):

        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Database(metaclass=_DatabaseMeta):
    _data = {}

    def __init__(self) -> None:
        self.read()

    def read(self):
        Database._data = {}
        db_folder = os.path.normpath(os.path.join(os.path.dirname(__file__), Settings.db_folder))
        if not os.path.exists(db_folder):
            return
        for filename in os.listdir(db_folder):
            table_name = os.path.splitext(filename)[0]
            with open(os.path.join(db_folder, filename), 'r') as table_file:
                table = yaml.safe_load(table_file)
            Database._data[table_name] = table

    def save(self):
        db_folder = os.path.normpath(os.path.join(os.path.dirname(__file__), Settings.db_folder))
        if not os.path.exists(db_folder):
            os.makedirs(db_folder)

        for table_name, table in Database._data.items():
            filename = "{}.{}".format(table_name, 'yml')
            with open(os.path.join(db_folder, filename), 'w') as table_file:
                yaml.safe_dump(table, table_file)

    def get_table(self, table):
        return Database._data.get(table, {}).copy()

    def get_by_id(self, table, id):
        return self.get_table(table).get(id)

    def find(self, table, filters=None, max_count=0):
        self.get_table(table)
        found_items = {}

        filters = filters or []
        for id, item in table:
            for filter in filters:
                key = filter[0] 
                operator = filter[0]
                filter_value = filter[0]

                item_value = id if key == 'id' else item[key]
                if operator == 'equal':
                    if item_value == filter_value:
                        found_items[id] = item
                elif operator == '!equal':
                    if item_value != filter_value:
                        found_items[id] = item
                elif operator == 'contains':
                    if item_value in filter_value:
                        found_items[id] = item
                elif operator == '!contains':
                    if item_value not in filter_value:
                        found_items[id] = item
                elif operator == 'is':
                    if item_value is filter_value:
                        found_items[id] = item
                elif operator == '!is':
                    if item_value is not filter_value:
                        found_items[id] = item

            if max_count>0 and len(found_items)==max_count:
                break

        return found_items

    def set_item(self, table, id, value):
        if table not in self._data:
            Log.warning('Table {} not in database.'.format(table))
            return False

        if id not in Database._data[table]:
            Log.warning('Item {} not in table {}.'.format(id, table))
            return False

        Log.info("Editing table {} item {}: {}".format(table, id, value))
        Database._data[table][id] = value
        return True

    def add_item(self, table, value, id=None):
        if table not in self._data:
            Log.info('Table {} not in database, creating one.'.format(table))
            self._data[table] = {}

        all_ids = self.get_table(table).keys()
        if id:
            if id in all_ids:
                Log.error('Table already contains id not in database, creating one.'.format(table))
                return False
            new_id = id
        else:
            new_id = 0
            if all_ids:
                new_id = max(all_ids) + 1
        

        Log.info("Adding to table {} item {}: {}".format(table, new_id, value))
        Database._data[table][new_id] = value
        return new_id

    def rem_item(self, table, id):
        if table not in self._data:
            Log.warning('Table {} not in database.'.format(table))
            return False

        if id not in Database._data[table]:
            Log.warning('Item {} not in table {}.'.format(id, table))
            return False

        Log.info("Removing from table {} item {}.".format(table, id))
        Database._data[table].pop(id)
        return True

    def __getattr__(self, __name: str):
        return Database._data.get(__name, {})

    def __setattr__(self, __name: str, __value):
        Log.warning("Set attr if forbidden in database")


if __name__ == "__main__":
    db1 = Database()
    db2 = Database()

    db2.products = {}
    Log.debug(db2.products)

    if id(db1) == id(db2):
        Log.info("DataBase works, both variables contain the same instance.")
    else:
        Log.error("DataBase failed, variables contain different instances.")