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
from update_tune_info import tune_info
import unicodedata


def yes_or_no(question):
    while True:
        choice = input(question).lower()
        if choice in ['y', 'ye', 'yes']:
            return True
        elif choice in ['n', 'no']:
            return False


class Deresta_recognizer(object):

    def __init__(self, config_fn=".crop_box.json"):
        with open(config_fn, "r") as f:
            self.config = json.load(f)
        self.regularized_size = (18, 26)
        self.num_templates = None
        self.title_templates = None
        self.difficulty_templates = None
        pass

    def load_num_templates(self):
        "数字のテンプレートを読み込み、numpy配列として返す"
        templates = []
        for i in range(10):
            im = Image.open("dat/" + str(i) +
                            ".jpg").resize(self.regularized_size)
            temp = np.asarray(im)
            templates += [temp]
        self.num_templates = templates
        return templates

    def load_title_templates(self):
        from glob import glob
        templates = []
        for fn in glob("./dat/title/*.jpg"):
            im = Image.open(fn)
            temp = np.asarray(im)
            templates += [[os.path.basename(fn), temp]]
        templates = dict(sorted(templates, key=lambda x: x[0]))
        return templates

    def add_new_tune_UI(self, img, info):
        img.show()
        print("一致率が低いです。新規譜面ではありませんか？")
        tune_name = input("画像の曲のタイトルの一部を入力")
        if len(info[info['楽曲名'].str.contains(tune_name)]) == 0:
            print("曲名を検索しましたが、ありませんでした。" +
                  "tmp_title.jpgとして保存します" +
                  "新しく実装された曲の場合、" +
                  "update_tune_info.pyの実行を検討して下さい。")
            img.save("tmp_title.jpg")
            raise("エラー1092")
        else:
            tune_info = info[info['楽曲名'].str.contains(tune_name)]
            print(tune_info['楽曲名'])
            print("楽曲情報と一致しました。")
            temp_path = "dat/title/" + tune_info[:1]['テンプレート名'].values[0]
            yesorno = yes_or_no("{}として追加しますか？(y/n)".format(temp_path))
            if yesorno == True:
                if os.path.exists(temp_path):
                    print(temp_path + "はすでに存在しています。")
                    print("予期しない動作です。閾値のチューニングが必要です。")
                    img.show()
                    import subprocess
                    subprocess.run(["open", temp_path])
                    raise("エラー5591")
                else:
                    img.save(temp_path)
                    print("{}として保存しました。".format(temp_path))
                    print("再実行してください。")
                    raise("エラー3349")
            else:
                print("追加を取りやめます。")

    def calc_score(self, x, temp):
        "ベクトルx、yを比較し、スコアを計算し返す。現状では負の二乗誤差"
        regularized_x = (x - np.min(x)) / (np.max(x) - np.min(x))
        regularized_temp = (temp - np.min(temp)) / \
            (np.max(temp) - np.min(temp))
        return -np.sum((regularized_temp - regularized_x)**2)

    def too_small_score(self, score):
        return (score < -500)

    def classify_number(self, img):
        """
        画像がどの数字であるかを識別して返す。
        arg:
          img: 画像
        return(int)
          識別された数字
        """
        gray = ImageOps.grayscale(img)
        value = np.array(gray.resize(self.regularized_size))
        if np.std(value) < 20:  # 数字らしきものが見えん場合
            answer = 0
        else:
            score = [self.calc_score(value, temp)
                     for temp in self.num_templates]
            answer = np.argmax(score)
        return answer

    def recognize_num(self, image_list):
        "画像リストの数字を認識し、ひとつづきの整数と解釈して返す"
        return int("".join([str(self.classify_number(img)) for img in image_list]))

    def recognize_title(self, img):
        "画像を認識し、曲情報の表を返す"
        from glob import glob

        # テンプレートの読み込み
        templates = self.load_title_templates()

        # 楽曲情報の取得
        info = tune_info(".tune_info.csv").load_info()

        # 一致率計算
        value = np.array(img)
        scores = [[key, self.calc_score(value, templates[key])]
                  for key in templates]
        answer = max(scores, key=lambda x: x[1])
        answer[0] = unicodedata.normalize('NFKC', answer[0])

        # 一致率が低する場合、テンプレート情報として追加する
        if self.too_small_score(answer[1]):
            self.add_new_tune_UI(img, info)
            return -1

        index = (info['テンプレート名'] == answer[0])
        if not any(index):
            print("タイトルテンプレートとtune_infoが一致しません")
            return None
        else:
            name = info[info['テンプレート名'] == answer[0]]['楽曲名'].values[0]
            return info[info['楽曲名'] == name]

    def recognize_difficulty(self, img):
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
            templates += [[os.path.basename(fn), temp]]
        # 対象画像の読み込み
        value = np.array(img)
        scores = [[item[0], self.calc_score(value, item[1])]
                  for item in templates]
        answer = max(scores, key=lambda x: x[1])[0].split(".")[0].upper()
        return answer

    def recognize_exists(self, img, template_fn):
        with Image.open(template_fn) as im:
            temp = np.array(im)
        # 対象画像の読み込み
        value = np.array(img)
        return bool(self.calc_score(value, temp) > -200)

    def extract(self, fn):
        if self.num_templates is None:
            self.load_num_templates()

        self.result = Image.open(fn).resize((1136, 640))
        # データ初期化
        self.data = {"date": datetime.now().strftime('%y/%m/%d %H:%M:%S:%f'),
                     "filename": fn}
        info = None
        for item in self.config:
            if item == 'title':
                img = self.result.crop(self.config[item])
                img.save(datetime.now().strftime('tmp/title.jpg'))
                info = self.recognize_title(img)
                self.data[item] = info['楽曲名'].values[0]
            elif item == 'difficulty':
                img = self.result.crop(self.config[item])
                img.save(datetime.now().strftime('tmp/difficulty.jpg'))
                difficulty = self.recognize_difficulty(img)
                self.data[item] = difficulty
            elif item == 'full_combo':
                img = self.result.crop(self.config[item])
                img.save("tmp/{}.jpg".format(item))
                self.data[item] = self.recognize_exists(
                    img, "./dat/full_combo.jpg")
            elif item == 'new_record':
                img = self.result.crop(self.config[item])
                img.save("tmp/{}.jpg".format(item))
                self.data[item] = self.recognize_exists(
                    img, "./dat/new_record.jpg")
            elif isinstance(self.config[item], list) and \
                    isinstance(self.config[item][0], list):
                images = []
                for i, loc in enumerate(self.config[item]):
                    im = self.result.crop(loc)
                    im.save("tmp/{}{}.jpg".format(item, i))
                    images += [im]
                self.data[item] = self.recognize_num(images)
            elif isinstance(self.config[item], list):
                im = self.result.crop(self.config[item])
                im.save("tmp/{}.jpg".format(item))
                self.data[item] = None
            else:
                print("?", item)
                pass
        return self.data


def main(fn):
    # 設定読み込み
    dr = Deresta_recognizer()
    data = dr.extract(fn)
    if data == -1:
        return -1
    print(json.dumps(data, indent=4, ensure_ascii=False))
    return data

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='デレステのリザルト画像からスコアなどの情報を抽出し、'
        + 'jsonで出力するスクリプト')
    parser.add_argument('filename', metavar='fn', type=str,
                        help='リザルト画面をスクショしたファイルの名前')
    args = parser.parse_args()

    main(args.filename)
