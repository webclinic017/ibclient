# -*- coding:utf-8 -*-
'''
Test account, portfolio and position
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
        self.acct_id = 'DU264039' # 'U8985278'

    def set_conn(self):
        client_id = random.randint(0, 10000)
        con = IBClient(port=7497, client_id=client_id)
        con.connect()
        return con

    def test_acct(self):
        self.set_data()
        con = self.set_conn()

        client_id = random.randint(0, 10000)
        context = Context(self.acct_id, starting_cash=120000)
        data = Data()

        con.register_strategy(context, data)
        con.enable_account_info_update()
        
        for i in range(2):
            print('%s' % '-'*60)
            print('account_id                      = %s' % (context.account.account_id                    ))
            print('accrued_interest                = %f' % (context.account.accrued_interest              ))
            print('buying_power                    = %f' % (context.account.buying_power                  ))
            print('cushion                         = %f' % (context.account.cushion                       ))
            print('day_trades_remaining            = %f' % (context.account.day_trades_remaining          ))
            print('equity_with_loan                = %f' % (context.account.equity_with_loan              ))
            print('excess_liquidity                = %f' % (context.account.excess_liquidity              ))
            print('initial_margin_requirement      = %f' % (context.account.initial_margin_requirement    ))
            print('leverage                        = %f' % (context.account.leverage                      ))
            print('maintenance_margin_requirement  = %f' % (context.account.maintenance_margin_requirement))
            print('net_leverage                    = %f' % (context.account.net_leverage                  ))
            print('net_liquidation                 = %f' % (context.account.net_liquidation               ))
            print('regt_equity                     = %f' % (context.account.regt_equity                   ))
            print('regt_margin                     = %f' % (context.account.regt_margin                   ))
            print('settled_cash                    = %f' % (context.account.settled_cash                  ))
            print('total_positions_value           = %f' % (context.account.total_positions_value         ))
            print('%s' % '-'*60)
            print('starting_cash   = %f' % context.portfolio.starting_cash     )
            print('capital_used    = %f' % context.portfolio.capital_used      )
            print('pnl             = %f' % context.portfolio.pnl               )
            print('portfolio_value = %f' % context.portfolio.portfolio_value   )
            print('positions_value = %f' % context.portfolio.positions_value   )
            print('returns         = %f' % context.portfolio.returns           )
            for sid in context.portfolio.positions:
                pos = context.portfolio.positions[sid]
                print('%s' % '-'*30)
                print('sid             = %f' %  pos.sid             )
                print('amount          = %f' %  pos.amount          )
                print('cost_basis      = %f' %  pos.cost_basis      )
                print('last_sale_price = %f' %  pos.last_sale_price )
                print('unrealized_pnl  = %f' %  pos.unrealized_pnl  )
                print('realized_pnl    = %f' %  pos.realized_pnl    )
            
            time.sleep(30)

        # TODO: add test logic here
        time.sleep(5)
        con.close()

if __name__ == "__main__":
    unittest.main()
