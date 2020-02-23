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
        self.stock_symbol = 'IBM'

    def set_conn(self):
        client_id = random.randint(0, 10000)
        con = IBClient(port=7497, client_id=client_id)
        con.connect()
        return con

    def test001_ownership_report(self):
        print('test_ownership_report...')
        self.set_data()
        con = self.set_conn()
        max_wait_time = 60.
        status, data = con.get_company_ownership(self.stock_symbol, max_wait_time)
        time.sleep(max_wait_time+3)
        print(status)
        print(data)
        con.close()

    def test002_finsmt_report(self):
        print('test_finsmt_report...')
        self.set_data()
        con = self.set_conn()
        max_wait_time = 20.
        status, data = con.get_financial_statements(self.stock_symbol)
        time.sleep(max_wait_time+3)
        print(status)
        print(data)
        con.close()

    def test003_analyst_report(self):
        print('test_analyst_report...')
        self.set_data()
        con = self.set_conn()
        max_wait_time = 30.
        status, data = con.get_analyst_estimates(self.stock_symbol)
        time.sleep(max_wait_time+3)
        print(status)
        print(data)
        con.close()

    def test004_financial_summary(self):
        print('test_financial_summary...')
        self.set_data()
        con = self.set_conn()
        max_wait_time = 30.
        status, data = con.get_financial_summary(self.stock_symbol)
        time.sleep(max_wait_time+3)
        print(status)
        print(data)
        con.close()

    def test005_company_overview(self):
        print('test_company_overview...')
        self.set_data()
        con = self.set_conn()
        max_wait_time = 30.
        status, data = con.get_company_overview(self.stock_symbol)
        time.sleep(max_wait_time+3)
        print(status)
        print(data)
        con.close()

if __name__ == "__main__":
    unittest.main()
