# -*- coding:utf-8 -*-
'''
Created on 11/08/2016
@author: Jin Xu
'''

import datetime
import time
from time import sleep, ctime
import random
import pandas as pd
import numpy as np

from ibclient import *



# mkt cap > $20B
big_cap_ls = ['AAPL', 'ABT', 'TAP', 'ADBE', 'ADI', 'ADM', 'AEP', 'AET', 'AFL', 'AIG', 'AMAT', 'TWX', 'AMGN', 'AON',
              'APA', 'APC', 'APD', 'APH', 'ADP', 'AXP', 'AZO', 'BA', 'BAC', 'BAX', 'BDX', 'BEN', 'BHI', 'BK', 'BMY',
              'BSX', 'CAT', 'C', 'CAH', 'CELG', 'CI', 'CL', 'CMCS A', 'COST', 'CSCO', 'CSX', 'CMI', 'D', 'DD', 'DE',
              'DHR', 'DIS', 'DOW', 'DUK', 'DVN', 'ECL', 'ED', 'EMR', 'EOG', 'EA', 'ESRX', 'ETN', 'F', 'FDX',
              'S', 'NEE', 'GD', 'GE', 'GILD', 'GIS', 'GLW', 'HAL', 'MNST', 'HCN', 'HD', 'HSY', 'HUM', 'HPQ', 'IBM',
              'BIIB', 'INTC', 'ITW', 'JNJ', 'K', 'KMB', 'KO', 'KR', 'LLY', 'LOW', 'LUV', 'MCD', 'MDT', 'CVS', 'SPGI',
              'MMC', 'MMM', 'MO', 'MRK', 'MSFT', 'MTB', 'MYL', 'NKE', 'NOC', 'NSC', 'NWL', 'OMC', 'ORCL', 'OXY', 'PAYX',
              'PCAR', 'PCG', 'PEG', 'PEP', 'PFE', 'PG', 'PNC', 'PPG', 'PPL', 'PX', 'QCOM', 'REGN', 'ROST', 'RTN', 'T',
              'SBUX', 'SCHW', 'SHW', 'SLB', 'SO', 'TRV', 'STT', 'STI', 'STJ', 'SYK', 'SYY', 'TEVA', 'TJX', 'TMO', 'TXN',
              'JCI', 'TSN', 'UNH', 'UNP', 'UTX', 'VFC', 'CBS', 'VLO', 'VRTX', 'WBA', 'WFC', 'WMB', 'WMT', 'WY', 'XOM',
              'AGN', 'CB', 'INT', 'GGP', 'ORLY', 'EQR', 'ATVI', 'SPG', 'BRK_B', 'SIRI', 'KEP', 'COF', 'FOXA', 'MCK',
              'LMT', 'DISH', 'EL', 'SCCO', 'ALXN', 'EIX', 'YHOO', 'AMTD', 'AMZN', 'BBT', 'MS', 'PXD', 'YUM', 'VTR',
              'AVB', 'CTSH', 'EPD', 'WM', 'CCI', 'NVDA', 'PCLN', 'GS', 'RAI', 'BLK', 'UPS', 'TGT', 'MET', 'NTES', 'VZ',
              'EXC', 'MON', 'MDLZ', 'FIS', 'ZBH', 'ANTM', 'CVX', 'PR', 'NFLX', 'COP', 'CME', 'EQIX', 'CCL', 'AMT',
              'SRE', 'PLD', 'EBAY', 'ALL', 'STZ', 'PSA', 'JPM', 'USB', 'HON', 'ISRG', 'ACN', 'MAR', 'ETP', 'CRM',
              'GOOG_L', 'LVS', 'LBTY_A', 'BID', 'ICE', 'UAL', 'MA', 'SE', 'TMUS', 'DAL', 'DFS', 'TEL', 'BX', 'VMW',
              'PM', 'V', 'AVGO', 'DG', 'CHTR', 'LYB', 'TSLA', 'WPZ', 'GM', 'KMI', 'HCA', 'LNKD', 'MPC', 'PSX', 'FB',
              'ABBV', 'ZTS', 'AAL', 'HLT', 'JD', 'SYF', 'BABA', 'PYPL', 'HPE']


# main_func(sec_, 666)
def main_func(security_list=[], f_path = 'G:\\analyst_estimates.csv'):
    print('starting at:', ctime())

    client_id = random.randint(0, 10000)
    acct_id = 'DU264039' #'U8985278'  # 'DU264039'
    port = 7496
    context = Context(acct_id, starting_cash=120000)
    data = Data()
    con = IBClientPro(client_id=client_id, port=port)
    con.connect()
    con.register_strategy(context, data)

    report_df = pd.DataFrame()
    count = 0
    for sec in security_list:
        try:
            df = con.get_analyst_estimates(sec)   # timeout = 100 sec
        except RuntimeError:
            # clean up
            print('[', ctime(), ']', 'Got break when requesting for %s' % (sec))

            report_df.to_csv(f_path)
            sleep(20)
            continue

        if df is not None:
            if len(df) > 0:
                report_df = report_df.append(df)
                count += 1
                print('.')
                if count % 20 == 0:
                    report_df.to_csv(f_path)
        sleep(0.2)

    # clean up
    print('[', ctime(), ']', 'Job finished. Closing TWS connection...')
    con.close()

