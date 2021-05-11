import tkinter
from tkinter import messagebox

from src.alerter import Alerter


class TkMessageBoxAlerter(Alerter):
    def report_new_homework(self, message: str):
        root = tkinter.Tk()
        root.attributes("-topmost", True)
        root.withdraw()
        messagebox.showinfo("Logbook Automation", message)
        root.destroy()
