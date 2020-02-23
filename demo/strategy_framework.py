# encoding: UTF-8

'''
This is a Strategy Framework using 'ibclient' package.
'''

import sched, time
from time import sleep, ctime
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from ibclient import *

# Strategy configurations
PRICE_UNIT = 2.5  # Constant
SID = int(252003475)  # The contract/security ID in the IB system
TARGET_AMOUNT = 10
N_MIN = 15  # 10          # N min after market open (9:30)


def initialize(context):
    # Define security
    context.current_contract = new_futures_contract('XINA50', 'SGX', False, '201701', 'CN', 'USD')
    context.security_list = [context.current_contract]

    # Define data bank
    context.tick_price = {}
    context.order_list = []
    for sec in context.security_list:
        context.tick_price[sec] = []

    # for order and position management
    context.long_positions = 0  # used for Long algo only
    context.short_positions = 0  # used for Short algo only

    # for hist and real-time market data (price/vol)
    context.current_data = None
    context.curr_rtprice = None

    # Setup time related variables
    now = datetime.now()
    context.year = now.year
    context.month = now.month
    context.day = now.day

    # define market open/close time
    context.pre_open = datetime(now.year, now.month, now.day, 9, 25)
    context.mkt_open = datetime(now.year, now.month, now.day, 9, 30)
    context.pre_close = datetime(now.year, now.month, now.day, 14, 55)
    context.mkt_close = datetime(now.year, now.month, now.day, 15, 00)

    # add any new variables to context here
    # e.g.
    # context.your_variable = 123


def before_trading_start(context, data):
    ''' this function will be schedule to run before market open (time specified by context.pre_open)

    :param context:
    :param data:
    :return:
    '''
    print('[', ctime(), ']', 'before_trading_start')

    try:
        # Get hist price (5 sec bar)
        end_str = datetime(context.year, context.month, context.day, 8, 0).strftime('%Y%m%d %H:%M:%S')
        context.price_hist = context.con.get_price_history(context.current_contract, end_str, '5 D', 'minute')
        sleep(0.5)
        price_daily = context.con.get_price_history(context.current_contract, end_str, '15 D', 'daily')
        sleep(0.5)
    except RuntimeError:
        return False

    # drop 0 volume; select 9am-3pm data points
    context.price_hist = context.price_hist[context.price_hist['Volume'] > 0]
    context.price_hist = context.price_hist.between_time('9:00', '11:30').append(
        context.price_hist.between_time('13:00', '15:00'))
    context.price_hist = context.price_hist.sort_index()

    try:
        # req real-time price and link variable to connection's ipc_msg_dict
        context.id_curr_rtprice = context.con.request_realtime_price(context.current_contract)
    except RuntimeError:
        return False
    # data_header = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    context.curr_rtprice = context.con.ipc_msg_dict[context.id_curr_rtprice][1].rt_price


def after_market_open(context, data):
    ''' Called after market open.

    :param context:
    :param data:
    :return:
    '''
    sleep(30)
    print('-' * 60)
    print('[', ctime(), ']', 'after_market_open')
    con = context.con

    # get min price data
    n_seconds = 60 * 60 * 3
    end_str = datetime(context.year, context.month, context.day, 9, (N_MIN + 30)).strftime('%Y%m%d %H:%M:%S')
    context.price_open_df = con.get_price_history(context.current_contract, end_str,
                                                  str(n_seconds) + ' S', 'minute')
    print(context.price_open_df)


def trading_algo(context, data):
    ''' Core trading algo called every N seconds

    :param context:
    :param data:
    :return:
    '''

    sleep(60)
    print('-' * 60)
    print('[', ctime(), ']', 'trading_algo')

    con = context.con
    mkt_close = context.mkt_close

    t_noon_1130 = datetime(context.year, context.month, context.day, 11, 30)
    t_noon_1300 = datetime(context.year, context.month, context.day, 13, 00)

    #
    # During Trading Hours
    #
    while datetime.now() < mkt_close:
        now = datetime.now()

        # Wait between the noon break
        if now > t_noon_1130 and now < t_noon_1300:
            print('[', ctime(), ']', 'Wait between 11:30 - 13:00')
            wait_t = t_noon_1300 - now
            sleep(wait_t.total_seconds())
            continue

        # When TWS connection is loss, wait until recovery
        if not context.con.connected:
            sleep(60)
            continue

        # TODO: Implement your trading algo here

        # wait for 30 sec before next round
        sleep(30)


def before_market_close(context, data):
    ''' Close all open positions; Cancel all open orders

    :param context:
    :param data:
    :return:
    '''
    print('-' * 60)
    print('[', ctime(), ']', 'before_market_close')
    con = context.con

    # get open orders and cancel them
    con.get_open_orders()
    sleep(2)
    for key in con.order_dict:
        if 'order' in con.order_dict[key]:
            order = con.order_dict[key]['order']
            if order.m_clientId == con.client_id:
                con.cancel_order(order.m_orderId)

    # get existing positions and close them
    if SID in context.portfolio.positions:
        target_amount = 0
        current_amt = context.portfolio.positions[SID].amount

        id = con.order_amount(context.current_contract, (target_amount - current_amt), style=MarketOrder())
        sleep(0.5)
        context.order_list.append(id)
        context.long_positions = target_amount


def after_market_close(context, data):
    '''

    :param context:
    :param data:
    :return:
    '''
    print('-' * 60)
    print('[', ctime(), ']', 'after_market_close')

    # TODO: implement what need to do after market close
    pass


def main_func(client_id=508):
    ''' the main function. Init IB client connections, global variables (context and data),
        and schedule trading functions to run in specific times.

    '''
    print('starting at:', ctime())

    # init context and data
    IB_ACCOUNT = 'DU264039'
    starting_cash = 20000
    context = Context(account_id=IB_ACCOUNT, starting_cash=starting_cash)
    data = Data()

    # init IB client
    context.client_name = 'IB client#1'
    context.client_id = client_id
    port = 7497
    context.con = IBClient(client_id=context.client_id, port=port, client_name=context.client_name)
    context.con.register_strategy(context, data)
    ret = context.con.connect()
    if ret is False:
        return ret

    # init variables inside context obj
    initialize(context)

    print('-' * 60)

    # schedule tasks
    task_sched = sched.scheduler(time.time, time.sleep)
    pre_open_ts = time.mktime(context.pre_open.timetuple())
    mkt_open_ts = time.mktime(context.mkt_open.timetuple())
    pre_close_ts = time.mktime(context.pre_close.timetuple())
    mkt_close_ts = time.mktime(context.mkt_close.timetuple())

    task_sched.enterabs(pre_open_ts, 1, before_trading_start, (context, data))
    task_sched.enterabs(mkt_open_ts + (N_MIN - 2) * 60, 1, after_market_open, (context, data))
    task_sched.enterabs(mkt_open_ts + N_MIN * 60, 1, trading_algo, (context, data))
    task_sched.enterabs(pre_close_ts, 1, before_market_close, (context, data))
    task_sched.enterabs(mkt_close_ts, 1, after_market_close, (context, data))
    task_sched.run()

    # clean up
    print('[', ctime(), ']', 'closing TWS connection')
    context.con.close()
    return


if __name__ == '__main__':
    main_func()
