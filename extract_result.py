#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
# デレステのリザルト画面から、データを抜き出しjsonで返すスクリプト
from PIL import Image
from PIL import ImageOps
import json
import numpy as np
import sys

class Deresta_recognizer(object):
    def __init__(self,config_fn=".crop_box.json"):
        with open(config_fn,"r") as f:
            self.config=json.load(f)
        self.regularized_size=(18,26)
        self.templates=None
        pass

    def load_templates(self):
        "テンプレートを読み込み、numpy配列として返す"
        templates = []
        for i in range(10):
            im = Image.open("dat/"+str(i)+".jpg").resize(self.regularized_size)
            temp = np.asarray(im)
            templates+=[temp]
        return templates

    def calc_score(self,x,y):
        "ベクトルx、yを比較し、スコアを計算し返す。現状では負の二乗誤差"
        regularized_x = (x-np.min(x))/(np.max(x)-np.min(x))
        regularized_y = (y-np.min(y))/(np.max(y)-np.min(y))
        return -np.sum((regularized_y-regularized_x)**2)

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
        score = [self.calc_score(temp,value) for temp in self.templates]
        answer = np.argmax(score)
        return answer

    def recognize(self,image_list):
        "画像リストの数字を認識し、ひとつづきの整数と解釈して返す"
        return int("".join([str(self.classify_number(img)) for img in image_list]))

    def extract(self,fn):
        if self.templates is None:
            self.templates=load_templates()

        self.result = Image.open(fn)
        # データ初期化
        self.data = {}
        for item in self.config:
            if isinstance(self.config[item],list) \
               and isinstance(self.config[item][0],list):
                images=[]
                for i,loc in enumerate(self.config[item]):
                    im = self.result.crop(loc)
                    im.save("tmp/{}{}.jpg".format(item,i))
                    images+=[im]
                self.data[item]=self.recognize(images)
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
