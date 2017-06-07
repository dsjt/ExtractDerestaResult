#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
# デレステのリザルト画面から、データを抜き出しjsonで返すスクリプト
from PIL import Image
from PIL import ImageOps
import json
import numpy as np
import sys

regularized_number_image_size=(18,26)

# テンプレートの読み込み、二値化したnumpy配列のリストと、画像のリストを返す
def load_templates():
    templates = []
    images = []
    for i in range(10):
        im = Image.open("dat/"+str(i)+".jpg").resize(regularized_number_image_size)
        images += [im]
        value = np.asarray(im)
        templates += [np.asarray(value<np.mean(value),dtype=int)]
    return templates,images

# 画像を読み込み、二値化したnumpy配列と画像を返す
def load_num_image(fn):
    im = Image.open(fn).resize(regularized_number_image_size)
    value = np.asarray(im)
    # 中央値で二値化
    bi_value = np.asarray(im<np.mean(value),dtype=int) # 黒が0になることに注意な
    return bi_value,im

# 画像から数字を認識して返す
def recognize_image(img):
    import sys
    templates,images = load_templates()
    gray=ImageOps.grayscale(img)
    value = np.array(gray.resize(regularized_number_image_size))
    bi_value = np.asarray(value < np.mean(value),dtype=int)
    score = [np.sum(np.logical_not(np.logical_xor(t,bi_value))) for t in templates]
    answer = np.argmax(score)
    return answer

# 前方一致でjpgファイルを検索しsort、数字認識し、それらを連結して返す
def recognize_item(img_list):
    return "".join([str(recognize_image(img)) for img in img_list])

def load_configuration(fn=".crop_box.json"):
    fp=open(fn,"r")
    config=json.load(fp)
    fp.close()
    return config

def main(fn):
    # 設定読み込み
    config = load_configuration()

    # リザルト画像
    result = Image.open(fn)

    # データ初期化
    data = {}
    for item in config:
        if isinstance(config[item],list) and isinstance(config[item][0],list):
            images=[]
            for i,loc in enumerate(config[item]):
                im = result.crop(loc)
                im.save("tmp/{}{}.jpg".format(item,i))
                images+=[im]
            data[item]=int(recognize_item(images))
        elif isinstance(config[item],list):
            im = result.crop(config[item])
            im.save("tmp/{}.jpg".format(item))
            data[item]=None
        elif isinstance(config[item],dict):
            # dictの中に単一四角形は許していない
            inner_data={}
            for jtem in config[item]:
                images=[]
                for i,loc in enumerate(config[item][jtem]):
                    im = result.crop(loc)
                    im.save("tmp/{}{}.jpg".format(item,i))
                    images+=[im]
                inner_data[jtem]=int(recognize_item(images))
            data[item]=inner_data
        else:
            print("?",item)
            pass

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
