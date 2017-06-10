import numpy as np
import itertools
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import json

def conv_table2list(table):
    "BeautifulSoupのtableから内容を取得してリストで返す"
    data=[]
    tbody = table.find('tbody')
    rows = tbody.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [e.text.strip() for e in cols]
        data.append([e for e in cols if e]) # Get rid of empty values
    return data

def extract_thead(table):
    "BeautifulSoupのtableからカラム情報を取得してリストで返す"
    thead=table.find("thead")
    row=thead.find_all('tr')[0]
    cols = row.find_all('th')
    return [e.text.strip() for e in cols]

# wikiから取得した楽曲情報をデータフレーム化
url = "https://imascg-slstage-wiki.gamerch.com/%E6%A5%BD%E6%9B%B2%E8%A9%B3%E7%B4%B0%E4%B8%80%E8%A6%A7"
html = urlopen(url)
bsObj = BeautifulSoup(html, "html.parser")
table = bsObj.findAll("table")[0] # wikiにtableが新たに追加されると壊れる。どうにかしたいところ
columns = extract_thead(table)
contents = conv_table2list(table)
tune_df = pd.DataFrame(contents,columns=columns)

# 比較に用いるテンプレートファイルをデータフレーム化
# ファイル名はもっと人間的が良いが、まだできてない
images = ["{}.jpg".format(i) for i in range(len(tune_df))]
template_df=pd.DataFrame(images,columns=["テンプレート名"])

# 結合、出力
df = pd.concat([tune_df,template_df],axis=1)
df.to_json(".tune_info.json",force_ascii=False)
# json.dumps(df.to_dict(),indent=4)
