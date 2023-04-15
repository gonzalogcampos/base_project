import os
import yaml

import log as Log


SETTINGS_FILE = os.path.join(os.path.dirname(__file__), '..', 'config', 'settings.yml')


class _SettingsMeta(type):
    def __getattr__(cls, __name: str):
        if __name not in cls._settings:
            raise AttributeError("Missing setting {}".format(__name))
        return cls._settings[__name]


class Settings(metaclass=_SettingsMeta):
    _settings = {}

    @staticmethod
    def read_settings():
        with open(SETTINGS_FILE, 'r') as settings_file:
            Settings._settings = yaml.safe_load(settings_file)

    @staticmethod
    def save_setting(key, value):
        Settings._settings[key] = value


if not Settings._settings:
    Settings.read_settings()


if __name__ == '__main__':
    Log.debug(Settings.db_folder)