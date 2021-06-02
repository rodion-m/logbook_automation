import asyncio
import os
import logging

from dotenv import load_dotenv

from src.auto_logbook_pw import AutoLogbookPwAsync
from src.tk_message_box_alerter import TkMessageBoxAlerter
from src.win10_toast_alerter import Win10ToastAlerter

load_dotenv()
logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logging.root.setLevel(logging.WARNING)


async def main():
    logging.warning('Running...')
    logbook = AutoLogbookPwAsync(os.getenv("login"), os.getenv("password"),
                                 Win10ToastAlerter(),
                                 headless=False)
    await logbook.start_homework_checker()


if __name__ == '__main__':
    asyncio.run(main(), debug=True)
