from os import chdir
from pathlib import Path
from sys import argv
from time import sleep

from requests import Response, Session
from requests.exceptions import ConnectionError
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from tools.counter import Counter
from tools.souper import Souper

from util.account import Account
from util.product import Product

match len(argv):
    case 6 | 7:
        match argv[1]:
            case "chrome":
                from selenium.webdriver import Chrome as Browser
                from selenium.webdriver.chrome.service import Service
            case "firefox":
                from selenium.webdriver import Firefox as Browser
                from selenium.webdriver.firefox.service import Service
            case "safari":
                from selenium.webdriver import Safari as Browser
                from selenium.webdriver.safari.service import Service
            case _: exit(print("Unknown browser"))
    case _: exit(print("Invalid argument(s)"))

#   Set `cwd` to project directory for easy accessbility of the `geckodriver.exe`
chdir(Path(argv[0]).parent)


class BotResponse:
    def __init__(self, res: Response = None, interrupt=False):
        self.res = res
        self.interrupt = interrupt

    def is_ok(self) -> bool:
        return self.res and self.res.status_code == 200

    def is_interrupt(self) -> bool:
        return self.interrupt

    def inner(self) -> Response:
        return self.res


class BotOptions:
    def __init__(self, browser: str, test: str, rate: float = 0.1, driver_path="geckodriver.exe"):
        if test:
            if test == "test":
                self.test = True
            else:
                self.shutdown("Invalid test parameter")
        else:
            self.test = False

        self.browser = browser
        self.rate = rate
        self.driver_path = driver_path


class BotSession:
    SCHEME = "https"
    HOST = "www.bestbuy.com"

    def __init__(self):
        self.inner = Session()

        self.inner.headers.update(
            {
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.5",
                'Host': BotSession.HOST,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0',
            }
        )

    def get(self, path: str) -> BotResponse:
        c = Counter()

        try:
            return BotResponse(self.inner.get(self.to(path)))
        except ConnectionError:
            if not c.run():
                return BotResponse()
        except KeyboardInterrupt:
            return BotResponse(interrupt=True)

    @staticmethod
    def to(path: str) -> str:
        return "%s://%s/%s" % (BotSession.SCHEME, BotSession.HOST, path)


class BotWebElement:
    def __init__(self, element: WebElement):
        self.element = element

    def attempt(self, func) -> bool:
        for _ in range(5):
            try:
                func(self.element)
                return True
            except:
                sleep(0.2)
        return False

    def click(self) -> bool:
        return self.attempt(lambda element: element.click())

    def send_keys(self, content: str) -> bool:
        return self.attempt(lambda element: element.send_keys(content))

    def submit(self) -> bool:
        return self.attempt(lambda element: element.submit())


