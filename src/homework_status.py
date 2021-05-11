from enum import Enum


class HomeworkStatus(Enum):
    UNDONE = 0
    REVIEW_NEEDED = 1
    DONE = 2

    @staticmethod
    def from_class_name(class_name: str):
        if "done" in class_name:
            return HomeworkStatus.DONE
        elif "disabled" in class_name:
            return HomeworkStatus.UNDONE
        else:
            return HomeworkStatus.REVIEW_NEEDED
