﻿# coding=utf-8

'''
IB Message Callback Functions
Created on 10/18/2016
@author: Jin Xu
@contact: jin_xu1@qq.com
'''
from __future__ import absolute_import, print_function, division
import pytz
from datetime import datetime
from copy import copy

from ib.ext.EWrapper import EWrapper
from ib.ext.EClientErrors import EClientErrors
from .IBUtils import *
from .IBSystemErrors import *
from .Account import *

class IBMsgWrapper(EWrapper):
    """ This class define IB Sock Message Call Back Mehtods, determining the way handling these messages"""
    def __init__(self, ib_client):
        """Constructor"""
        super(IBMsgWrapper, self).__init__()
        self.ib_client = ib_client                       # IB socket client instance
        self.ib_client_name = ib_client.client_name      # name of a IB socket client instance

    #
    # History and real-time bar callbacks
    #
    def historicalData(self, reqId, date, open, high, low, close, volume, count, WAP, hasGaps):
        ''' This callback function handles message.historicalData generated by reqHistoricalData API.
            This handler parse price history data and append the record (type tuple) to data buffer list.

        Returns:
            None
        '''
        #print((date, open, high, low, close, volume)
        if reqId in self.ib_client.ipc_msg_dict:
            request = self.ib_client.ipc_msg_dict[reqId][0]
            response = self.ib_client.ipc_msg_dict[reqId][1]
        else:
            print('historicalData: reqId(%s) is not in ib_client.ipc_msg_dict' % str(reqId))
            return

        if int(high) != -1:
            response.price_hist.append((date, open, high, low, close, volume))
        else:
            # end of receiving data
            response.status = ResponseDetails.STATUS_FINISHED
            response.event.set()

    def realtimeBar(self, reqId, time, open, high, low, close, volume, wap, count):
        """ generated source for method realtimeBar """
        #print((reqId, time, open, high, low, close, volume)

        if reqId in self.ib_client.ipc_msg_dict:
            request = self.ib_client.ipc_msg_dict[reqId][0]
            response = self.ib_client.ipc_msg_dict[reqId][1]
        else:
            print('realtimeBar: reqId(%s) is not in ib_client.ipc_msg_dict' % str(reqId))
            return

        # convert the time to market/exchange time
        time = datetime.fromtimestamp(time)
        exchange = request.contract.m_exchange
        server_timezone = pytz.timezone("Asia/Shanghai")                        # timezone where the server runs
        mkt_timezone = pytz.timezone(IBEXCHANGE.get_timezone(exchange))         # Get Exchange's timezone
        adj_time = server_timezone.localize(time).astimezone(mkt_timezone)      # covert server time to Exchange's time
        adj_time = adj_time.strftime("%Y%m%d %H:%M:%S")                          # from datetime to string

        response.rt_price.append((adj_time, open, high, low, close, volume))
        return
    #
    # Order message callbacks
    #
    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld):
        """ generated source for method orderStatus """
        # print('orderStatus', orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld
        if clientId != self.ib_client.client_id:
            return
        key = (clientId, orderId)

        if key not in self.ib_client.order_dict:
            self.ib_client.order_dict[key] = {}

        self.ib_client.order_dict[key]['status'] = status
        self.ib_client.order_dict[key]['filled'] = bool(filled)
        self.ib_client.order_dict[key]['permId'] = int(permId)
        self.ib_client.order_dict[key]['remaining'] = int(remaining)
        self.ib_client.order_dict[key]['avgFillPrice'] = float(avgFillPrice)
        self.ib_client.order_dict[key]['lastFillPrice'] = float(lastFillPrice)
        self.ib_client.order_dict[key]['whyHeld'] = whyHeld

    def openOrder(self, orderId, contract, order, orderState):
        """ generated source for method openOrder """
        clientId = order.m_clientId
        if clientId != self.ib_client.client_id:
            return

        key = (clientId, orderId)
        if key not in self.ib_client.order_dict:
            self.ib_client.order_dict[key] = {}

        self.ib_client.order_dict[key]['contract'] = copy(contract)
        self.ib_client.order_dict[key]['order'] = copy(order)
        self.ib_client.order_dict[key]['status'] = orderState.m_status

    def openOrderEnd(self):
        """ generated source for method openOrderEnd """
        self.ib_client.get_order_event.set()

    def nextValidId(self, orderId):
        """ Get nextValid Order Id from IB host and update the order ID to the IB client instance"""
        self.ib_client.order_id = orderId

    #
    # Fundamental Data Handler
    #
    def fundamentalData(self, reqId, data):
        """ generated source for method fundamentalData """
        if reqId in self.ib_client.ipc_msg_dict:
            request = self.ib_client.ipc_msg_dict[reqId][0]
            response = self.ib_client.ipc_msg_dict[reqId][1]
        else:
            print('fundamentalData: reqId(%s) is not in ib_client.ipc_msg_dict' % str(reqId))
            return
        response.fundamental_data = data
        response.status = ResponseDetails.STATUS_FINISHED
        response.event.set()

    #
    # Tick messages handler
    #
    def tickPrice(self, tickerId, field, price, canAutoExecute):
        """ generated source for method tickPrice """
        # print('tickPrice', tickerId
        if field not in TICK_FIELDS:
            print('tickPrice', tickerId, field, price)
            return

        if tickerId in self.ib_client.ipc_msg_dict:
            request = self.ib_client.ipc_msg_dict[tickerId][0]
            response = self.ib_client.ipc_msg_dict[tickerId][1]
        else:
            print('tickPrice: reqId(%s) is not in ib_client.ipc_msg_dict' % str(tickerId))
            return

        field_id = TICK_FIELDS[field]
        response.tick_data[field_id] = price
        return

    def tickSize(self, tickerId, field, size):
        """ generated source for method tickSize """
        # print('tickSize', tickerId, field, size

        if field not in TICK_FIELDS:
            return

        if tickerId in self.ib_client.ipc_msg_dict:
            request = self.ib_client.ipc_msg_dict[tickerId][0]
            response = self.ib_client.ipc_msg_dict[tickerId][1]
        else:
            print('tickSize: reqId(%s) is not in ib_client.ipc_msg_dict' % str(tickerId))
            return

        field_id = TICK_FIELDS[field]
        response.tick_data[field_id] = size
        return

    def tickOptionComputation(self, tickerId, field, impliedVol, delta, optPrice, pvDividend, gamma, vega, theta, undPrice):
        """ generated source for method tickOptionComputation """
        pass

    def tickGeneric(self, tickerId, tickType, value):
        """ generated source for method tickGeneric """
        #print('tickGeneric', tickerId, tickType, value
        # 49 - halt, 0: no, 1: yes

        # https://interactivebrokers.github.io/tws-api/tick_types.html#gsc.tab=0
        pass

    def tickString(self, tickerId, tickType, value):
        """ generated source for method tickString """
        #print(tickerId, tickType, value, type(value)
        # IB_TICK_ID_TIMESTAMP    = 45
        # IB_TICK_ID_FIN_RATIOS   = 47
        # IB_TICK_ID_DIVIDENDS    = 59
        # IB_TICK_ID_NEWS         = 62

        if tickerId not in self.ib_client.ipc_msg_dict:
            print('tickString: reqId(%s) is not in ib_client.ipc_msg_dict' % str(tickerId))
            return
        if tickType not in TICK_STRING_TYPES:
            print('tickString: tickType(%s) is not in target list: %s' % (str(tickType), TICK_STRING_TYPES))
            return

        request = self.ib_client.ipc_msg_dict[tickerId][0]
        response = self.ib_client.ipc_msg_dict[tickerId][1]
        response.tick_str = value

        if tickType == TICK_TYPE_FIN_RATIOS or tickType == TICK_TYPE_DIVIDENDS:
            response.event.set()
            response.status = ResponseDetails.STATUS_FINISHED
            self.ib_client.connection.cancelMktData(tickerId)

        return

    def tickSnapshotEnd(self, reqId):
        """ generated source for method tickSnapshotEnd """
        # print('tickSnapshotEnd:', reqId

        # if reqId in self.ib_client.ipc_msg_dict:
        #     response = self.ib_client.ipc_msg_dict[reqId][1]
        #     response.snapshot_req_end.set()
        # else:
        #     print('tickSnapshotEnd: reqId(%s) is not in ib_client.ipc_msg_dict' % str(reqId)

        self.ib_client.tick_snapshot_req_end.set()
        return

    def tickEFP(self, tickerId, tickType, basisPoints, formattedBasisPoints, impliedFuture, holdDays, futureExpiry, dividendImpact, dividendsToExpiry):
        """ generated source for method tickEFP """
        pass

    #
    # General message handlers
    #
    def error(self, id=None, errorCode=None, errorMsg=None):


        '''
            error: 1 354 Requested market data is not subscribed.Delayed market data is available.Error&BEST/STK/Top&BEST/STK/Top
        '''

        info_ls = [IBSystemErrors.TWS_MKT_DATA_OK.m_errorCode, IBSystemErrors.TWS_HIST_DATA_OK.m_errorCode,
                   IBSystemErrors.TWS_HIST_DATA_INACTIVE.m_errorCode, IBSystemErrors.TWS_MKT_DATA_INACTIVE.m_errorCode,
                   399, 202]

        warning_ls = [10147,  # cancel_order when OrderId 400 that needs to be cancelled is not found.
                      ]

        error_ls = [430, 200]

        IB_FARM_DISPLAY_LS = ['secdefhk', 'hkhmds', 'usfarm.us',  'hfrarm', 'usfuture', 'usfuture.us',
                              'usfarm', 'ushmds', 'mcgw1.ibllc.com.cn']

        if errorCode in info_ls:
            # connection OK or Inactive list
            self.ib_client.connected = True
            # TODO: decode 'farm' name from this error msg
            for farm in IB_FARM_NAME_LS:
                if farm in errorMsg:
                    if 'is OK' in errorMsg or 'is inactive' in errorMsg:
                        self.ib_client.hmdf_status_dict[farm] = 'OK'
                    elif 'is broken' in errorMsg:
                        self.ib_client.hmdf_status_dict[farm] = 'BROKEN'

                    if farm in IB_FARM_DISPLAY_LS:
                        print('[TWS INFO] ', errorMsg)
            if errorCode == 202:
                print('[TWS INFO] ', errorMsg)

        elif errorCode in warning_ls:
            # connection OK or Inactive list
            print('[TWS WARNING] ', errorMsg)
        elif errorCode in error_ls:
            # this error will be handled below
            pass
        else:
            print('error:', id, errorCode, errorMsg)
            # TODO: decode 'farm' name from this error msg
            for farm in IB_FARM_NAME_LS:
                if farm in errorMsg and farm in IB_FARM_DISPLAY_LS:
                        print('[TWS INFO] ', errorMsg)

        # clear events
        if IBSystemErrors.TWS_MKT_DATA_OK.m_errorCode == errorCode or IBSystemErrors.TWS_MKT_DATA_INACTIVE == errorCode:
            self.ib_client.mdf_conn_event.clear()
            self.ib_client.conn_down_event.clear()
        if IBSystemErrors.TWS_HIST_DATA_OK.m_errorCode == errorCode or IBSystemErrors.TWS_HIST_DATA_INACTIVE == errorCode:
            self.ib_client.hdf_conn_event.clear()
            self.ib_client.conn_down_event.clear()

        # set events
        if IBSystemErrors.TWS_MKT_DATA_DISCON.m_errorCode == errorCode:
            self.ib_client.mdf_conn_event.set()
            # error: -1 2105 HMDS data farm connection is broken:euhmds
            for farm in IB_FARM_NAME_LS:
                if farm in errorMsg:
                    if 'is OK' in errorMsg or 'is inactive' in errorMsg:
                        self.ib_client.hmdf_status_dict[farm] = 'OK'
                    elif 'is broken' in errorMsg:
                        self.ib_client.hmdf_status_dict[farm] = 'BROKEN'

        if IBSystemErrors.TWS_HIST_DATA_DISCON.m_errorCode == errorCode:
            self.ib_client.hdf_conn_event.set()
            for farm in IB_FARM_NAME_LS:
                if farm in errorMsg:
                    if 'is OK' in errorMsg or 'is inactive' in errorMsg:
                        self.ib_client.hmdf_status_dict[farm] = 'OK'
                    elif 'is broken' in errorMsg:
                        self.ib_client.hmdf_status_dict[farm] = 'BROKEN'

        if errorCode == EClientErrors.CONNECT_FAIL.m_errorCode or errorCode == EClientErrors.UPDATE_TWS.m_errorCode or \
                        errorCode == IBSystemErrors.TWS_SOCKET_DROP.m_errorCode or \
                        errorCode == IBSystemErrors.TWS_CONN_LOST.m_errorCode:
            self.ib_client.connected = False
            self.ib_client.conn_down_event.set()
            for farm in IB_FARM_NAME_LS:
                if farm in errorMsg:
                    if 'is OK' in errorMsg or 'is inactive' in errorMsg:
                        self.ib_client.hmdf_status_dict[farm] = 'OK'
                    elif 'is broken' in errorMsg:
                        self.ib_client.hmdf_status_dict[farm] = 'BROKEN'

        # Fundamentals Req
        if errorCode == 200 or errorCode == 430:
            # Sample: error: 3 200 No security definition has been found for the request
            # Sample: 4 430 We are sorry, but fundamentals data for the security specified is not available.failed to fetch
            if id in self.ib_client.ipc_msg_dict:
                response = self.ib_client.ipc_msg_dict[id][1]
                response.request_id = id
                response.status = errorCode
                response.error_msg = errorMsg # 'RequestID=%d, ErrorCode=%d, Reason:%s' % (id, errorCode, errorMsg)
                response.event.set()

        if errorCode == 399:
            # Sample: error: 1 399 Order Message:
            pass

    def error_0(self, strval=None):
        print('error_0', strval)

    def error_1(self, id=None, errorCode=None, errorMsg=None):
        print('error_1', id, errorCode, errorMsg)

    def currentTime(self, time):
        """ generated source for method currentTime """
        print('currentTime', time)

    def connectionClosed(self):
        print('connectionClosed: TWS closes the sockets connection or TWS is shutting down.')
        self.ib_client.connected = False
        self.ib_client.conn_down_event.set()

    #
    # Account Info handler
    #
    def updateAccountValue(self, key, value, currency, accountName):
        """ generated source for method updateAccountValue """
        if key in Account.KEYS:
            self.ib_client.context.account.update(key, value, currency, accountName)

    def updatePortfolio(self, contract, position, marketPrice, marketValue, averageCost, unrealizedPNL, realizedPNL, accountName):
        """ generated source for method updatePortfolio """

        '''
            print(contract, position, marketPrice, marketValue, averageCost, unrealizedPNL, realizedPNL, accountName)
            <ib.ext.Contract.Contract object at 0x10f053470> 322000 3.76474355 1212247.43 3.73681765 8992.15 0.0 DU264039
            <ib.ext.Contract.Contract object at 0x10f053470> 0 3.48525 0.0 0.0 0.0 2623.26 DU264039
            <ib.ext.Contract.Contract object at 0x10f053470> 0 3.67499995 0.0 0.0 0.0 517.25 DU264039
            <ib.ext.Contract.Contract object at 0x10f053470> 0 5.48500015 0.0 0.0 0.0 626.46 DU264039
            <ib.ext.Contract.Contract object at 0x10f053470> 0 6.8449998 0.0 0.0 0.0 218.71 DU264039
            <ib.ext.Contract.Contract object at 0x10f053470> 310000 6.76399995 2096839.98 6.78236975 -5694.64 0.0 DU264039
        '''

        if contract and int(position) != 0 and float(marketValue) != float(0):
            symbol = self.ib_client.context.get_symbol_by_conid(int(contract.m_conId))
            if symbol is None:
                #
                # NOTE: it could be the case that the account has positions manually ordered not in strategy's asset universe
                #
                #raise ValueError("contract ID {} not found in the context lookup table. Please check the database file during the init.".format(contract.m_conId))
                print("contract ID {} not found in the context lookup table. Please check the database file during the init.".format(
                    int(contract.m_conId)))
            else:
                #self.ib_client.context.portfolio.update(symbol, contract, position, marketPrice, marketValue, averageCost, unrealizedPNL, realizedPNL, accountName)
                self.ib_client.context.portfolio.update_positions(symbol, contract, position, marketPrice,
                                                                  marketValue, averageCost, unrealizedPNL, realizedPNL, accountName)


    def updateAccountTime(self, timeStamp):
        """ generated source for method updateAccountTime """
        #print('updateAccountTime', timeStamp, type(timeStamp)
        pass

    def accountDownloadEnd(self, accountName):
        """ generated source for method accountDownloadEnd """
        pass

    def position(self, account, contract, pos, avgCost):
        """ generated source for method position """
        #print('postion', account, contract, pos, avgCost
        pass

    def positionEnd(self):
        """ generated source for method positionEnd """
        #print('positionEnd'
        pass

    def accountSummary(self, reqId, account, tag, value, currency):
        """ generated source for method accountSummary """
        #print('accountSummary', reqId, account, tag, value, currency
        pass

    def accountSummaryEnd(self, reqId):
        """ generated source for method accountSummaryEnd """
        #print('accountSummaryEnd', reqId
        pass

    #
    # Get Contract Info
    #
    def contractDetails(self, reqId, contractDetails):
        """ generated source for method contractDetails """

        if reqId in self.ib_client.ipc_msg_dict:
            request = self.ib_client.ipc_msg_dict[reqId][0]
            response = self.ib_client.ipc_msg_dict[reqId][1]
        else:
            print('contractDetails: reqId(%s) is not in ib_client.ipc_msg_dict' % str(reqId))
            return
        response.contract_list.append(contractDetails)

    def bondContractDetails(self, reqId, contractDetails):
        """ generated source for method bondContractDetails """
        if reqId in self.ib_client.ipc_msg_dict:
            request = self.ib_client.ipc_msg_dict[reqId][0]
            response = self.ib_client.ipc_msg_dict[reqId][1]
        else:
            print('contractDetails: reqId(%s) is not in ib_client.ipc_msg_dict' % str(reqId))
            return
        response.contract_list.append(contractDetails)

    def contractDetailsEnd(self, reqId):
        """ generated source for method contractDetailsEnd """
        if reqId in self.ib_client.ipc_msg_dict:
            request = self.ib_client.ipc_msg_dict[reqId][0]
            response = self.ib_client.ipc_msg_dict[reqId][1]
        else:
            print('contractDetailsEnd: reqId(%s) is not in ib_client.ipc_msg_dict' % str(reqId))
            return
        response.status = ResponseDetails.STATUS_FINISHED
        response.event.set()

    #
    # Others
    #
    def execDetails(self, reqId, contract, execution):
        """ generated source for method execDetails """
        pass

    def execDetailsEnd(self, reqId):
        """ generated source for method execDetailsEnd """
        pass

    def updateMktDepth(self, tickerId, position, operation, side, price, size):
        """ generated source for method updateMktDepth """
        pass

    def updateMktDepthL2(self, tickerId, position, marketMaker, operation, side, price, size):
        """ generated source for method updateMktDepthL2 """
        pass

    def updateNewsBulletin(self, msgId, msgType, message, origExchange):
        """ generated source for method updateNewsBulletin """
        pass

    def managedAccounts(self, accountsList):
        """ generated source for method managedAccounts """
        pass

    def receiveFA(self, faDataType, xml):
        """ generated source for method receiveFA """
        pass

    def scannerParameters(self, xml):
        """ generated source for method scannerParameters """
        pass

    def scannerData(self, reqId, rank, contractDetails, distance, benchmark, projection, legsStr):
        """ generated source for method scannerData """
        pass

    def scannerDataEnd(self, reqId):
        """ generated source for method scannerDataEnd """
        pass

    def deltaNeutralValidation(self, reqId, underComp):
        """ generated source for method deltaNeutralValidation """
        pass

    def marketDataType(self, reqId, marketDataType):
        """ generated source for method marketDataType """
        pass

    def commissionReport(self, commissionReport):
        """ generated source for method commissionReport """
        pass
