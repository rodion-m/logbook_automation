import logging
import webbrowser
from win10toast_click import ToastNotifier

from src.alerter import Alerter


def open_homework_url():
    try:
        webbrowser.open_new("https://logbook.itstep.org/#/homeWork")
    except:
        logging.error('Failed to open URL. Unsupported variable type.')


class Win10ToastAlerter(Alerter):
    def report_new_homework(self, message: str):
        # initialize
        toaster = ToastNotifier()

        # showcase
        toaster.show_toast(
            "New homework!",  # title
            message,  # message
            icon_path=None,  # 'icon_path'
            duration=30,
            # for how many seconds toast should be visible; None = leave notification in Notification Center
            threaded=True,
            # True = run other code in parallel; False = code execution will wait till notification disappears
            callback_on_click=open_homework_url  # click notification to run function
        )


