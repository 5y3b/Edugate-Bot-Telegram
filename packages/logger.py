from os import makedirs, path
from typing import Optional 
import logging

# create Logs class using the logging module
class Logger(logging.Logger):
    """This class handles logging info, default folder is `logs/`

            :param logger_name: name of the logger, default is `Logger_{logger_count}`
            :param log_file:  file to store logs at, default is `logs.log`
            :param log_folder: folder to store `log_file` at, default is `logs\\`

            ~"""
    __logger_count = 1
    def __init__(self, logger_name: Optional[str]=None, log_file: Optional[str]=None, logs_folder: Optional[str]=None):
        """This class handles logging info, default folder is `logs/`

            :param logger_name: name of the logger, default is `Logger_{logger_count}`
            :param log_file:  file to store logs at, default is `logs.log`
            :param log_folder: folder to store `log_file` at, default is `logs\\`

            ~"""
        
        
        logger_name = logger_name or f"Logger_{Logger.__logger_count}"
        logs_folder = logs_folder or 'logs'
        log_file = log_file or f"logs.log"
        log_path = path.join(logs_folder, log_file)

        makedirs(logs_folder, exist_ok=True)
        
        super().__init__(logger_name)
        file_handler = logging.FileHandler(log_path, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s', 
            datefmt='%d-%b-%y %H:%M:%S'
            )
        file_handler.setFormatter(formatter)
        
        self.addHandler(file_handler)
        self.setLevel(logging.INFO)

        Logger.__logger_count += 1
        
        self.info(f"initialized ------, log file: {log_path}")

        