from rqalpha_plus.apis import *
from rqdatac import *


# 在这个方法中编写任何的初始化逻辑。context对象将会在你的算法策略的任何方法之间做传递。
def init(context):
    context.s1 = "000001.XSHE"
    update_universe(context.s1)
    # 是否已发送了order
    context.fired = False
    logger.info("RunInfo: {}".format(context.run_info))


def before_trading(context):
    print("before")
    pass


# 你选择的证券的数据更新将会触发此段逻辑，例如日或分钟历史数据切片或者是实时数据切片更新
def handle_bar(context, bar_dict):
    # 开始编写你的主要的算法逻辑
    start_date = '20221201'
    end_date = '20221231'
    universe = '000001.XSHE'

    # 获取股票历史价格数据
    price_arr = history_bars(universe, 30, '1d', ['close'])
    price_arr = price_arr['close']
    price_df = pd.DataFrame(price_arr, columns=['close'])

    factor_list = get_all_factor_names()
    factor_dict = get_factor(universe, factor=factor_list[:10], start_date=start_date, end_date=end_date)
    print(factor_dict)

    # bar_dict[order_book_id] 可以拿到某个证券的bar信息
    # context.portfolio 可以拿到现在的投资组合状态信息

    # 使用order_shares(id_or_ins, amount)方法进行落单

    # TODO: 开始编写你的算法吧！
    if not context.fired:
        # order_percent并且传入1代表买入该股票并且使其占有投资组合的100%
        logger.info("order_percent:{}".format(order_percent(context.s1, 1)))
        context.fired = True


def after_trading(context):
    pass
