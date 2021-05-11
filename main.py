import os
import logging

from dotenv import load_dotenv
from src.auto_logbook import AutoLogbook
from src.tk_message_box_alerter import TkMessageBoxAlerter

load_dotenv()
logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logging.root.setLevel(logging.WARNING)

if __name__ == '__main__':
    logging.warning('Running...')
    logbook = AutoLogbook(os.getenv("login"), os.getenv("password"),
                          os.getenv("driver_filename"),
                          TkMessageBoxAlerter(),
                          headless=True)
    logbook.start_homework_checker()
