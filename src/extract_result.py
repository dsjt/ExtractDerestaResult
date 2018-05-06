#!/usr/bin/python3
# -*- coding: utf-8 -*-
# デレステのリザルト画面から、データを抜き出しjsonで返すスクリプト
from PIL import Image
from PIL import ImageOps
import json
import numpy as np
import os
from datetime import datetime
from update_tune_info import tune_info
import unicodedata


def yes_or_no(question):
    """
    ユーザーにyes/noを尋ね、結果をTrue/Falseで返す
    """
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
        """
        数字のテンプレートを dat/{数字}.jpg ファイルから読み込み、numpy配列として返す
        """
        templates = []
        for i in range(10):
            im = Image.open("dat/" + str(i) +
                            ".jpg").resize(self.regularized_size)
            temp = np.asarray(im)
            templates += [temp]
        self.num_templates = templates
        return templates

    def load_title_templates(self):
        """
        dat/title/{曲名}.jpg から曲名画像を読み取り、numpy配列として返す。
        """
        from glob import glob
        templates = []
        for fn in glob("./dat/title/*.jpg"):
            im = Image.open(fn)
            temp = np.asarray(im)
            templates += [[os.path.basename(fn), temp]]
        templates = dict(sorted(templates, key=lambda x: x[0]))
        return templates

    def add_new_tune_UI(self, img, info):
        """
       一致率が低いとき、新規楽曲の画像であると考えられる。
        新規楽曲のデータをインタラクティブに追加するためのユーザーインターフェースを提供する。
        1. 入力画像から楽曲名部分を切り取り、表示する
        2. 楽曲名の一部を入力してもらう
        3. .tune_info.csv ファイルを検索し、楽曲情報を表示し、認識できる楽曲に追加するかを尋ねる。
        args:
            img: 画像
            info: .tune_info.csvから読み取った楽曲情報
        return: 未定義
        """
        img.show()
        print("一致率が低いです。新規譜面ではありませんか？")
        tune_name = input("画像の曲のタイトルの一部を入力")
        if len(info[info['楽曲名'].str.contains(tune_name)]) == 0:
            img.save("tmp_title.jpg")
            print("曲名を検索しましたが、ありませんでした。" +
                  "tmp_title.jpgとして保存します" +
                  "新しく実装された曲の場合、" +
                  "update_tune_info.pyの実行を検討して下さい。")
            raise ValueError("曲名が見つかりません")
        else:
            tune_info = info[info['楽曲名'].str.contains(tune_name)]
            print(tune_info['楽曲名'])
            print("楽曲情報と一致しました。")
            temp_path = "dat/title/" + tune_info[:1]['テンプレート名'].values[0]
            yesorno = yes_or_no("{}として追加しますか？(y/n)".format(temp_path))
            if yesorno:
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

    def calc_score(self, x, y):
        """
        numpy配列のx、yを比較し、一致率スコアを計算して返す。
        現状では負の二乗誤差を一致率スコアとしている。
        args:
            x: numpy配列 次元はyと同じであれば不問
            y: numpy配列 次元はxと同じであれば不問
        return:
            小数。一致率のスコアを表す。大きいほど、一致している。
        """
        regularized_x = (x - np.min(x)) / (np.max(x) - np.min(x))
        regularized_y = (y - np.min(y)) / (np.max(y) - np.min(y))
        return -np.sum((regularized_y - regularized_x)**2)

    def too_small_score(self, score):
        """
        一致率を調べ、小さすぎればTrue, そうでなければFalseを返す。
        後の修正に備えている。
        """
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
        """
        画像からなるリストを受け取り、各画像の数字を認識し、ひとつづきの整数と解釈して返す。
        args:
            image_list: 要素が画像データからなるリスト
        return:
            整数
        """
        num_list = [str(self.classify_number(img)) for img in image_list]
        return int("".join(num_list))

    def recognize_title(self, img):
        """
        画像を認識し、曲情報の表を返す
        曲情報は .tune_info.csv からpandasのデータフレームとして取得する。
        args:
            img: 画像データ
        return:
            pandasのデータフレーム
        """
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
        """
        画像データから難易度を認識し、難易度を文字列で返す。
        args:
            img: 画像データ
        return:
            文字列。難易度を表す。
        """
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

    def recognize_exists(self, img, exist_fn, notex_fn):
        """
        画像の存在を認識する。例えば、フルコンボ表示が存在するかを判定する。
        args:
            img: 入力画像から該当部分を切り取った画像データ
            exist_fn: 存在する場合の画像のファイル名
            notex_fn: 存在しない場合の画像のファイル名
        return:
            真偽値。存在すると判定すればTrue, そうでなければFalse
        """
        with Image.open(exist_fn) as im:
            exist_val = np.array(im)
        with Image.open(notex_fn) as im:
            notex_val = np.array(im)
        # 対象画像の読み込み
        value = np.array(img)

        exist_score = self.calc_score(value, exist_val)
        notex_score = self.calc_score(value, notex_val)
        return bool(exist_score > notex_score)

    def extract(self, fn):
        """
        ファイルを認識し、楽曲情報や得点を抽出し、辞書形式で返す。
        args:
            fn: リザルト画像のファイル名
        return:
            辞書
        """
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
                    img, "./dat/full_combo.jpg", "./dat/not_full_combo.jpg")
            elif item == 'new_record':
                img = self.result.crop(self.config[item])
                img.save("tmp/{}.jpg".format(item))
                self.data[item] = self.recognize_exists(
                    img, "./dat/new_record.jpg", "./dat/not_new_record.jpg")
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
    try:
        dr = Deresta_recognizer()
        data = dr.extract(fn)
        if data == -1:
            return -1
        print(json.dumps(data, indent=4, ensure_ascii=False))
        return data
    except ValueError as err:
        print(err)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='デレステのリザルト画像からスコアなどの情報を抽出し、'
        + 'jsonで出力するスクリプト')
    parser.add_argument('filename', metavar='fn', type=str,
                        help='リザルト画面をスクショしたファイルの名前')
    args = parser.parse_args()

    main(args.filename)
