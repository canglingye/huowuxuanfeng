# -*- coding:utf-8 -*-
import baostock as bs
import sys
import pandas as pd

print("be happy!")

class BaseStockInfo(object):

    def __init__(self, stock_code, start_date, end_date, freq="d"):
        self._freq = freq
        self._k_data = None
        self._k_data_plus = None
        self._stock_code = stock_code
        self._start_date = start_date
        self._end_date = end_date

    def save_cvs(self, path, code_reverse=False):
        # 格式问题，默认格式为sh.000001，修改为000001.sh
        temp_data = self._k_data
        temp_data['code'] = temp_data['code'].map(lambda x: '.'.join(x.split(".")[::-1]))
        self._k_data.to_csv(path)

    def load_csv(self, path):
        self._k_data = pd.read_csv(path)

    def __str__(self):
        return str(self._k_data)






