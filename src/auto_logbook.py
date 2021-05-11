import logging
from datetime import datetime
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions

from src.alerter import Alerter
from src.homework_status import HomeworkStatus


class AutoLogbook:
    """Logbook automation class"""

    def __init__(self, login: str, password: str, driver_filename: str, alerter: Alerter, headless: bool = True):
        self.login = login
        self.password = password
        self.alerter: Alerter = alerter
        self.not_logged = True
        options = webdriver.ChromeOptions()
        options.headless = headless
        self.driver = webdriver.Chrome(driver_filename, options=options)

    def get_review_needed_homework(self):
        logged: bool = self.is_logged()
        if not logged:
            logged = self.do_login()
        if not logged:
            raise Exception("Cannot login. Perhaps wrong login or password (check .env file).")
        logging.warning("Checking homework...")
        self.driver.get("https://logbook.itstep.org/#/homeWork")
        table: WebElement = WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((By.XPATH, "//table[contains(@class, 'home_work-table')]"))
        )
        sleep(5)
        tbody = table.find_element_by_tag_name("tbody")
        rows = tbody.find_elements_by_tag_name("tr")
        homework: list = []
        for row in rows:
            name = row.text.strip()
            student_name_td = row.find_element_by_xpath(".//td[contains(@class, 'student-name')]")
            if student_name_td:
                p = student_name_td.find_element_by_tag_name("p")
                if p:
                    name = p.text.strip()
            grade_div = row.find_element_by_xpath(".//div[contains(@class, 'input-field')]")
            status = HomeworkStatus.from_class_name(grade_div.get_attribute("class"))
            homework.append((name, status))

        done_homework = list(h[0] for h in homework if h[1] == HomeworkStatus.DONE)
        undone_homework = list(h[0] for h in homework if h[1] == HomeworkStatus.UNDONE)
        review_needed_homework = list(h[0] for h in homework if h[1] == HomeworkStatus.REVIEW_NEEDED)

        logging.warning(f'Done homework: {len(done_homework)}')
        logging.warning(f'Undone homework: {len(undone_homework)}')
        if len(review_needed_homework) > 0:
            logging.warning(f'HOMEWORK NEEDED REVIEW ({len(review_needed_homework)}):\n {review_needed_homework}')

        return review_needed_homework

    def is_logged(self, refresh: bool = True) -> bool:
        if self.not_logged:
            return False
        if refresh:
            self.driver.get("https://logbook.itstep.org/#/")
        return "login" not in self.driver.current_url

    def do_login(self) -> bool:
        logging.warning("Logging in...")
        self.not_logged = None
        self.driver.get("https://logbook.itstep.org/login/#/")
        # https://selenium-python.readthedocs.io/waits.html
        elem = WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((By.ID, "login"))
        )
        elem.clear()
        elem.send_keys(self.login)

        elem = self.driver.find_element_by_id("password")
        elem.clear()
        elem.send_keys(self.password)

        elem.send_keys(Keys.RETURN)

        try:
            WebDriverWait(self.driver, 5).until_not(
                expected_conditions.url_contains("login")
            )
            self.not_logged = False
        except TimeoutException:
            self.not_logged = True

        logging.warning(f"Logged in: {not self.not_logged}")
        return not self.not_logged

    def start_homework_checker(self, repeat_delay_in_sec: int = 5 * 60):
        while True:
            review_needed_homework = self.get_review_needed_homework()
            if review_needed_homework and len(review_needed_homework) > 0:
                self.alerter.report_new_homework(datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                                                 + f": New homework is appeared!\n{review_needed_homework}")
            else:
                logging.warning("No new homework")
            logging.warning(f"Sleeping {repeat_delay_in_sec} seconds...")
            sleep(repeat_delay_in_sec)
