import asyncio
import logging
from datetime import datetime
from typing import List

from src.alerter import Alerter
from src.homework_status import HomeworkStatus

from playwright.async_api import async_playwright, Browser, Page


class AutoLogbookPwAsync:
    """Logbook automation class"""
    browser: Browser
    page: Page

    def __init__(self, login: str, password: str, alerter: Alerter, headless: bool = True):
        self.login = login
        self.password = password
        self.alerter = alerter
        self.not_logged = True
        self.headless = headless

    async def make_sure_page_is_created(self):
        if self.page is None:
            p = await async_playwright().start()
            self.browser = await p.webkit.launch(headless=self.headless)
            self.page = await self.browser.new_page()

    async def get_review_needed_homework(self) -> List[str]:
        await self.make_sure_page_is_created()
        logged: bool = await self.is_logged()
        if not logged:
            logged = await self.do_login()
        if not logged:
            raise Exception("Cannot login. Perhaps wrong login or password (check .env file).")
        logging.warning("Checking homework...")
        await self.page.goto("https://logbook.itstep.org/#/homeWork")

        table = await self.page.wait_for_selector("xpath=//table[contains(@class, 'home_work-table')]")
        await asyncio.sleep(5)
        tbody = await table.query_selector("tbody")
        rows = await tbody.query_selector_all("tr")
        homework: List[(str, HomeworkStatus)] = []
        for row in rows:
            name = (await row.text_content()).strip()
            student_name_td = await row.query_selector("xpath=.//td[contains(@class, 'student-name')]")
            if student_name_td:
                p = await student_name_td.query_selector("p")
                if p:
                    name = (await p.text_content()).strip()
            grade_divs = await row.query_selector_all("xpath=.//div[contains(@class, 'input-field')]")
            for div in grade_divs:
                status = HomeworkStatus.from_class_name(await div.get_attribute("class"))
                homework.append((name, status))

        done_homework = list(h[0] for h in homework if h[1] == HomeworkStatus.DONE)
        undone_homework = list(h[0] for h in homework if h[1] == HomeworkStatus.UNDONE)
        review_needed_homework = list(h[0] for h in homework if h[1] == HomeworkStatus.REVIEW_NEEDED)

        logging.warning(f'Done homework: {len(done_homework)}')
        logging.warning(f'Undone homework: {len(undone_homework)}')

        if len(review_needed_homework) > 0:
            logging.warning(f'HOMEWORK NEEDED REVIEW ({len(review_needed_homework)}):\n {review_needed_homework}')

        return review_needed_homework

    async def is_logged(self, refresh: bool = True) -> bool:
        await self.make_sure_page_is_created()
        if self.not_logged:
            return False
        if refresh:
            await self.page.goto("https://logbook.itstep.org/#/")
        return "login" not in self.page.url

    async def do_login(self) -> bool:
        await self.make_sure_page_is_created()
        logging.warning("Logging in...")
        self.not_logged = None
        await self.page.goto("https://logbook.itstep.org/login/#/")
        # https://selenium-python.readthedocs.io/waits.html
        login = await self.page.wait_for_selector("#login")
        await login.fill(self.login)

        await self.page.fill("#password", self.password)

        await self.page.click(".btn-login")
        await asyncio.sleep(2)

        try:
            await self.page.wait_for_load_state(timeout=10)
        except TimeoutError:
            self.not_logged = True

        logging.warning(f"Logged in: {not self.not_logged}")
        return not self.not_logged

    async def start_homework_checker(self, repeat_delay_in_sec: int = 5 * 60):
        while True:
            review_needed_homework = await self.get_review_needed_homework()
            if review_needed_homework and len(review_needed_homework) > 0:
                self.alerter.report_new_homework(datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                                                 + f": New homework is appeared!\n{review_needed_homework}")
            else:
                logging.warning("No new homework")
            logging.warning(f"Sleeping {repeat_delay_in_sec} seconds...")
            await asyncio.sleep(repeat_delay_in_sec)
