# デレステのリザルト画面から、数字を抜き出して、新しいファイル名で保存するスクリプト

from datetime import datetime
from logging import getLogger, FileHandler, DEBUG, StreamHandler
import logging
from PIL import Image
from PIL import ImageOps
from sklearn.neighbors import KNeighborsClassifier
import numpy as np
import json
import os
from functools import reduce
import shutil
from glob import glob
from uuid import uuid4

logger = getLogger(__name__)
sh = logging.StreamHandler()
formatter = logging.Formatter('[%(name)s] %(message)s')
sh.setFormatter(formatter)
logger.addHandler(sh)
logger.setLevel(DEBUG)

logger.debug(datetime.now().strftime("[%y/%m/%d %H:%M:%S]"))

regularized_size = (18, 26)


def load_num_templates():
    """
    数字のテンプレートを dat/{数字}.jpg ファイルから読み込み、numpy配列として返す
    """
    templates = []
    for i in range(10):
        im = Image.open("dat/" + str(i) +
                        ".jpg").resize(regularized_size)
        temp = np.asarray(im)
        templates += [temp]
    num_templates = templates
    return templates


def setup_knn():
    knn = KNeighborsClassifier(n_neighbors=1)
    X = load_num_templates()
    X_vectorized = np.asarray([x.ravel() for x in X])
    y = range(10)
    knn.fit(X_vectorized, np.asarray(y))
    return knn


def classify_number(img):
    """
    画像がどの数字であるかを識別して返す。
    arg:
      img: 画像
    return(int)
      識別された数字
    """
    # てかり対策として、RGBのBのみを見る
    arr = np.array(img)
    newimg = Image.fromarray(np.asarray(img)[:, :, 2])
    gray = newimg
    # gray = ImageOps.grayscale(img)
    value = np.array(gray.resize(regularized_size))
    if np.std(value) < 20:  # 数字らしきものが見えん場合
        answer = 0
    else:
        answer = int(knn.predict(value.reshape(1, -1)))
        proba = knn.predict_proba(value.reshape(1, -1))
        proba_dic = {(i, f) for i, f in enumerate(list(proba.ravel()))}
        res = str(max(proba_dic, key=lambda x: x[1]))
        res += " ..."
        logger.debug(res+reduce(lambda x, y: str(x)+", "+str(y),
                                list(proba.ravel())))
        # str(proba.argmax()) + " ... " +
        # ",".join(map(str, list(proba[proba > 0].argsort()))))
        # logger.debug(sorted(proba_dic, key=lambda x: x[1], reverse=True))
    return answer


def recognize_num(image_list):
    """
    画像からなるリストを受け取り、各画像の数字を認識し、ひとつづきの整数と解釈して返す。
    args:
        image_list: 要素が画像データからなるリスト
    return:
        整数
    """
    num_list = [str(classify_number(img)) for img in image_list]
    return int("".join(num_list))


# 設定ファイルを読み込む
config_fn = ".crop_box.json"
with open(config_fn, "r") as f:
    config = json.load(f)

# ディレクトリ削除・作成
for i in range(10):
    path = "tmpdata/{}".format(i)
    if os.path.exists(path):
        shutil.rmtree(path)
        logger.debug("shutil.rmtree({}) done.".format(path))
    os.mkdir(path)
    logger.debug("os.mkdir({}) done.".format(path))

knn = setup_knn()
files = glob("test02/*")
for fn in files:
    result = Image.open(fn).resize((1136, 640))
    # 数字を抜き出して
    for item in config:
        if isinstance(config[item], list) and \
           isinstance(config[item][0], list):
            logger.debug(item)
            for i, loc in enumerate(config[item]):
                im = result.crop(loc)
                im.save("tmpdata/{}/{}.jpg".format(classify_number(im), uuid4()))
