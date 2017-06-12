import numpy as np
import itertools
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import json


class html_table_parser(object):

    def __init__(self):
        pass

    def extract_thead(self, table):
        "BeautifulSoupのtableからカラム情報を取得してリストで返す"
        thead = table.find("thead")
        row = thead.find_all('tr')[0]
        cols = row.find_all('th')
        return [e.text.strip() for e in cols]

    def conv_table2list(self, table):
        "BeautifulSoupのtableから内容を取得してリストで返す"
        data = []
        tbody = table.find('tbody')
        rows = tbody.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [e.text.strip() for e in cols]
            data.append([e for e in cols if e])  # Get rid of empty values
        return data

    def get_df_from(self, url):
        # pandas.read_htmlを使えればそちらを使いたい
        html = urlopen(url)
        bsObj = BeautifulSoup(html, "html.parser")
        # wikiにtableが新たに追加されると壊れる。いずれどうにか
        table = bsObj.findAll("table")[0]
        columns = self.extract_thead(table)
        contents = self.conv_table2list(table)
        self.data = pd.DataFrame(contents, columns=columns)
        return self.data


class tune_info(html_table_parser):

    def __init__(self, fn):
        super().__init__()
        self.fn = fn

    def load_info(self):
        self.data = pd.read_csv(self.fn)
        return self.data

    def save_info(self):
        self.data.to_csv(self.fn)
        return self.data


def test():
    ti = tune_info(".tune_info.csv")
    url = "https://imascg-slstage-wiki.gamerch.com/%E6%A5%BD%E6%9B%B2%E8%A9%B3%E7%B4%B0%E4%B8%80%E8%A6%A7"
    dfs = ti.get_df_from(url)
    templates = dfs['楽曲名'].str.cat(["jpg"] * len(dfs), sep=".")
    templates.name = "テンプレート名"
    ti.data = pd.concat([dfs, templates], axis=1)
    ti.save_info()
