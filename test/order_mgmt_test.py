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
        self.stock = new_stock_contract('MSFT')
        self.future = new_futures_contract('VIX', 'CFE', False, expiry='201612', tradingClass='VX')

    def set_conn(self):
        client_id = random.randint(0, 10000)
        acct_id = 'DU264039'
        context = Context(acct_id, starting_cash=120000)
        data = Data()
        con = IBClient(port=7497, client_id=client_id)
        con.connect()
        return con

    def test_get_open_orders(self):
        print('%s test_get_open_orders %s' % ('-'*30, '-'*30))
        self.set_data()
        con = self.set_conn()
        # order MSFT at $10 - this will create a pending order
        id1 = con.order_amount(self.stock, 100, style=LimitOrder(10.))
        time.sleep(0.2)
        id2 = con.order_amount(self.future, -1, style=LimitOrder(10.))
        time.sleep(1)
        id3 = con.order_amount(self.future, -1, style=MarketOrder())
        time.sleep(1)

        con.get_open_orders()
        time.sleep(5)
        for key in con.order_dict:
            print('%s' % '-'*60)
            if 'order' in con.order_dict[key]:
                order = con.order_dict[key]['order']
                print('m_orderId       = %d' % order.m_orderId)
                print('m_clientId      = %d' % order.m_clientId)
                print('m_permId        = %d' % order.m_permId)
                print('m_action        = %s' % order.m_action)
                print('m_totalQuantity = %d' % order.m_totalQuantity)
                print('m_orderType     = %s' % order.m_orderType)
            if 'contract' in con.order_dict[key]:
                contract = con.order_dict[key]['contract']
                print('contract        = %d' % contract.m_conId)

            print('status', ' ', con.order_dict[key]['status'])
            print('filled', ' ', con.order_dict[key]['filled'])
            print('permId', ' ', con.order_dict[key]['permId'])
            print('remaining', ' ', con.order_dict[key]['remaining'])
            print('avgFillPrice', ' ', con.order_dict[key]['avgFillPrice'])
            print('lastFillPrice', ' ', con.order_dict[key]['lastFillPrice'])
            print('whyHeld', ' ', con.order_dict[key]['whyHeld'])

        con.close()
        time.sleep(0.5)

    def test_cancel_orders(self):
        print('%s test_cancel_orders %s' % ('-'*30, '-'*30))
        self.set_data()
        con = self.set_conn()

        # order MSFT at $10 - this will create a pending order
        id1 = con.order_amount(self.stock, 100, style=LimitOrder(10.))
        time.sleep(0.5)
        id2 = con.order_amount(self.future, -1, style=LimitOrder(10.))
        time.sleep(0.5)
        id3 = con.order_amount(self.stock, -100, style=LimitOrder(80.))
        time.sleep(0.5)

        con.get_open_orders()
        time.sleep(5)
        for key in con.order_dict:
            print('%s' % '-'*60)
            if 'order' in con.order_dict[key]:
                order = con.order_dict[key]['order']
                print('m_orderId       = %d' % order.m_orderId)
                print('m_clientId      = %d' % order.m_clientId)
                print('m_permId        = %d' % order.m_permId)
                print('m_action        = %s' % order.m_action)
                print('m_totalQuantity = %d' % order.m_totalQuantity)
                print('m_orderType     = %s' % order.m_orderType)
            if 'contract' in con.order_dict[key]:
                contract = con.order_dict[key]['contract']
                print('contract        = %d' % contract.m_conId)

            print('status', ' ', con.order_dict[key]['status'])
            print('filled', ' ', con.order_dict[key]['filled'])
            print('permId', ' ', con.order_dict[key]['permId'])
            print('remaining', ' ', con.order_dict[key]['remaining'])
            print('avgFillPrice', ' ', con.order_dict[key]['avgFillPrice'])
            print('lastFillPrice', ' ', con.order_dict[key]['lastFillPrice'])
            print('whyHeld', ' ', con.order_dict[key]['whyHeld'])

        con.cancel_order(id1)
        time.sleep(0.2)
        con.get_open_orders()
        time.sleep(1)

        for key in con.order_dict:
            order = con.order_dict[key]['order']
            contract = con.order_dict[key]['contract']
            print('%s' % '-'*60)
            print('m_orderId       = %d' % order.m_orderId)
            print('m_clientId      = %d' % order.m_clientId)
            print('m_permId        = %d' % order.m_permId)
            print('m_action        = %s' % order.m_action)
            print('m_totalQuantity = %d' % order.m_totalQuantity)
            print('m_orderType     = %s' % order.m_orderType)
            print('contract        = %d' % contract.m_conId)

        con.close()
        time.sleep(0.5)

if __name__ == "__main__":
    unittest.main()
