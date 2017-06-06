#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
# デレステのリザルト画面から、データを抜き出しjsonで返すスクリプト
from PIL import Image
from PIL import ImageOps
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
    threshold_value = np.asarray(im<np.mean(value),dtype=int) # 黒が0になることに注意な
    return threshold_value,im

# 画像から数字を認識して返す
def recognize_image(img):
    import sys
    templates,images = load_templates()
    value = np.array(img.resize(regularized_number_image_size))
    bi_value = np.asarray(value < np.mean(value),dtype=int)
    score = [np.sum(np.logical_not(np.logical_xor(t,bi_value))) for t in templates]
    answer = np.argmax(score)
    return answer

# 前方一致でjpgファイルを検索しsort、数字認識し、それらを連結して返す
def recognize_item(img_list):
    return "".join([str(recognize_image(img)) for img in img_list])

def main(fn):
    # リザルト画像
    result = Image.open(fn)
    grey = ImageOps.grayscale(result)

    data = {}

    # 曲名
    title=result.crop((172,125,371,180))
    data['title']=None
    title.save("tmp/title.jpg")
    # 難易度
    difficulty=result.crop((173,100,269,120))
    data['difficulty']=None
    difficulty.save("tmp/difficulty.jpg")
    # 楽曲Lv
    lv=[grey.crop((419,103,430,118)),
        grey.crop((431,103,442,118))]
    data['level']=int(recognize_item(lv))
    for i,l in enumerate(lv):
        l.save("tmp/lv{}.jpg".format(i))

    data['judge']={}
    # perfect
    perfect=[grey.crop((371,206,387,229)),
             grey.crop((390,206,406,229)),
             grey.crop((409,206,425,229)),
             grey.crop((428,206,444,229))]
    data['judge']['perfect']=int(recognize_item(perfect))
    for i,l in enumerate(perfect):
        l.save("tmp/perfect{}.jpg".format(i))

    # great
    great=[grey.crop((371,241,387,264)),
           grey.crop((390,241,406,264)),
           grey.crop((409,241,425,264)),
           grey.crop((428,241,444,264))]
    data['judge']['great']=int(recognize_item(great))
    for i,l in enumerate(great):
        l.save("tmp/great{}.jpg".format(i))
    # nice
    nice=[grey.crop((371,276,387,299)),
          grey.crop((390,276,406,299)),
          grey.crop((409,276,425,299)),
          grey.crop((428,276,444,299))]
    data['judge']['nice']=int(recognize_item(nice))
    for i,l in enumerate(nice):
        l.save("tmp/nice{}.jpg".format(i))

    # bad
    bad=[grey.crop((371,311,387,334)),
         grey.crop((390,311,406,334)),
         grey.crop((409,311,425,334)),
         grey.crop((428,311,444,334))]
    data['judge']['bad']=int(recognize_item(bad))
    for i,l in enumerate(bad):
        l.save("tmp/bad{}.jpg".format(i))
    # miss
    miss=[grey.crop((371,346,387,369)),
          grey.crop((390,346,406,369)),
          grey.crop((409,346,425,369)),
          grey.crop((428,346,444,369))]
    data['judge']['miss']=int(recognize_item(miss))
    for i,l in enumerate(miss):
        l.save("tmp/miss{}.jpg".format(i))

    # combo
    combo=[grey.crop((364,400,382,425)),
           grey.crop((385,400,403,425)),
           grey.crop((406,400,424,425)),
           grey.crop((427,400,445,425))]
    data['combo']=int(recognize_item(combo))
    for i,l in enumerate(combo):
        l.save("tmp/combo{}.jpg".format(i))

    # fullcombo
    full_combo=result.crop((372,368,477,396))
    data['full_combo']=None
    full_combo.save("tmp/full_combo.jpg")
    # new record
    new_record=result.crop((372,450,477,479))
    data['new_record']=None
    new_record.save("tmp/new_record.jpg")
    # score
    score=[grey.crop((301,480,319,506)),
           grey.crop((322,480,340,506)),
           grey.crop((343,480,361,506)),
           grey.crop((364,480,382,506)),
           grey.crop((385,480,403,506)),
           grey.crop((406,480,424,506)),
           grey.crop((427,480,445,506))]
    data['score']=int(recognize_item(score))
    for i,l in enumerate(score):
        l.save("tmp/score{}.jpg".format(i))

    # high_score
    high_score=[grey.crop((321,521,337,542)),
                grey.crop((339,521,355,542)),
                grey.crop((357,521,373,542)),
                grey.crop((375,521,391,542)),
                grey.crop((393,521,409,542)),
                grey.crop((411,521,427,542)),
                grey.crop((429,521,445,542))]
    data['high_score']=int(recognize_item(high_score))
    for i,l in enumerate(high_score):
        l.save("tmp/high_score{}.jpg".format(i))

    # PRP
    PRP=[grey.crop((332,573,347,592)),
         grey.crop((348,573,363,592)),
         grey.crop((364,573,379,592)),
         grey.crop((380,573,395,592))]
    data['PRP']=int(recognize_item(PRP))
    for i,l in enumerate(PRP):
        l.save("tmp/PRP{}.jpg".format(i))

    import json
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
