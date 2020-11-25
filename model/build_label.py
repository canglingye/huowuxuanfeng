# -*- coding:utf-8 -*-
import baostock as bs
import sys
import os
import pandas as pd

from stock.base_stock_info import BaseStockInfo


class BuildLabel(object):

    def __init__(self, input_path, output_path):

        self.input_paths = []
        self.output_path = output_path
        self.output_labels = None

        if os.path.isdir(input_path):
            sub_file_name_lists = os.listdir(input_path)
            for file_name in sub_file_name_lists:
                self.input_paths.append(os.path.join(input_path, file_name))
        else:
            self.input_paths.append(input_path)

    def build_label(self, default_pos=1, default_neg=0):
        # 如果7天之后，股价上涨5%以及以上，标记为正样本
        reward_cycle = 7

        output_label = []
        for input_path in self.input_paths:
            origin_data = pd.read_csv(input_path)
            for index in range(origin_data.index.size - reward_cycle):
                label = default_neg
                if origin_data.loc[index + reward_cycle]["close"] > origin_data.loc[index]["close"]:
                    label = default_pos
                output_label.append([origin_data.loc[index]["date"], origin_data.loc[index]["code"], label])
        self.output_labels = pd.DataFrame(data=output_label, columns=["date", "code", "label"])

    def save_label(self):
        self.output_labels.to_csv(self.output_path, index=False)


if __name__ == "__main__":

    input_path = "../resource/stock_info"
    output_path = "../resource/model_data/label/label.dat"
    bl = BuildLabel(input_path, output_path)
    bl.build_label()
    bl.save_label()