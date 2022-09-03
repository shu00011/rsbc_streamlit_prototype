#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Random sampling without replacement: random.sample()

import numpy as np
import random
import datetime
import pickle
import time
import plotly.figure_factory as ff
import scipy
import pandas as pd

MAXITER = 30  # counter　n回まで
# NBINS:階級数．ヒストグラムの棒の数？

def get_rbsc(score1, score2):  # score1が高いとrhoが高くなると仮説を立てている
    favor, unfavor = 0, 0
    for d1 in score1:
        for d2 in score2:
            if (d1) > (d2):
                favor += 1
            else:
                unfavor += 1
            rbsc = (favor - unfavor) / (favor + unfavor)
    return rbsc


# 標準偏差
def my_snippet(l, s, rho_star, e, counters, df):
    x=df

    xs=np.sort(x) # xを昇順にsort

    """
    全体集合xの中から大きさsのyを取り出して2等分する
    →この繰り返しがcounter
    """
    # TODO:ValueError: Sample larger than population or is negative
    y = random.sample(list(x), s)
    y1 = y[:int(len(y) * 0.5)]  # AとBそのもの．indexでなくて値そのもの．
    y2 = y[int(len(y) * 0.5):]
    rho = get_rbsc(y1, y2)

    counter = 0

    z = list(set(x) - set(y))  # z=すでに選んだ値をxから除外したもの

    while not (rho_star - e <= rho and rho <= rho_star + e) and (counter < MAXITER):

        if rho < rho_star - e:  # 求めたいpより低い時→y1の集合を高くしたい
            counter1 = 0
            while counter1 < MAXITER:
                counter1 += 1
                w = np.random.choice(z, 1)[0]  # w: 配列=zのなかから1こずつランダムに選ぶ
                """
                wがy1より大きければy1にwを加える→y1の平均値をどんどん高くする
                """
                if (np.mean(y1) < w):  # meanは引数の平均．
                    y1.append(w)
                    z.remove(w)
                    break

            counter2 = 0
            while counter2 < MAXITER:
                counter2 += 1
                w = np.random.choice(y1, 1)[0]  # w = y1から1こずつランダムに選ぶ
                if (np.mean(y1) > w):  # y1のAVGよりもwが小さい→wを抜く
                    y1.remove(w)
                    z.append(w)
                    break

            # counter3-4：y2を低くする
            counter3 = 0
            while counter3 < MAXITER:
                counter3 += 1
                w = np.random.choice(z, 1)[0]
                if (np.mean(y2) > w):
                    y2.append(w)
                    z.remove(w)
                    break

            counter4 = 0
            while counter4 < MAXITER:
                counter4 += 1
                w = np.random.choice(y2, 1)[0]
                if (np.mean(y2) < w):
                    y2.remove(w)
                    z.append(w)
                    break

        if rho > rho_star + e:  # y1を低くしてy2を高くしたい
            counter5 = 0
            while counter5 < MAXITER:
                counter5 += 1
                w = np.random.choice(z, 1)[0]
                if (np.mean(y2) < w):
                    y2.append(w)
                    z.remove(w)
                    break

            counter6 = 0
            while counter6 < MAXITER:
                counter6 += 1
                w = np.random.choice(y2, 1)[0]
                if (np.mean(y2) > w):
                    y2.remove(w)
                    z.append(w)
                    break

            counter7 = 0
            while counter7 < MAXITER:
                counter7 += 1
                w = np.random.choice(z, 1)[0]
                if (np.mean(y1) > w):
                    y1.append(w)
                    z.remove(w)
                    break

            counter8 = 0
            while counter8 < MAXITER:
                counter8 += 1
                w = np.random.choice(y1, 1)[0]
                if (np.mean(y1) < w):
                    y1.remove(w)
                    z.append(w)
                    break

        rho = get_rbsc(y1, y2)
        counter += 1

    return y1, y2


def init(userListsize, userSelectlist, userRhostar, userEps):
    """
    ハイパーパラメータ4つ．
    LISTSIZE：数の集合
    SELECTLIST：LISTSIZEから取り出す部分集合の大きさ
    （実行不可能なのはLISTSIZE<SELECTLISTのとき．
    RHO_STAR：RBSC係数p*
        RBSC_SubGenは求めたいpに近づける仕組み．
        RBSC係数p
            総当たり．仮説に反する証拠が多ければpは低くなる．
    EPS：誤差e．大きければアルゴリズムはすぐに収束する．
    """
#     LISTSIZE = np.arange(100, 901, 50)  # [100, 300, 500 ,700, 900]
#     SELECTLIST = np.arange(100, 501, 50)  # [100, 200, 300, 400, 500]
#     RHO_STAR = np.arange(0.3, 0.71, 0.04)  # [0.3, 0.5, 0.7]
#     EPS = np.arange(0.05, 0.16, 0.01)  # [0.05, 0.1, 0.15]

    LISTSIZE = userListsize
    SELECTLIST = userSelectlist
    RHO_STAR = userRhostar
    EPS = userEps

    """
    デフォルト値を設定．
    2つを固定して残り2つを比較する．（2次元で）
    出力は6つになる．
    """

    # 表を表示するためのコード
    counters = {}
    counters[LISTSIZE] = {}
    counters[LISTSIZE][SELECTLIST] = {}
    counters[LISTSIZE][SELECTLIST][RHO_STAR] = {}
    counters[LISTSIZE][SELECTLIST][RHO_STAR][EPS] = []

    return counters

# 恐らくmain関数．
def rbsc(LISTSIZE, SELECTLIST, RHO_STAR, EPS, NBINS, element):

    # NBINS:階級数．ヒストグラムの棒の数？

    counters = init(LISTSIZE, SELECTLIST, RHO_STAR, EPS)

    # np.count_nonzero()→引数の条件に合う要素の個数

    if LISTSIZE <= SELECTLIST:
        return

    A, B= my_snippet( \
        LISTSIZE, \
        SELECTLIST, \
        RHO_STAR, \
        EPS, \
        counters, \
        element)

    return A, B