class Bot:
    def __init__(self, browser: str, sku: str, email: str, password: str, cvv: str, test: str = None):
        self.options = BotOptions(browser, test=test)
        self.driver = Browser(service=Service(self.options.driver_path))
        self.account = Account(email, password, cvv)
        self.session = BotSession()
        self.product = Product(sku)

    def test(self) -> bool:
        return self.options.test

    def shutdown(self, msg: str = None, exit=False, block=True):
        self.session.inner.close()
        self.driver.close()

        if msg:
            Counter.rprint(msg)
        if exit:
            exit(1)
        if block:
            input()

    def get(self, path: str) -> Response | None:
        res = self.session.get(path)

        if res.is_ok():
            return res.inner()
        elif res.is_interrupt():
            self.shutdown("Keyboard Interrupt", True)
        else:
            return None

    def find_element(self, xpath: str, wait: int = None, check=True, clickable=True) -> BotWebElement | None:
        if check:
            self.deny_survey_optional()

        locator = ((By.XPATH, xpath))
        if clickable:
            ec = EC.element_to_be_clickable(locator)
        else:
            ec = EC.visibility_of_element_located(locator)

        if wait == None:
            try:
                return BotWebElement(self.driver.find_element(ec))
            except:
                return None
        else:
            try:
                return BotWebElement(WebDriverWait(self.driver, wait).until(ec))
            except:
                return None

    def get_product_url(self) -> bool:
        res = self.get("site/searchpage.jsp?st=" + self.product.sku)

        if res:
            self.product.url = res.url.split(BotSession.HOST)[1][1::]
            return True
        else:
            return False

    def update_product(self) -> bool:
        res = self.get(self.product.url)

        if res:
            soup = Souper.do(res.text)

            self.product.update(Souper.sku(
                soup), Souper.model(soup), Souper.name(soup))

            return self.product.valid()
        else:
            return False

    def status(self) -> bool:
        res = self.get(self.product.url)

        if res:
            button = Souper.status(Souper.do(res.text))

            if button:
                return button["data-button-state"] == "ADD_TO_CART"
            else:
                self.shutdown("Error: HTML Parsing Error", True)
        else:
            self.shutdown("Connection Error", True)

    def wait_until_in_stock(self):
        self.driver.get(BotSession.to(self.product.url))

        c = Counter("Out of Stock")

        while True:
            if self.status():
                Counter.rprint("IN STOCK")
                break
            elif c.old():
                self.update_product()
            else:
                c.run()
            sleep(self.options.rate)

        self.session.inner.close()
        self.driver.refresh()

    def deny_survey_optional(self):
        clickable = self.find_element(
            "//button[@id=\"survey_invite_no\"]", check=False)
        if clickable:
            clickable.click()

    def login(self, msg: str = None) -> bool:
        if msg:
            Counter.rprint(msg)

        self.driver.get(BotSession.to("identity/global/signin"))

        clickable = self.find_element("//input[@id=\"fld-e\"]", 10)
        if not clickable or not clickable.send_keys(self.account.email):
            return False

        clickable = self.find_element("//input[@id=\"fld-p1\"]", 10)
        if not clickable or not clickable.send_keys(self.account.password):
            return False

        if not clickable.submit():
            return False

        return self.find_element("//div[@aria-label=\"Error\"]", 10) == None

    def add_to_cart(self, msg: str = None) -> bool:
        if msg:
            Counter.rprint(msg)

        clickable = self.find_element(
            "//button[@data-sku-id=\"%s\"][@data-button-state=\"ADD_TO_CART\"]" % self.product.sku, 10)

        return clickable and clickable.click()

    def cart(self, msg: str = None) -> bool:
        if msg:
            Counter.rprint(msg)

        clickable = self.find_element(
            "//a[@class=\"c-button c-button-secondary c-button-sm c-button-block \"]", 10)

        return clickable and clickable.click()

    def checkout(self, msg: str = None) -> bool:
        if msg:
            Counter.rprint(msg)

        clickable = self.find_element(
            "//button[@class=\"btn btn-lg btn-block btn-primary\"]", 10)

        return clickable and clickable.click()

    def continue_optional(self, msg: str = None):
        if msg:
            Counter.rprint(msg)

        clickable = self.find_element(
            "//button[@class=\"btn btn-lg btn-block btn-secondary\"]", 5)

        return clickable and clickable.click()

    def enter_cvv(self, msg: str = None):
        if msg:
            Counter.rprint(msg)

        clickable = self.find_element("//input[@id=\"cvv\"]", 5)

        return clickable and clickable.send_keys(self.account.cvv)

    def place_order(self, msg: str = None) -> bool:
        if msg:
            Counter.rprint(msg)

        clickable = self.find_element(
            "//button[@class=\"btn btn-lg btn-block btn-primary button__fast-track\"]", 10)

        return clickable and clickable.click()

    def evaluate(self) -> bool:
        return self.find_element("//h1[@class=\"thank-you-enhancement__oc-heading\"]", 60, clickable=False) != None

    @staticmethod
    def from_args():
        return Bot(*argv[1::])
