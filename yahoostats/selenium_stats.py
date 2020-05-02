from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
import configparser
from pprint import pprint as pp

config = configparser.ConfigParser()
config.read('config.ini')
print(config.sections())


firefox_options = Options()
firefox_options.add_argument("--headless")
firefox_options.add_argument('--no-sandbox')
FIRE_OPT = firefox_options
YAHOO_URL = f'https://finance.yahoo.com/quote'
PATH_GECKO = '/usr/local/bin'


class Webscraper:
    def __init__(self, url, path_to_geckodriver, firefox_options):
        self._url = url
        self._path_to_geckodriver = path_to_geckodriver
        self.firefox_options = firefox_options
        self.__driver = None

    def start(self):
        self.__driver = webdriver.Firefox(self._path_to_geckodriver, options=self.firefox_options)
        self.__driver.get(self._url)
        time.sleep(1)
        print('Webdriver Started')

    def accept_cockies(self):
        # cookies = pickle.load(open("cookies.pkl", "rb"))
        # for cookie in cookies:
        #     driver.add_cookie(cookie)
        try:
            cockie_window = self.__driver.find_element_by_tag_name('body')
            cockie_window.find_element_by_name('agree').click()
            print('Cockies accepted.')
            # pp(self.__driver.get_cookies())
        except Exception as exe:
            print('Unable to accept cockies.')
            print(exe)

    def stop(self):
        try:
            self.__driver.close()
            print('Webscraper has finished.Quit.')
        except Exception as exe:
            print('Unable to stop the Webscraper.')
            print(exe)

    def get_yahoo_statistics(self, stock_list):
        stock_data = {}
        for stock in stock_list:
            print(f'Start webscraping {stock}')
            stock_url = f"{self._url}/{stock}/key-statistics?p={stock}"
            self.__driver.get(stock_url)
            html = self.__driver.execute_script('return document.body.innerHTML;')
            soup = BeautifulSoup(html, "html.parser")
            stock_data.update({stock: {}})
            if "Symbols similar to" in soup.get_text():
                print(f'The stock - {stock} was not found in Yahoo Finance.')
                continue
            else:
                data = soup.find(id="Main")
                tables = data.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')
                    # row_list = list()
                    for tr in rows:
                        td = tr.find_all('td')
                        if len(td) > 1:
                            stock_data[stock].update({td[0].text: td[1].text})

        return stock_data

    def tipranks(self, ticker):
        """
        https://www.tipranks.com/stocks/amd/stock-analysis
        https://www.tipranks.com/stocks/amd/price-target
        http://theautomatic.net/2019/01/19/scraping-data-from-javascript-webpage-python/
        price - target value
        <div class="client-components-stock-research-analysts-price-target-style__actualMoney">

        <div class="client-components-stock-research-analysts-price-target-style__change">
        """

        url_tr = f'https://www.tipranks.com/stocks/{ticker}/price-target'
        self.__driver.get(url_tr)
        html = self.__driver.execute_script('return document.body.innerHTML;')
        soup = BeautifulSoup(html, "html.parser")
        div_target_pr = soup.find('div', {
            'class': "client-components-stock-research-analysts-price-target-style__actualMoney"})
        print("JS content need to use Selenium")
        target_pr = div_target_pr.find('span')['title']
        # div_target_prof = soup.find('div', {
        #     'client-components-stock-research-analysts-price-target-style__change'})
        # print(div_target_prof)
        # target_change = div_target_prof.find('strong')
        # target_change_lbl = div_target_prof.text
        # print(target_change_lbl)
        # session = HTMLSession()
        # r = session.get(url_tr)
        # r.html.render()
        # print(data)
        return target_pr

    def simplywall(self, ticker):
        """
        https://simplywall.st/stocks/us/media/nasdaq-goog.l/alphabet
        https://simplywall.st/stocks/us/software/nyse-gtt/gtt-communications
        """
        pass

    def get_yahoo_list_stocks(self, stock_list):

        result = self.get_yahoo_statistics(stock_list)
        pp(result)
        row_list = list()
        for i in stock_list:
            revenue = result[i].get('Revenue (ttm)')
            peg = result[i].get('PEG Ratio (5 yr expected) 1')
            eps = result[i].get('Diluted EPS (ttm)')
            current_ratio = result[i].get('Current Ratio (mrq)')
            qeg = result[i].get('Quarterly Earnings Growth (yoy)')
            price_book = result[i].get('Price/Book (mrq)')
            oper_cash_flow = result[i].get('Operating Cash Flow (ttm)')
            net_income = result[i].get('Net Income Avi to Common (ttm)')
            beta = result[i].get('Beta (5Y Monthly) ')
            row = [i, revenue, net_income, oper_cash_flow, peg, eps,
                   current_ratio, qeg, price_book, beta]
            row_list.append(row)
        column_list = ['stock', 'revenue', 'net_income', 'oper_cash_flow', 'peg', 'eps',
                       'current_ratio', 'qeg', 'price_book', 'beta']
        df_ys = pd.DataFrame(row_list, columns=column_list)
        return df_ys

    def scroll(self, px):
        self.__driver.execute_script(f"window.scrollTo(0, {px})")
        print(f"Scrolled with {px} px")

    def screenshot(self, path):
        self.__driver.save_screenshot(path)
        print(f"Screenshot saved as {path} ")

    def test_run(self):
        try:
            browser = webdriver.Firefox(
                self._path_to_geckodriver, options=self.firefox_options)
            browser.get(self._url)
            print('Successful test run')
            browser.close()
            return True
        except Exception as exe:
            print("Something gone wrong...")
            print(exe)
            return False


def ys_run(stock_list):
    yh = Webscraper(YAHOO_URL, PATH_GECKO, FIRE_OPT)
    yh.start()
    yh.accept_cockies()
    result_df = (yh.get_yahoo_list_stocks(stock_list))
    yh.stop()
    return result_df


def tr_run():
    tr = Webscraper(YAHOO_URL, PATH_GECKO, FIRE_OPT)
    tr.start()
    result_df = (tr.tipranks('GOOGL'))
    tr.stop()
    return result_df


if __name__ == "__main__":
    stock_list = ['GOOGL', 'GTT', 'VMW', 'AMD', 'NVDA', 'TSLA', 'IBM', 'DELL']
    # ys_run(stock_list)
    print(tr_run())