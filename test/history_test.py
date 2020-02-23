# -*- coding:utf-8 -*-
'''
Created on 11/08/2016
@author: Jin Xu
'''
import unittest
import datetime
import time
import random
from ibclient import *

class Test(unittest.TestCase):

    def set_data(self):
        self.stock = new_stock_contract('IBM')
        self.stock_str = 'APOL'
        self.future = new_futures_contract('VIX', 'CFE', False, expiry='201612', tradingClass='VX')
        self.end = datetime.datetime(2016, 10, 20).strftime('%Y%m%d %H:%M:%S')

    def set_conn(self):
        client_id = random.randint(0, 10000)
        con = IBClient(port=7497, client_id=client_id)
        con.connect()
        return con

    def test_get_hist_data(self):
        self.set_data()
        con = self.set_conn()
        print(con.get_price_history(self.stock, self.end, '3 D', 'daily'))
        print(con.get_price_history(self.stock_str, self.end, '10 D', 'minute'))
        print(con.get_price_history(self.future, self.end, '3 D', 'daily'))
        con.close()
        time.sleep(0.5)

    def test_get_hist_data_long(self):
        self.set_data()
        con = self.set_conn()
        print(con.get_price_history(self.stock, self.end, '3 M', 'daily'))
        print(con.get_price_history(self.stock_str, self.end, '1 Y', 'daily'))
        con.close()
        time.sleep(0.5)

    def test_get_realtime_price(self):
        self.set_data()
        con = self.set_conn()
        id1, rt_p = con.request_realtime_price(self.stock)
        time.sleep(5)
        print(con.ipc_msg_dict[id1][1].rt_price)
        time.sleep(0.1)
        con.cancel_realtime_price(id1)
        con.close()
        time.sleep(0.5)

if __name__ == "__main__":
    unittest.main()
