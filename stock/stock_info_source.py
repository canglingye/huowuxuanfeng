# -*- coding:utf-8 -*-
import baostock as bs
import sys
import pandas as pd

from stock.base_stock_info import BaseStockInfo

index_pro = "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ,psTTM,\
             pcfNcfTTM,isST"
index_mini = "date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg"


def show_error(func_name, res):
    if res.error_code != '0':
        print('%s respond error_code: %s' % (func_name, res.error_code))
        print('%s respond  error_msg: %s' % (func_name, res.error_msg))


class StockInfoSource(object):

    def __init__(self, freq="d"):
        self._freq = freq
        self.login()

    def login(self):
        res = bs.login(user_id="anonymous", password="123456")
        show_error(sys._getframe().f_code.co_name, res)

    def load_his_k_data(self, base_stock_info):
        # 获取历史K线数据
        data_list = []
        res = bs.query_history_k_data(base_stock_info._stock_code, index_pro if self._freq == 'd' else index_mini,
                                      start_date=base_stock_info._start_date, end_date=base_stock_info._end_date,
                                      frequency=self._freq, adjustflag="3")  # frequency="d"取日k线，adjustflag="3"默认不复权

        show_error(sys._getframe().f_code.co_name, res)

        while (res.error_code == '0') & res.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(res.get_row_data())

        df_data = pd.DataFrame(data_list, columns=res.fields)
        df_data.set_index(["date"], inplace=True)
        df_data.index = pd.to_datetime(df_data.index)
        df_data[['low', 'high', 'open', 'close', 'volume']] = df_data[['low', 'high', 'open', 'close', 'volume']].astype(float)

        base_stock_info._k_data = df_data
        base_stock_info._k_data_plus = df_data


if __name__ == "__main__":
    bs3 = BaseStockInfo(stock_code='601006.sh', start_date='2010-01-01', end_date='2020-11-20', freq='d')
    sis = StockInfoSource()
    sis.load_his_k_data(bs3)

    path = "../resource/stock_info/%s.dat" % (bs3._stock_code)
    bs3.save_cvs(path, True)
    bs3.load_csv(path)
    print(bs3)
