# -*-coding:utf-8-*-
import pandas as pd
import time
import os
import pickle
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn import metrics

from model.build_feature import BuildFeature
from model.build_label import BuildLabel
from model.build_sample import BuildSample
from util.Func import *
from stock.base_stock_info import BaseStockInfo
from stock.stock_info_source import StockInfoSource


# ----------------全局配置开始---------------------
# 目标股票代号集合
target_stock_info_path = "../resource/target_stock.dat"
feature_conf = "../resource/model_data/feature_conf/fc.data_v1"
# 构建数据最大起止时间点
start_date = "2010-01-01"
# 默认最终时间为bizdate，即当前时间的前一天，现在为当天
end_date = time.strftime("%Y-%m-%d", time.localtime())

freq = 'd'
strategy_name = "KDJ"

# ----------------默认配置-------------------------
target_stock_info_save_path = "../resource/stock_info/"
target_stock_label_save_path = "../resource/model_data/label/label.dat"
target_stock_feature_save_dir = "../resource/model_data/feature"
target_stock_sample_path = "../resource/model_data/sample/sample_v1"
target_stock_model_save_path = "../resource/model_data/model/demo_model"
# ----------------全局配置结束----------------------

# ----------------构建label开始---------------------

# 读取股票原始数据
target_stock_lists = get_target_stock(target_stock_info_path)
target_stock_info_lists = []
sis = StockInfoSource()
for target_stock, marks in target_stock_lists:
    stock_info = BaseStockInfo(stock_code=target_stock, start_date=start_date, end_date=end_date, freq=freq)
    sis.load_his_k_data(stock_info)
    path = os.path.join(target_stock_info_save_path, target_stock)
    stock_info.save_cvs(path, True)
    target_stock_info_lists.append(stock_info)

# 构建label
bl = BuildLabel(target_stock_info_save_path, target_stock_label_save_path)
# 用lr的时候负例结果是-1
bl.build_label(default_neg=-1)
bl.save_label()

# ----------------构建label结束---------------------

# ----------------构建feature开始-------------------
bf = BuildFeature()
for stock_info in target_stock_info_lists:
    bf.getFeature(target_stock_feature_save_dir, start_date, end_date, strategy_name, stock_info)

# ----------------构建feature结束-------------------

# ----------------构建样本开始-----------------------

bl = BuildSample(target_stock_label_save_path, target_stock_feature_save_dir, target_stock_sample_path, feature_conf)
bl.build_sample()
bl.save_sample()

# ----------------构建样本结束-----------------------

# ----------------读入数据开始-----------------------

# 读入feature
feature_name_list = []
with open(feature_conf, "r") as finput:
    for line in finput:
        if "#" not in line and len(line.strip()) > 0:
            content = line.strip().split(",")
            feature_name_list.append(content[2])
print("feature_name_list is", feature_name_list)

data = pd.read_csv(target_stock_sample_path).dropna(how='any')

train = data[:int(len(data) * 0.9)]
test = data[int(len(data) * 0.9):]
X_train = train[feature_name_list]
Y_train = train['label']

X_test = test[feature_name_list]
Y_test = test['label']

print(X_train.value_counts())
print(X_test.value_counts())

# ----------------读入数据结束-----------------------

# ----------------训练开始--------------------------

lr = LogisticRegression(C=1.0, penalty='l2', tol=0.0001)
lr.fit(X_train, Y_train)


print(lr.coef_)
print(lr.intercept_)
print(lr.n_iter_)

# ----------------训练结束--------------------------

# ----------------模型指标评估开始-----------------------

lr_y_predict = lr.predict(X_test)
lr_y_predict_prob = lr.predict_proba(X_test)
print(lr_y_predict, lr_y_predict_prob)

lr_y_score = lr.score(X_test, Y_test)
print(lr.score(X_test, Y_test))
print(type(Y_test), type(lr_y_predict_prob), lr_y_predict_prob.shape, type(lr_y_predict_prob[:, 1]), lr_y_predict_prob[:, 1].shape)
print(metrics.roc_auc_score(Y_test, lr_y_predict_prob[:, 1]))

# ----------------模型指标评估结束-----------------------

# ----------------导出模型开始-----------------------

with open(target_stock_model_save_path, "wb") as foutpput:
    lr_model = pickle.dump(lr, foutpput)

# ----------------导出模型结束-----------------------

with open(target_stock_model_save_path, "rb") as finput:
    lr_model = pickle.load(finput)