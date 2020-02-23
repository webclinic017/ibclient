# coding=utf-8

'''
Define common used variables and functions
Created on 10/18/2016
@author: Jin Xu
@contact: jin_xu1@qq.com
'''
from __future__ import absolute_import, print_function, division
from threading import Event

# Tick Data Fields
TICK_FIELDS = {}
TICK_FIELDS[0] = 'bidVolume1'
TICK_FIELDS[1] = 'bidPrice1'
TICK_FIELDS[2] = 'askPrice1'
TICK_FIELDS[3] = 'askVolume1'
TICK_FIELDS[4] = 'lastPrice'
TICK_FIELDS[5] = 'lastVolume'
TICK_FIELDS[6] = 'highPrice'
TICK_FIELDS[7] = 'lowPrice'
TICK_FIELDS[8] = 'volume'
TICK_FIELDS[9] = 'preClosePrice'
TICK_FIELDS[14] = 'openPrice'
TICK_FIELDS[22] = 'openInterest'
TICK_FIELDS[45] = 'lastTradeTS'

# Define TICK_TYPE according to
# https://interactivebrokers.github.io/tws-api/tick_types.html
TICK_TYPE_001          = 1
TICK_TYPE_TIMESTAMP    = 45
TICK_TYPE_FIN_RATIOS   = 47
TICK_TYPE_DIVIDENDS    = 59
TICK_TYPE_NEWS         = 62

TICK_STRING_TYPES = [TICK_TYPE_TIMESTAMP, TICK_TYPE_FIN_RATIOS, TICK_TYPE_DIVIDENDS, TICK_TYPE_NEWS]

class OrderStyle(object):
    ''' Define IB order type.
    '''
    def __init__(self, order_type='MKT', limit_price=None, stop_price=None):
        self.order_type = order_type
        self.limit_price = limit_price
        self.stop_price = stop_price
        self.is_combo_order = False
        self.non_guaranteed = None

class MarketOrder(OrderStyle):
    ''' Define Market Order type.
    '''
    def __init__(self):
        self.order_type = 'MKT'
        self.limit_price = None
        self.stop_price = None
        self.is_combo_order = False
        self.non_guaranteed = None

class LimitOrder(OrderStyle):
    ''' Define Limit order type.
    '''
    def __init__(self, limit_price):
        self.order_type = 'LMT'
        self.limit_price = limit_price
        self.stop_price = None
        self.is_combo_order = False
        self.non_guaranteed = None

class StopOrder(OrderStyle):
    ''' Define Stop order type.
    '''
    def __init__(self, stop_price):
        self.order_type = 'STP'
        self.limit_price = None
        self.stop_price = stop_price
        self.is_combo_order = False
        self.non_guaranteed = None

class StopLimitOrder(OrderStyle):
    ''' Define Stop Limit order type.
    '''
    def __init__(self, limit_price, stop_price):
        self.order_type = 'STP LMT'
        self.limit_price = limit_price
        self.stop_price = stop_price
        self.is_combo_order = False
        self.non_guaranteed = None

class ComboMarketOrder(OrderStyle):
    ''' Define IB Combo Market Order type.
    '''
    def __init__(self):
        self.order_type = 'MKT'
        self.limit_price = None
        self.stop_price = None
        self.is_combo_order = True
        self.non_guaranteed = True

class ComboLimitOrder(OrderStyle):
    ''' Define IB Combo Limit Order type.
    '''
    def __init__(self, limit_price):
        self.order_type = 'LMT'
        self.limit_price = limit_price
        self.stop_price = None
        self.is_combo_order = True
        self.non_guaranteed = True

class RequestDetails():
    def __init__(self, req_name, req_type=None, contract=None):
        self.func_name = req_name
        self.req_type = req_type
        self.contract = contract

class ResponseDetails():
    # Status Defition for this Response
    STATUS_FINISHED = 0

    def __init__(self):
        self.price_hist = []    # for historical price responses
        self.rt_price = []      # for real-time bar responses
        self.status = -1        # error_code in IBMsgWrapper
        self.request_id = -1
        self.error_msg = ''
        self.event = Event()
        self.fundamental_data = ''
        self.contract_list = []
        self.tick_str = None
        # tick_data stores either live tick data or a tick snapshot
        self.tick_data = {'bidVolume1'  :  -1,  'bidPrice1'    :  -1,
                          'askPrice1'    :  -1, 'askVolume1'   :  -1,
                          'lastPrice'    :  -1, 'lastVolume'   :  -1,
                          'highPrice'    :  -1, 'lowPrice'     :  -1,
                          'volume'       :  -1, 'preClosePrice':  -1,
                          'openPrice'   :  -1,  'openInterest':  -1,
                          'lastTradeTS': -1}


class IBEXCHANGE(object):
    ''' Define exchange in IB system.
    Please refer to https://www.ibkr.com.cn/cn/index.php?f=5429 for details.
    For timezone strings, please refers to pytz.all_timezones
    A few commonly used timezone strings:
        'Asia/Bangkok',  'Asia/Dubai','Asia/Hong_Kong',  'Asia/Shanghai', 'Asia/Singapore',
        'US/Alaska',  'US/Central', 'US/Eastern', 'US/Mountain', 'US/Pacific', 'UTC',
    '''

    SMART = 'SMART'
    GLOBEX = 'GLOBEX'
    IDEALPRO = 'IDEALPRO'

    # North America
    NYMEX = 'NYMEX'
    NASDAQ = 'ISLAND'
    CFE = 'CFE'
    CBOE = 'CBOE'

    # Asia
    SGX = 'SGX'         # Singapore Exchange (SGX)
    SEHK = 'SEHK'       # Hong Kong Stock Exchange (SEHK)
    SEHKNTL = 'SEHKNTL' # 沪港通

    TIMEZONE = {}
    TIMEZONE['SGX'] = 'Asia/Shanghai'
    TIMEZONE['SEHK'] = 'Asia/Shanghai'
    TIMEZONE['SEHKNTL'] = 'Asia/Shanghai'
    TIMEZONE['NYMEX'] = 'US/Eastern'
    TIMEZONE['ISLAND'] = 'US/Eastern'
    TIMEZONE['NYMEX'] = 'US/Eastern'
    TIMEZONE['CFE'] = 'US/Central'
    TIMEZONE['CBOE'] = 'US/Central'
    TIMEZONE['SMART'] = 'US/Eastern'

    @staticmethod
    def get_timezone(exchange):
        return IBEXCHANGE.TIMEZONE.get(exchange, 'US/Eastern')

