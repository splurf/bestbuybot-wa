from bs4 import BeautifulSoup


class Souper:
    PARSER = "lxml"

    @staticmethod
    def do(text: str) -> BeautifulSoup:
        return BeautifulSoup(text, Souper.PARSER)

    @staticmethod
    def sku(soup: BeautifulSoup):
        temp = soup.find("div", {"class": "sku product-data"})
        if temp != None:
            temp = temp.find("span", {"class": "product-data-value body-copy"})
            if temp != None:
                temp = temp.text.strip()
        return temp

    @staticmethod
    def model(soup: BeautifulSoup):
        temp = soup.find("div", {"class": "model product-data"})
        if temp != None:
            temp = temp.find("span", {"class": "product-data-value body-copy"})
            if temp != None:
                temp = temp.text.strip()
        return temp

    @staticmethod
    def name(soup: BeautifulSoup):
        temp = soup.find("h1", {"class": "heading-5 v-fw-regular"})
        return temp if temp == None else temp.text.strip()

    @staticmethod
    def status(soup: BeautifulSoup):
        temp = soup.find("div", {"class": "fulfillment-add-to-cart-button"})
        return temp if temp == None else temp.find("button")
