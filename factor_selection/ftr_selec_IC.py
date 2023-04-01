import numpy as np
import pandas as pd
import rqdatac as rq
from rqdatac import *
from rqdatac import finance
from rqdatac import get_price
from rqdatac import order_book_id
from rqdatac import trading_date

rq.init()

# 获取股票池
universe = get_index_stocks('000300.XSHG', date='2022-03-31')
universe = sorted(universe, key=lambda x: finance.run_query(query(finance.SW1_DAILY_PRICE).filter(finance.SW1_DAILY_PRICE.code == x, finance.SW1_DAILY_PRICE.date == '2022-03-31').first().sw1_code))

# 选取市值排名前100的股票
market_cap = finance.run_query(
    query(finance.STK_CAPITALIZATION).filter(
        finance.STK_CAPITALIZATION.code.in_(universe),
        finance.STK_CAPITALIZATION.date == '2022-03-31'
    )
).set_index('code')
market_cap = market_cap.loc[market_cap['rank'] <= 100]

# 获取因子数据
pe_ratio = get_factor('pe_ratio', market_cap.index, '2022-03-31', '2022-03-31').T
pb_ratio = get_factor('pb_ratio', market_cap.index, '2022-03-31', '2022-03-31').T
roe = get_factor('roe', market_cap.index, '2022-03-31', '2022-03-31').T
eps = get_factor('eps', market_cap.index, '2022-03-31', '2022-03-31').T
peg_ratio = pe_ratio / eps

# 计算每个因子的IC值
def calc_ic(factor_data, close_data, n):
    factor_returns = factor_data.pct_change()
    asset_returns = close_data.pct_change()
    ic = factor_returns.corrwith(asset_returns, axis=1)
    ic = ic.dropna()
    ic = ic.sort_values(ascending=False)[:n]
    return ic

# 使用IC法筛选因子
def select_factors(factor_data, close_data, n):
    ic_list = []
    for factor_name in factor_data.columns:
        ic = calc_ic(factor_data[factor_name], close_data, 1)
        if not ic.empty:
            ic_list.append(ic.iloc[0])
    if not ic_list:
        return None
    ic_mean = pd.Series(ic_list).mean()
    ic_mean = ic_mean.sort_values(ascending=False)[:n]
    selected_factors = factor_data[ic_mean.index]
    return selected_factors

# 筛选出最有用的5个因子
close_data = get_price(market_cap.index, start_date='2022-03-31', end_date='2022-03-31', fields='close', frequency='1d').close
factor_data = get_factor(universe, '2022-03-31', '2022-03-31')
selected_factors = select_factors(factor_data, close_data, 5)

# 构建因子加权模型
weights = selected_factors.rank(pct=True).mean(axis=1)
weights /= weights.abs().sum()
weights = weights.dropna()

# 进行多因子选股
factor_data = factor_data.loc[weights.index]
factor_data = factor_data.loc[:, selected_factors.columns]

factor_data = factor_data / factor_data.std()

scores = factor_data.dot(weights)

# 排序选股结果
selected_stocks = scores.sort_values(ascending=False).index[:10]
