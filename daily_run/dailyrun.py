# -*- coding:utf-8 -*-
import sys, os
import matplotlib.pyplot as plt
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import warnings
import backtrader as bt
import datetime

from base_strategy.kdj_strategy import KDJStrategy
from stock.base_stock_info import BaseStockInfo
from stock.stock_info_source import StockInfoSource

warnings.filterwarnings('ignore')
# plt.rcParams['figure.figsize'] = (16.0, 4.0)

print("be happy!")


class DailyRun(object):

    def __init__(self, stock_path, account_dir, start_date, end_date):

        self.stock_path = stock_path
        self.start_date = start_date
        self.end_date = end_date
        self.cerebros = {}

        self.target_stocks_list = []
        self.target_stock_infos = []

        self.read_target_stocks_list(stock_path)
        self.read_target_stock_infos()

    def read_target_stocks_list(self, path):
        with open(path, "r") as finput:
            for line in finput:
                if '#' not in line:
                    line = line.strip().split(",")
                    stock_code = line[0]
                    self.target_stocks_list.append([stock_code])
                    self.cerebros[stock_code] = bt.Cerebro(stdstats=False)

        print("self.cerebros", self.cerebros)

    def read_target_stock_infos(self):
        assert (self.target_stocks_list is not None and len(self.target_stocks_list) >= 1)

        stock_info_source = StockInfoSource()
        for stock in self.target_stocks_list:
            stock_code = stock[0]
            bs = BaseStockInfo(stock_code, self.start_date, self.end_date)
            stock_info_source.load_his_k_data(bs)
            self.target_stock_infos.append(bs)
            print(bs._k_data)
            data = bt.feeds.PandasData(dataname=bs._k_data,
                                       fromdate=datetime.datetime(2020, 8, 4),
                                       todate=datetime.datetime(2020, 11, 13))
            bs._k_data.to_csv("sample.csv")
            cerebro = self.cerebros[stock_code]
            cerebro.adddata(data)
            cerebro.addstrategy(KDJStrategy)
            cerebro.broker.setcash(100000.0)
            cerebro.broker.setcommission(0.0017)

    def run(self):
        for stock_code, cerebro in self.cerebros.items():
            print("start run %s......" % stock_code)
            cerebro.run()

            print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

            return_all = cerebro.broker.getvalue() / 100000.0
            print('Total ROI: {0}%, Annual ROI{1}%'.format(
                round((return_all - 1.0) * 100, 2),
                round((pow(return_all, 1.0 / 10) - 1.0) * 100, 2)
            ))
            cerebro.plot(style='bar')

            print("end run %s......" % stock_code)



stock_path = "../resource/target_stock.dat"
account_dir = "../resource/user_account"
start_date = "2020-08-03"
end_date = "2020-11-13"
mode = "backtest" # backtest or dailyrun

# 初始化股票信息
DR = DailyRun(stock_path, account_dir, start_date, end_date)

DR.run()

# # 计算某一天的交易建议
# DR.trade_reference_answer()
#
# # 立即执行交易建议
# DR.backtest_do_trade()
# # 计算账户最新状态
# DR.update_user_account()
# # 根据T日收盘价计算近似收益(假设随时能够买卖)
# DR.cal_gain()
# # 保存当天交易状态。等待下次启动。
# DR.close()
#
