import backtrader as bt
import pandas as pd
from util.Constant import *
import numpy as np

class KDJStrategy(bt.Strategy):

    lines = ('K', 'D', 'J')

    params = (
        ('period', 9),
        ('period_dfast', 3),
        ('period_dslow', 3),
        ('save_feature_path', None),
        ('code', "000001.sh")
    )

    plotlines = dict(
        J=dict(
            _fill_gt=('K', ('red', 0.50)),
            _fill_lt=('K', ('green', 0.50)),
        )
    )
    def log(self, txt, dt=None):
        """ Logging function fot this strategy"""
        dt = dt or self.datas[0].datetime.date(0)
        print("%s, %s" % (dt.isoformat(), txt))

    @staticmethod
    def percent(today, yesterday):
        return float(today - yesterday) / today

    def __init__(self):

        self.dataclose = self.datas[0].close
        self.volume = self.datas[0].volume

        self.order = None
        self.buyprice = None
        self.buycomm = None

        # 9个交易日内最高价
        self.high_nine = bt.indicators.Highest(self.data.high, period=9)
        # 9个交易日内最低价
        self.low_nine = bt.indicators.Lowest(self.data.low, period=9)
        # 计算rsv值
        self.rsv = 100 * bt.DivByZero(
            self.data_close - self.low_nine, self.high_nine - self.low_nine, zero=None
        )
        # self.K=50
        # self.D=50
        # 计算rsv的3周期加权平均值，即K值
        self.K = bt.indicators.EMA(self.rsv, period=3, plot=False)#2/3*self.K + 1/3*self.rsv
        # D值=K值的3周期加权平均值
        self.D = bt.indicators.EMA(self.K, period=3, plot=False)#2/3*self.D + 1/3*self.K
        # J=3*K-2*D
        self.J = 3 * self.K - 2 * self.D

        self.save_feature_path = self.params.save_feature_path
        self.save_content = []

    def save_feature(self, feature):
        if self.params.save_feature_path is not None:
            self.save_content.append(feature)


    def notify_order(self, order):
        print("order")
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    "BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f"
                    % (order.executed.price, order.executed.value, order.executed.comm)
                )

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
                self.bar_executed_close = self.dataclose[0]
            else:
                self.log(
                    "SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f"
                    % (order.executed.price, order.executed.value, order.executed.comm)
                )
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("Order Canceled/Margin/Rejected")

        self.order = None

    def notify_trade(self, trade):
        print("trade")
        if not trade.isclosed:
            return

        self.log("OPERATION PROFIT, GROSS %.2f, NET %.2f" % (trade.pnl, trade.pnlcomm))

    def next(self):

        self.log("Close, %.2f" % self.dataclose[0])

        if self.order:
            return

        condition1 = self.J[-1] - self.D[-1]
        condition2 = self.J[0] - self.D[0]

        self.save_feature([self.datas[0].datetime.date(0),
                           self.params.code,
                           self.K[0], self.D[0], self.J[0],
                           self.K[0] - self.J[0], self.K[0] - self.D[0], self.D[0] - self.J[0]])

        # 用sklearn默认自带的forward就可以，这里只是示例手动搬运
        condition = self.K[0] * 0.00180087 \
                    + self.D[0] * 0.00369708 \
                    - self.J[0] * 0.00199154 \
                    + (self.K[0] - self.J[0]) * 0.00379241 \
                    - (self.K[0] - self.D[0]) * 0.00189621 \
                    + (self.D[0] - self.J[0]) * 0.00568862\
                    -0.22552621
        print(condition)

        condition = 1 / (1 + np.exp(-condition))
        print(condition)

        if not self.position:
            # if condition1 < 0 and condition2 > 0:
            if condition > 0.5:
                self.order = self.buy()

        else:
            # if condition1 < 0 and condition2 > 0:
            if condition <= 0.5:
                self.log("K, %.2f" % self.K[0])
                self.log("J, %.2f" % self.J[0])
                self.log("D, %.2f" % self.D[0])
                self.log("SELL CREATE, %.2f" % self.dataclose[0])
                self.order = self.sell()

    def stop(self):
        if self.params.save_feature_path is not None:
            result = pd.DataFrame(data=self.save_content, columns=["date", "code", "K", "D", "J", KD, KJ, DJ])
            result.to_csv(self.save_feature_path, index=False)


