# coding=utf-8
'''
Account, Portfolio, and Position
For simplicity, 1 Account : 1 Portfolio instance; 1 Portfolio : N Positions
Created on 11/21/2016
@author: Jin Xu
@contact: jin_xu1@qq.com
'''
from __future__ import absolute_import, print_function, division
import pandas as pd
import numpy as np
from ib.ext.Contract import Contract


# context.portfolio.positions
class Portfolio(object):
    ''' Current assumption is 1 portfolio : 1 account.
    The portfolio object is accessed using  context.portfolio and has the following properties:
        capital_used
            Float: The net capital consumed (positive means spent) by buying and selling securities up to this point.cash
            Float: The current amount of cash in your portfolio.
        pnl
            Float: Dollar value profit and loss, for both realized and unrealized gains.
        positions
            Dictionary: A dictionary of all the open positions, keyed by security ID. More information about each position object can be found in
            the next section.
        portfolio_value
            Float: Sum value of all open positions and ending cash balance.
        positions_value
            Float: Sum value of all open positions.
        returns
            Float: Cumulative percentage returns for the entire portfolio up to this point. Calculated as a fraction of the starting value of the
            portfolio. The returns calculation includes cash and portfolio value. The number is not formatted as a percentage, so a 10% return is
            formatted as 0.1.
        starting_cash
            Float: Initial capital base for this backtest or live execution.start_date
    '''

    def __init__(self, account_id, starting_cash=1.):
        # the account this portfolio linked to
        self.account = Account(account_id)
        self.starting_cash = float(starting_cash)
        self.capital_used = float()
        self.pnl = float()
        self.positions = dict()
        # self.portfolio_value = self.account.net_liquidation
        # self.positions_value = self.account.total_positions_value
        self.returns = float()

    @property
    def portfolio_value(self):
        return self.account.net_liquidation

    @property
    def positions_value(self):
        return self.account.total_positions_value

    @property
    def cash(self):
        return self.account.excess_liquidity

    @property
    def leverage(self):
        return self.account.leverage

    #
    # def update(self, contract, position, marketPrice, marketValue, averageCost, unrealizedPNL, realizedPNL,
    #            accountName):
    #
    #     if not isinstance(contract, Contract):
    #         raise TypeError("contract must be a contract object")
    #
    #     # sid = (contract.m_conId, contract.m_symbol, contract.m_localSymbol)
    #     sid = contract.m_conId
    #     # TODO: use contract's unique ID as KEY
    #     if sid in self.positions:
    #         self.positions.pop(sid)
    #     self.positions[sid] = Position(sid, position, marketPrice, averageCost, unrealizedPNL, realizedPNL)
    #
    #     # sum all positions' value
    #     self.positions_value = 0.
    #     for sid in self.positions:
    #         p = self.positions[sid]
    #         self.positions_value += p.amount * p.last_sale_price
    #
    #     self.portfolio_value = self.positions_value + self.account.excess_liquidity
    #     self.pnl = self.portfolio_value - self.starting_cash
    #     assert (self.starting_cash != 0)
    #     self.returns = self.portfolio_value / self.starting_cash


    def update_positions(self, symbol, contract, position, marketPrice, marketValue, averageCost,
                         unrealizedPNL, realizedPNL, accountName):

        if not isinstance(contract, Contract):
            raise TypeError("contract must be a contract object")

        # sid = (contract.m_conId, contract.m_symbol, contract.m_localSymbol)
        sid = contract.m_conId

        self.positions[symbol] = Position(sid, position, marketPrice, averageCost, unrealizedPNL, realizedPNL)
        # updatePortfolio <ib.ext.Contract.Contract object at 0x0000000003EDD390> <class 'ib.ext.Contract.Contract'>
        # 4 10223.178711 10225.35 DU264039
        # calc
        # ['sid', 'amount', 'last_sale_price', 'cost_basis', 'unrealizedPNL', 'realizedPNL']

        # NOTE: out dated code; chagne to use the account member values instead;
        # # sum all positions' value
        # self.positions_value = 0.
        # for symbol in self.positions:
        #     p = self.positions[symbol]
        #     self.positions_value += p.amount * p.last_sale_price
        #
        # self.portfolio_value = self.positions_value + self.account.excess_liquidity

        # TODO: check the starting_cash
        self.pnl = self.portfolio_value - self.starting_cash
        assert (self.starting_cash != 0)
        self.returns = self.portfolio_value / self.starting_cash

    def print_summary(self):
        print('%s' % '-' * 60)
        print('portfolio_value            = %s' % (self.portfolio_value))
        print('positions_value            = %f' % (self.positions_value))
        print(Position.HEDAER)
        for symbol in self.positions:
            print('{} {}'.format(symbol, str(self.positions[symbol])))
        print('%s' % '-' * 60)

