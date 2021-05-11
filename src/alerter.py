from abc import ABCMeta, abstractmethod


class Alerter(metaclass=ABCMeta):
    @abstractmethod
    def report_new_homework(self, message: str):
        pass
