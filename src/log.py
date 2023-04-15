import os
from datetime import datetime

from settings import Settings

def debug(msg):
    _log(msg, 3)


def info(msg):
    _log(msg, 2)


def warning(msg):
    _log(msg, 1)


def error(msg):
    _log(msg, 0)


def _log(msg, lvl):
    time_text = datetime.now().strftime(Settings.log_format_time)
    date_text = datetime.now().strftime(Settings.log_format_date)
    lvl_text = Settings.log_level_list[lvl]
    log_msg = Settings.log_format.format(date=date_text, time=time_text, lvl=lvl_text, msg=msg)
    log_filepath = Settings.log_filepath.format(date=date_text, time=time_text)
    log_filepath = os.path.join(os.path.dirname(__file__), log_filepath)
    log_filepath = os.path.normpath(log_filepath)

    if Settings.log_level_save >= lvl:
        if not os.path.exists(os.path.dirname(log_filepath)):
            os.makedirs(os.path.dirname(log_filepath))
        with open(log_filepath, 'a') as log_file:
            log_file.write(log_msg)
            log_file.write('\n')

    if Settings.log_level_print >= lvl:
        print(log_msg)


if __name__ == '__main__':
    debug('This is a debug test')
    info('This is a info test')
    warning('This is a warning test')
    error('This is a error test')