class Account(object):
    '''
        Below is a table of account fields available to reference in a live trading algorithm with Interactive Brokers.
        context.account.accrued_interest (IB: AccruedCash)
        (Float) Interest that has accumulated but has not been paid or charged.
        (Float) Equity with loan value less the initial margin requirement.
        context.account.buying_power (IB: BuyingPower)
        (Float)
        IB Cash Account: Minimum (Equity with Loan Value, Previous Day Equity with Loan Value)-Initial Margin.
        IB Margin Account: Available Funds * 4.
        context.account.cushion (IB: Cushion)
        (Float) Excess liquidity as a percentage of net liquidation.
        context.account.day_trades_remaining (IB: DayTradesRemaining)
        (Float) The number of open/close trades a user can place before pattern day trading is detected.
        context.account.equity_with_loan (IB: EquityWithLoanValue)
        (Float)
        IB Cash Account: Settled Cash.
        IB Margin Account: Total cash value + stock value + bond value + (non-U.S. & Canada securities options value).
        context.account.excess_liquidity (IB: ExcessLiquidity)
        (Float) Equity with loan value less the maintenance margin.Backtest value:  context.portfolio.cash
        context.account.initial_margin_requirement (IB: InitMarginReq)
        (Float) The minimum portion of a new security purchase that an investor must pay for in cash.
        context.account.leverage (IB: GrossLeverage)
        (Float) Gross position value divided by net liquidation.
        context.account.maintenance_margin_requirement (IB: MaintMarginReq)
        (Float) The amount of equity which must be maintained in order to continue holding a position.
        context.account.net_leverage (IB: NetLeverage)
        (Float) The default value is also used for live trading.
        context.account.net_liquidation (IB: NetLiquidation)
        (Float) Total cash, stock, securities options, bond, and fund value.
        context.account.regt_equity (IB: RegTEquity)
        (Float)
        IB Cash Account: Settled Cash.IB Margin Account: Total cash value + stock value + bond value + (non-U.S. & Canada securities options value).
        context.account.regt_margin (IB: RegTMargin)
        (Float) The margin requirement calculated under US Regulation T rules.
        context.account.settled_cash (IB: SettledCash)
        (Float) Cash recognized at the time of settlement less purchases at the time of trade, commissions, taxes, and fees.
        context.account.total_positions_value (IB: GrossPositionValue)
        (Float) The sum of the absolute value of all stock and equity option positions.
    '''

    KEYS = ['AvailableFunds', 'AccruedCash', 'BuyingPower', 'Cushion', 'EquityWithLoanValue',
            'ExcessLiquidity', 'InitMarginReq', 'MaintMarginReq', 'NetLiquidation', 'RegTEquity',
            'RegTMargin', 'SettledCash', 'GrossPositionValue']

    def __init__(self, account_id):
        self.account_id = account_id
        self.account_currency = ''
        self.accrued_interest = 0.
        self.buying_power = 0.
        self.cushion = 0.
        self.day_trades_remaining = 0.
        self.equity_with_loan = 0.
        self.excess_liquidity = 0.
        self.initial_margin_requirement = 0.
        self.leverage = 0.
        self.maintenance_margin_requirement = 0.
        self.net_leverage = 0.
        self.net_liquidation = 0.
        self.regt_equity = 0.
        self.regt_margin = 0.
        self.settled_cash = 0.
        self.total_positions_value = 0.

    def update(self, key, value, currency, account_id):
        # key, value, currency, accountName
        self.account_currency = currency
        if account_id != self.account_id:
            print('Received incorrect IB account ID')
            return

        if key == 'AvailableFunds':      self.available_fund = float(value)
        if key == 'AccruedCash':         self.accrued_interest = float(value)
        if key == 'BuyingPower':         self.buying_power = float(value)
        if key == 'Cushion':             self.cushion = float(value)
        if key == 'EquityWithLoanValue': self.equity_with_loan = float(value)
        if key == 'ExcessLiquidity':     self.excess_liquidity = float(value)
        if key == 'InitMarginReq':       self.initial_margin_requirement = float(value)
        if key == 'MaintMarginReq':      self.maintenance_margin_requirement = float(value)
        if key == 'NetLiquidation':      self.net_liquidation = float(value)
        if key == 'RegTEquity':          self.regt_equity = float(value)
        if key == 'RegTMargin':          self.regt_margin = float(value)
        if key == 'SettledCash':         self.settled_cash = float(value)
        if key == 'GrossPositionValue':  self.total_positions_value = float(value)

        # GrossLeverage (Float) Gross position value divided by net liquidation.
        if self.net_liquidation != 0.:
            self.leverage = self.total_positions_value / self.net_liquidation
        else:
            self.leverage = 0.
        # if key == '':         self.day_trades_remaining            = float(value)
        # if key == '':         self.net_leverage    = float(value)

    
    def print_summary(self):
        print('%s' % '-' * 60)
        print('account_id                      = %s' % (self.account_id))
        print('accrued_interest                = %f' % (self.accrued_interest))
        print('buying_power                    = %f' % (self.buying_power))
        print('cushion                         = %f' % (self.cushion))
        print('day_trades_remaining            = %f' % (self.day_trades_remaining))
        print('equity_with_loan                = %f' % (self.equity_with_loan))
        print('excess_liquidity                = %f' % (self.excess_liquidity))
        print('initial_margin_requirement      = %f' % (self.initial_margin_requirement))
        print('leverage                        = %f' % (self.leverage))
        print('maintenance_margin_requirement  = %f' % (self.maintenance_margin_requirement))
        print('net_leverage                    = %f' % (self.net_leverage))
        print('net_liquidation                 = %f' % (self.net_liquidation))
        print('regt_equity                     = %f' % (self.regt_equity))
        print('regt_margin                     = %f' % (self.regt_margin))
        print('settled_cash                    = %f' % (self.settled_cash))
        print('total_positions_value           = %f' % (self.total_positions_value))
        print('%s' % '-' * 60)

class Position(object):
    '''
    The position object represents a current open position, and is contained inside the positions dictionary. For example, if you had an open
    AAPL position, you'd access it using  context.portfolio.positions[symbol('AAPL')]. The position object has the following properties:
    amount
    Integer: Whole number of shares in this position.
    cost_basis
    Float: The volume-weighted average price paid (price and commission) per share in this position.
    last_sale_price
    Float: Price at last sale of this security. This is identical to  close_price and  price.
    sid
    Integer: The ID of the security.
    '''

    HEDAER = "\tlast_price\tamount\t\tavg_cost\t\tunrealized_pnl\t\trealized_pnl"

    def __init__(self, sid, amount, last_sale_price, cost_basis, unrealizedPNL, realizedPNL):
        self.amount = int(amount)
        self.cost_basis = float(cost_basis)
        self.last_sale_price = float(last_sale_price)
        self.sid = int(sid)
        self.unrealized_pnl = float(unrealizedPNL)
        self.realized_pnl = float(realizedPNL)

    def __str__(self):
        return "\t%.2f\t\t%d\t\t%.2f\t\t%.2f\t\t%.2f\n" % (self.last_sale_price, self.amount, self.cost_basis,
                                                           self.unrealized_pnl, self.realized_pnl)
