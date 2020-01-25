import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time

class Scrape:
    def __init__(self, base_url, test_mode = False, pref = '東京都内', begin_page = 1, end_page = 10):
        self.store_id = ''
        self.store_id_num = 0
        self.store_name = ''
        self.score = 0
        self.pref = pref
        self.review_cnt = 0
        self.columns = ['store_id', 'store_name', 'score', 'pref', 'review_cnt', 'review']
        self.df = pd.DataFrame(columns=self.columns)
        self.__regexcomp = re.compile(r'\n|\s')

        page_num = begin_page

        if test_mode:
            list_url = base_url + str(page_num) + '/?Srt=D&SrtT=rt&sort_mode=1'
            self.scrape_list(list_url, mode=test_mode)
        else:
            while True:
                list_url = base_url + str(page_num) + '/?Srt=D&SrtT=rt&sort_mode=1'
                if self.scrape_list(list_url, mode=test_mode) != True:
                    break

                if page_num >= end_page:
                    break

                page_num += 1

        return

    def scrape_list(self, list_url, mode):
        r = requests.get(list_url)
        if r.status_code != requests.codes.ok:
            return False

        soup = BeautifulSoup(r.content, 'html.parser')
        soup_a_list = soup.find_all('a', class_='list-rst__rst-name-target')

        if len(soup_a_list) < 1:
            return False

        if mode:
            for soup_a in soup_a_list[:2]:
                item_url = soup_a.get('href')
                self.store_id_num += 1
                self.score_item(item_url, mode)
                print(item_url)


    def score_item(self, item_url, mode):
        start = time.time()
        r = requests.get(item_url)
        if r.status_code != requests.codes.ok:
            print(f'error:not found{ item_url }')
            return

        soup = BeautifulSoup(r.content, 'html.parser')
        store_name = soup.find('h2', class_='display-name').find('span').string
        if self.store_id_num % 10 == 0:
            print('{} -> {}'.format(self.store_id_num, store_name))
        
        self.store_name = store_name.strip()
        print(self.store_name)
        exit()

        exit()


Scrape(base_url="https://tabelog.com/tokyo/rstLst/ramen/",test_mode=True)