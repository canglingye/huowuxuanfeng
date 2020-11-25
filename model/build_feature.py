# -*- coding:utf-8 -*-

import backtrader as bt
import datetime
import time
import warnings
import os
from base_strategy.kdj_strategy import KDJStrategy
from stock.base_stock_info import BaseStockInfo
from stock.stock_info_source import StockInfoSource
from util.Func import get_target_stock

warnings.filterwarnings('ignore')

class BuildFeature(object):

    def __init__(self):
        pass

    def getFeature(self, output_dir, start_date, end_date, feature_strategy_name, stock_info):

        stock_code = stock_info._stock_code

        output_path = os.path.join(output_dir, "feature_%s" % stock_code)

        cerebro = bt.Cerebro(stdstats=False)
        print("123")
        if feature_strategy_name == "KDJ":
            print("here")
            cerebro.addstrategy(KDJStrategy, save_feature_path=output_path, code=stock_code)

        data = bt.feeds.PandasData(dataname=stock_info._k_data,
                                   fromdate=datetime.datetime.strptime(start_date, "%Y-%m-%d"),
                                   todate=datetime.datetime.strptime(end_date, "%Y-%m-%d")
                                   )

        cerebro.adddata(data)

        cerebro.broker.setcash(100000.0)
        cerebro.broker.setcommission(0.0017)
        cerebro.addsizer(bt.sizers.AllInSizer, percents=10)

        cerebro.run()


if __name__ == '__main__':

    # 目标股票代号集合
    target_stock_info_path = "../resource/target_stock.dat"
    # 构建数据最大起止时间点
    start_date = "2010-01-01"
    # 默认最终时间为bizdate，即当前时间的前一天
    end_date = time.strftime("%Y-%m-%d", time.localtime())

    freq = 'd'

    # ----------------默认配置-------------------------
    target_stock_info_save_path = "../resource/test/"
    target_stock_lists = get_target_stock(target_stock_info_path)
    sis = StockInfoSource()
    bf = BuildFeature()
    for target_stock, marks in target_stock_lists:
        stock_info = BaseStockInfo(stock_code=target_stock, start_date=start_date, end_date=end_date, freq=freq)
        sis.load_his_k_data(stock_info)
        path = os.path.join(target_stock_info_save_path, target_stock)
        stock_info.save_cvs(path, True)
        bf.getFeature("../resource/test/", start_date, end_date, "KDJ", stock_info)
