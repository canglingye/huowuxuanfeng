# -*- coding:utf-8 -*-
import baostock as bs
import sys
import os
import pandas as pd

from stock.base_stock_info import BaseStockInfo


class BuildSample(object):

    def __init__(self, label_path, feature_path, sample_path, feature_conf):

        # 只有一份文件
        self.label_path = label_path

        # 多份特征文件
        self.feature_path = []
        if os.path.isdir(feature_path):
            sub_file_name_lists = os.listdir(feature_path)
            for file_name in sub_file_name_lists:
                self.feature_path.append(os.path.join(feature_path, file_name))
        else:
            self.feature_path.append(feature_path)

        self.sample_path = sample_path
        self.feature_conf = []

        with open(feature_conf, "r") as finput:
            for line in finput:
                if "#" not in line and len(line.strip()) > 0:
                    # date,code,name
                    # 以date_code为key索引name
                    self.feature_conf.append("$$".join(line.strip().split(",")))

        self.train_data = None

    def build_sample(self):
        # 3000股 * 10年 * 200天 * 6维特征大概数据量在800M，按照多维特征来看，目测1G~2G，pandas应该能搞定。
        # 对于多源特征暂时还没有处理方案orz

        # 读取所有特征
        feature_center = []
        for feature in self.feature_path:
            now_feature = pd.read_csv(feature)
            feature_center.append(now_feature)

        # outer join将所有特征拼接在一起。
        feature_center = pd.concat(feature_center)
        # 设定索引轴
        # code为通用含义，在后面特征拼接的时候可以翻译成 自身的股票代码、行业代码等等，暂时这些都不支持。。。。。。
        # feature_center = feature_center.set_index(['date', 'code'])

        label_data = pd.read_csv(self.label_path)
        self.train_data = pd.merge(label_data, feature_center, how='left', on=['date', 'code'])

    def save_sample(self):
        self.train_data.to_csv(self.sample_path, index=False)


if __name__ == "__main__":

    label_path = "../resource/model_data/label/label.dat"
    feature_path = "../resource/model_data/feature/"
    feature_conf = "../resource/model_data/feature_conf/fc.data_v1"
    sample_path = "../resource/model_data/sample/sample_v1"

    bl = BuildSample(label_path, feature_path, sample_path, feature_conf)
    bl.build_sample()
    bl.save_sample()
