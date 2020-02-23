# -*- coding:utf-8 -*-
'''
Created on 11/08/2016
@author: Jin Xu
'''
import unittest
import datetime
import time
from ibclient import *
import random

class Test(unittest.TestCase):

    def set_data(self):
        self.stock = new_stock_contract('MSFT')
        self.future = new_futures_contract('VIX', 'CFE', False, expiry='201612', tradingClass='VX')

    def set_conn(self):
        client_id = random.randint(0, 10000)
        con = IBClient(port=7497, client_id=client_id)
        con.connect()
        return con

    def test_buy_stocks(self):
        self.set_data()
        con = self.set_conn()
        id1 = con.order_amount(self.stock, 1000, style=MarketOrder())
        time.sleep(0.5)
        id2 = con.order_amount(new_stock_contract('APOL'), 1000, style=LimitOrder(8.6))
        con.close()
        time.sleep(0.5)

    def test_sell_stocks(self):
        self.set_data()
        con = self.set_conn()
        id1 = con.order_amount(self.stock, -500, style=MarketOrder())
        time.sleep(0.5)
        id2 = con.order_amount(new_stock_contract('APOL'), -500, style=LimitOrder(8.2))
        con.close()
        time.sleep(0.5)

    def test_trade_futures(self):
        self.set_data()
        con = self.set_conn()
        id1 = con.order_amount(self.future, 1, style=MarketOrder())
        time.sleep(0.5)
        id2 = con.order_amount(self.future, -1, style=LimitOrder(10000))
        con.close()
        time.sleep(0.5)

    def test_trade_combo(self):
        self.set_data()
        con = self.set_conn()
        time.sleep(0.5)
        con.close()
        time.sleep(0.5)

if __name__ == "__main__":
    unittest.main()
