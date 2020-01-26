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
        self.genre_list = ['ラーメン', 'つけ麺']

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

        store_genre = soup.find('div', class_='rdheader-subinfo').find_all('dl')[1].find('span').text
        if store_genre not in self.genre_list:
            print('not ラーメン or つけ麺')
            self.store_id_num -= 1
            return

        ranting = soup.find('span', class_='rdheader-rating__score-val-dtl').text
        print('評価点数 : {}'.format(ranting))
        self.score = ranting

        if self.score == '-':
            print('評価なしのため除外')
            self.store_id_num -= 1
            return

        if float(self.score) < 3.0:
            print('3.0未満のため除外')
            self.store_id_num -= 1
            return

        review_href = soup.find('li', id='rdnavi-review').find('a', class_='mainnavi').get('href')
        # print(review_url)

        review_url = review_href + '?pal=tokyo&rcd=13162681&srt=&sby=&smp=1&use_type=0&rvw_part=all&lc=2'
        self.scrape_review(review_url)


    def scrape_review(self, review_url):
        # pass
        exit()
# ?pal=tokyo&rcd=13162681&srt=&sby=&smp=1&use_type=0&rvw_part=all&lc=2
# https://tabelog.com/tokyo/A1326/A132601/13162681/dtlrvwlst/?pal=tokyo&rcd=13162681&srt=&sby=&smp=1&use_type=0&rvw_part=all&lc=2

Scrape(base_url="https://tabelog.com/tokyo/rstLst/ramen/",test_mode=True)