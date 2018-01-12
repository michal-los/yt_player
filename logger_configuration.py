import logging
import os
from shutil import copyfile


class DuplicateFilter(logging.Filter):
    """ a filter to suppress repeating log messages """
    def __init__(self):
        logging.Filter.__init__(self)
        self.last_log = None

    def filter(self, record):
        current_log = record.msg
        if current_log != getattr(self, "last_log", None):
            self.last_log = current_log
            return True
        return False


def backup_and_clear_logfile(_log_file_name):
    """ copies a logfile appending '.bak' as it's new extension and then clears the logfile """
    copyfile(_log_file_name, _log_file_name + ".bak")
    with open(_log_file_name, 'w'):
        pass


def configure_logger(log_file_name="logfile.log",
                     log_level=logging.ERROR,
                     log_file_size_limit_bytes=1024*1024):
    """
    Configures logger according to parameters:
    :param log_file_name: name of log file to write to
    :param log_level:
    :param log_file_size_limit_bytes: if the limit exceeds file will be backed up and cleared
    :return: preconfigured logger object
    """
    if os.path.isfile(log_file_name):
        log_file_size_bytes = os.stat(log_file_name).st_size

        if log_file_size_bytes > log_file_size_limit_bytes:
            backup_and_clear_logfile(log_file_name)

    _logger = logging.getLogger('Youtube Player')
    log_file = logging.FileHandler(log_file_name)

    logs_formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    log_file.setFormatter(logs_formatter)
    _logger.addFilter(DuplicateFilter())
    _logger.addHandler(log_file)
    _logger.setLevel(log_level)
    return _logger
