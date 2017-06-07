#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
# デレステのリザルト画面から、データを抜き出しjsonで返すスクリプト
from PIL import Image
from PIL import ImageOps
import json
import numpy as np
import sys
import os
import pandas as pd
from datetime import datetime

class Deresta_recognizer(object):
    def __init__(self,config_fn=".crop_box.json"):
        with open(config_fn,"r") as f:
            self.config=json.load(f)
        self.regularized_size=(18,26)
        self.num_templates=None
        self.title_templates=None
        self.difficulty_templates=None
        pass

    def load_num_templates(self):
        "数字のテンプレートを読み込み、numpy配列として返す"
        templates = []
        for i in range(10):
            im = Image.open("dat/"+str(i)+".jpg").resize(self.regularized_size)
            temp = np.asarray(im)
            templates+=[temp]
        self.num_templates=templates
        return templates


    def load_templates(self):
        # self.load_title_tamplates()
        # self.load_difficulty_tamplates()
        self.load_num_templates()

    def calc_score(self,x,temp):
        "ベクトルx、yを比較し、スコアを計算し返す。現状では負の二乗誤差"
        regularized_x = (x-np.min(x))/(np.max(x)-np.min(x))
        regularized_temp = (temp-np.min(temp))/(np.max(temp)-np.min(temp))
        return -np.sum((regularized_temp-regularized_x)**2)

    def classify_number(self,img):
        """
        画像がどの数字であるかを識別して返す。
        arg:
          img: 画像
        return(int)
          識別された数字
        """
        gray = ImageOps.grayscale(img)
        value = np.array(gray.resize(self.regularized_size))
        if np.std(value) < 10: # 数字らしきものが見えん場合
            answer = 0
        else:
            score = [self.calc_score(value,temp) for temp in self.num_templates]
            answer = np.argmax(score)
        return answer

    def recognize_num(self,image_list):
        "画像リストの数字を認識し、ひとつづきの整数と解釈して返す"
        return int("".join([str(self.classify_number(img)) for img in image_list]))

    def recognize_title(self,img):
        "画像を認識し、曲情報の表を返す"
        from glob import glob

        # テンプレートの読み込み
        templates = []
        for fn in glob("./dat/tunes/*.jpg"):
            im = Image.open(fn)
            temp = np.asarray(im)
            templates+=[[os.path.basename(fn), temp]]
        templates = dict(sorted(templates,key=lambda x: x[1]))

        # 対象画像の読み込み
        value = np.array(img)

        scores = [[key,self.calc_score(value,templates[key])] for key in templates]
        # 最大値が小さすぎるようなら、識別不能の新データと解釈して保存しておきたい
        answer=max(scores,key=lambda x:x[1])

        info=pd.read_json(".tune_info.json")
        name = info[info['テンプレート名']==answer[0]]['楽曲名'].values[0]
        return info[info['楽曲名']==name]

    def recognize_difficulty(self,img):
        templates = []
        for fn in ["./dat/debut.jpg",
                   "./dat/regular.jpg",
                   "./dat/pro.jpg",
                   "./dat/master.jpg",
                   "./dat/master+.jpg"]:
            if not os.path.exists(fn):
                continue
            im = Image.open(fn)
            temp = np.asarray(im)
            templates+=[[os.path.basename(fn), temp]]
        # 対象画像の読み込み
        value = np.array(img)
        import pdb; pdb.set_trace()
        scores = [[item[0],self.calc_score(value,item[1])] for item in templates]
        answer=max(scores,key=lambda x:x[1])[0].split(".")[0].upper()
        return answer

    def extract(self,fn):
        if (self.num_templates is None or \
            self.title_templates is None):
            self.load_templates()

        self.result = Image.open(fn)
        # データ初期化
        self.data = {"date": datetime.now().strftime('%y%m%d-%H%M%S-%f')}
        info = None
        for item in self.config:
            if item == 'title':
                img = self.result.crop(self.config[item])
                info = self.recognize_title(img)
                self.data[item]=info['楽曲名'].values[0]
            elif item == 'difficulty':
                img = self.result.crop(self.config[item])
                difficulty=self.recognize_difficulty(img)
                self.data[item]=difficulty
            elif item == 'full_combo':
                img = self.result.crop(self.config[item])
                difficulty=self.recognize_difficulty(img)
                self.data[item]=difficulty
            elif isinstance(self.config[item],list) and \
               isinstance(self.config[item][0],list):
                images=[]
                for i,loc in enumerate(self.config[item]):
                    im = self.result.crop(loc)
                    im.save("tmp/{}{}.jpg".format(item,i))
                    images+=[im]
                self.data[item]=self.recognize_num(images)
            elif isinstance(self.config[item],list):
                im = self.result.crop(self.config[item])
                im.save("tmp/{}.jpg".format(item))
                self.data[item]=None
            else:
                print("?",item)
                pass
        return self.data


def main(fn):
    # 設定読み込み
    dr = Deresta_recognizer()
    data = dr.extract(fn)
    print(json.dumps(data,indent=4))
    return data

if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='デレステのリザルト画像からスコアなどの情報を抽出し、'\
                   +'jsonで出力するスクリプト')
    parser.add_argument('filename', metavar='fn', type=str,
                        help='リザルト画面をスクショしたファイルの名前')
    args = parser.parse_args()

    main(args.filename)
