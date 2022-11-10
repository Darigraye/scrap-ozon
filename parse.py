from config import START_URL, DOMAIN_NAME
from bs4 import BeautifulSoup

import time
import json

import re
import undetected_chromedriver as uc


class ScrapOzon():
    NUMBER_PHONES_TO_SCRAPPING = 100

    def __init__(self):
        self.count_scraped_phones = 0
        self.number_current_page = 1
        self.driver = uc.Chrome()

    def __get_pages_html(self):
        while self.count_scraped_phones != 100:
            self.driver.get(START_URL + f'&page={self.number_current_page}')
            yield self.driver.page_source
            self.number_current_page += 1

    def __type_is_phone(self, headline):
        span = headline.next_sibling.contents[0]
        return re.search('Тип: [Сс]мартфон', span.text) 

    def __get_hrefs_to_phone(self, product_hrefs):
        hrefs = []
        for headline in product_hrefs:
                
                if self.__type_is_phone(headline):
                    href = headline.get('href')
                    hrefs.append(DOMAIN_NAME + href)
                    print(self.count_scraped_phones)
        return hrefs

    def __scroll_page(self):
        SCROLL_PAUSE_TIME = 10
        last_height = self.driver.execute_script(
                                "return document.body.scrollHeight")
        while True:
            self.driver.execute_script(
                                "window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)
            new_height = self.driver.execute_script(
                                "return document.body.scrollHeight")

            if new_height == last_height:
                break
            last_height = new_height

    def __preparing_data(self, data):
        lst_data = data.split()
        len_name_os = len(lst_data[1])
        name_os = lst_data[1][0 : len_name_os // 2]
        version_os = lst_data[-1]
        return ' '.join((name_os, version_os))

    def __get_data_about_os(self):
        self.__scroll_page()
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        blocks_characteristic_div = soup.find('div', id='section-characteristics')

        if blocks_characteristic_div:
            blocks_characteristic = blocks_characteristic_div.contents[1]
            for block in blocks_characteristic.contents:
                for data in block:
                    for item in data.contents:
                        if re.search(r'Версия', item.text):
                            return self.__preparing_data(item.text)
        else:
            self.count_scraped_phones = self.count_scraped_phones - 1 \
                                        if self.count_scraped_phones > 0 else 0     

    def parse_pages(self):
        self.driver.execute_script("window.open()")
        
        with open('os_phones.json', 'w', encoding='utf-8') as fd:
            for html in self.__get_pages_html():
                soup = BeautifulSoup(html, 'lxml')
                product_hrefs = soup.find_all('a' , class_='tile-hover-target k8n')
                urls_to_products = self.__get_hrefs_to_phone(product_hrefs)

                self.driver.switch_to.window(self.driver.window_handles[1])
                for url in urls_to_products:
                    self.driver.get(url)
                    data_about_os = self.__get_data_about_os()
                    if data_about_os:
                        self.count_scraped_phones += 1
                        json.dump(data_about_os, fd, indent=4, ensure_ascii=False)
                    if self.count_scraped_phones == self.NUMBER_PHONES_TO_SCRAPPING:
                        break

                self.driver.switch_to.window(self.driver.window_handles[0])
            

if __name__ == '__main__':
    try:
        uc.TARGET_VERSION = 78 
        s = ScrapOzon()
        s.parse_pages()
    except Exception as e:
        print(e)
