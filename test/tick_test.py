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
        self.stock = new_stock_contract('IBM')
        self.stock_str = 'APOL'
        self.future = new_futures_contract('VIX', 'CFE', False, expiry='201612', tradingClass='VX')
        self.end = datetime.datetime(2016, 10, 20).strftime('%Y%m%d %H:%M:%S')

    def set_conn(self):
        client_id = random.randint(0, 10000)
        con = IBClient(port=7497, client_id=client_id)
        con.connect()
        return con

    def test001_get_tick_snapshot(self):
        print('test_get_tick_snapshot...')
        self.set_data()
        con = self.set_conn()
        for i in range(20):
            try:
                tick_data = con.get_tick_snapshot(self.stock)
                time.sleep(10)
            except RuntimeError:
                con.close()
            else:
                print(tick_data)
        con.close()
        time.sleep(0.5)

    def test002_get_tick(self):
        print('def test_get_tick...')
        self.set_data()      
        con = self.set_conn()
        try:
            id2, tick_data = con.request_tick_data(self.stock)
            time.sleep(2)
        except RuntimeError:
            print('test_get_tick:RuntimeError')
            con.close()
        else:
            print(con.ipc_msg_dict[id2][1].tick_snapshot)
            time.sleep(5)
            print(con.ipc_msg_dict[id2][1].tick_snapshot)
            time.sleep(5)
            print(con.ipc_msg_dict[id2][1].tick_snapshot)
            time.sleep(5)
            con.cancel_tick_request(id2)
        con.close()
        time.sleep(0.5)

if __name__ == "__main__":
    unittest.main()
