#-*- coding: utf-8 -*-

'''

   Trader Station for TWS (GUI)
   This application is designed for the trader who should notaccess
   TWS and client account directly. Other features, such as risk management,
   trading signals, and stop win/loss, could be integrated into this GUI.

'''


'''
TODO:

Display
1) add real-time quato price/ask/bid
2) add long term chart and trend
3) add trading signals
4) add orders/positions

Intelligence
1) option pricing model, and real-time volatility estimation.
2) N-stock weighted volume vs. shares outstanding; # of ups vs. # of downs
3) Shanghai short-term interest rate

'''

import numpy as np
import pandas as pd
import time
from time import sleep, ctime
from datetime import datetime, timedelta
from threading import Timer
import threading

from ibclient import *

from Tkinter import Canvas, Label, Tk, BOTH, Text, Menu, END, Button
from Tkinter import S, E, W, NW, CENTER
from PIL import Image, ImageTk
import tkFileDialog
from ttk import Frame, Style
from tkMessageBox import askokcancel
import matplotlib
import matplotlib.animation as animation
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.ticker import Formatter
from matplotlib.finance import candlestick2_ochl, candlestick_ochl
from matplotlib import rc
# Set the global font to be DejaVu Sans, size 10 (or any other sans-serif font of your choice!)
# http://matplotlib.org/users/customizing.html
#rc('font',**{'family':'sans-serif','sans-serif':['DejaVu Sans'],'size':10})

from ScrolledText import *

# Strategy configurations
PRICE_UNIT = 2.5        # Constant
SID = int(252003475)    # SID = int(252003475) # <--XINA50 201701
TARGET_AMOUNT = 10

IB_ACCOUNT = 'DU264039'  # Demo Acct 'DU264039';
starting_cash = 20000
context = Context(account_id=IB_ACCOUNT, starting_cash=starting_cash)
context.con = None
data = Data()

win_high = 680
win_width = 1200


def init_matplotlib():
    """Just some Matplotlib settings."""
    matplotlib.rcParams["font.size"] = 10
    matplotlib.rcParams["axes.xmargin"] = 0.2
    matplotlib.rcParams["axes.ymargin"] = 0.2
    # End of InitMatplotlib().

def initialize(context):
    # connect to TWS
    context.client_name = 'XINA50 Intraday Break'
    context.client_id = 108
    port = 7497
    context.con = IBClient(client_id=context.client_id, port=port, client_name=context.client_name)
    context.con.host = 'localhost' #'192.168.1.107'
    context.con.register_strategy(context, data)
    ret = context.con.connect()
    if ret is False:
        return

    # Setup time related variables
    now = datetime.now()
    context.year = now.year
    context.month = now.month
    context.day = now.day

    con = context.con
    # Define security
    context.current_contract = new_futures_contract('XINA50', 'SGX', False, '201702', 'CN', 'USD')
    context.security_list = [context.current_contract]

    # Define data bank
    context.tick_price = {}
    context.order_list = []
    for sec in context.security_list:
        context.tick_price[sec] = []

    # for order and position management
    context.long_positions = 0              # used for Long algo only
    context.short_positions = 0             # used for Short algo only

    # for hist and real-time market data (price/vol)
    context.current_data = None
    context.rt_price = None
    context.tick_data = None
    context.price_df = None
    context.timeout_flag = False

    # Get real-time price
    try:
        id1, context.rt_price = context.con.request_realtime_price(context.current_contract)
        time.sleep(0.5)
    except RuntimeError:
        print('request_realtime_price:RuntimeError')
        con.close()


    # Get tick data
    try:
        # {'lastPrice': 166.62, 'openPrice': 166.1, 'askVolume1': 0, 'bidVolume1': 0, 'lastVolume': 1, 'volume': 13991, 'lastTradeTS': 1483045199, 'lowPrice': 166.0, 'highPrice': 166.99, 'bidPrice1': -1.0, 'openInterest': -1, 'preClosePrice': 166.19, 'askPrice1': -1.0}
        id2, context.tick_data = con.request_tick_data(context.current_contract)
        time.sleep(0.5)
    except RuntimeError:
        print('test_get_tick:RuntimeError')
        con.close()


def isin_tranding_hours():
    """
    Called XXX.
    """
    now = datetime.now()
    year = now.year
    month = now.month
    day = now.day

    t_0930 = datetime(year, month, day, 9, 00)
    t_1130 = datetime(year, month, day, 11, 30)
    t_1300 = datetime(year, month, day, 13, 00)
    t_1500 = datetime(year, month, day, 18, 00)

    # if (now > t_0930 and now < t_1130) or (now > t_1300 and now < t_1500):
    if (now > t_0930 and now < t_1500):
        return True
    else:
        return False

def order_timeout(context, data, order_id):
    client_id = context.con.client_id
    order_info = context.con.order_dict[(client_id, order_id)]
    order_status = order_info['status']
    order_filled = order_info['filled']

    if order_filled is False:
        context.con.cancel_order(order_id)
    context.timeout_flag = True


def b(context, data):
    """
    Called XXX.
    """
    if isin_tranding_hours() == False:
        print('%s: out of trading hour.' % (ctime()))
        return

    con = context.con
    client_id = context.con.client_id
    target_amt = TARGET_AMOUNT
    # get bid data
    tick_data = context.tick_data

    # algo to cehck our bidding price
    spread = (tick_data['askPrice1'] - tick_data['bidPrice1'])
    if spread > PRICE_UNIT:
        price = tick_data['bidPrice1'] + PRICE_UNIT
    else:
        if tick_data['bidVolume1'] > tick_data['askVolume1']:
            price = tick_data['bidPrice1'] + PRICE_UNIT
        else:
            price = tick_data['bidPrice1']

    # place limited order
    print('%s: placing order.... amount %d, price %f' % (ctime(), target_amt, price))
    order_id = con.order_amount(context.current_contract, target_amt, style=LimitOrder(price))
    last_price = price

    # wait for N sec and then check order status
    sleep(2)
    order_info = context.con.order_dict[(client_id, order_id)]
    print('%s: order filled? %s' % (ctime(), order_info['filled']))
    if order_info['filled']:
        return

    t = Timer(60, order_timeout, (context, data, order_id))
    context.timeout_flag = False
    t.start()

    while order_info['filled'] is False and context.timeout_flag is False:
        # update price
        spread = (tick_data['askPrice1'] - tick_data['bidPrice1'])
        if spread > PRICE_UNIT:
            price = tick_data['bidPrice1'] + PRICE_UNIT
        else:
            if tick_data['bidVolume1'] > tick_data['askVolume1']:
                price = tick_data['bidPrice1'] + PRICE_UNIT
            else:
                price = tick_data['bidPrice1']

        if price != last_price:
            print('%s: modifying order.... amount %d, price %f' % (ctime(), target_amt, price))
            con.modify_order(order_id, context.current_contract, target_amt, style=LimitOrder(price))
            last_price = price
        sleep(8)

    if order_info['filled'] and context.timeout_flag is False:
        t.cancel()

    return


def c(context, data):
    """
    Called XXX.
    """
    if isin_tranding_hours() is False:
        return

    # get current position
    if SID in context.portfolio.positions:
        current_amt = context.portfolio.positions[SID].amount
        target_amount = -1*current_amt
    else:
        return

    # get bid data
    con = context.con
    client_id = context.con.client_id
    tick_data = context.tick_data

    # algo to cehck our bidding price
    if target_amount > 0:
        # get price for BUY BACK
        spread = (tick_data['askPrice1'] - tick_data['bidPrice1'])
        if spread > PRICE_UNIT:
            price = tick_data['bidPrice1'] + PRICE_UNIT
        else:
            if tick_data['bidVolume1'] > tick_data['askVolume1']:
                price = tick_data['bidPrice1'] + PRICE_UNIT
            else:
                price = tick_data['bidPrice1']
    else:
        # get price for SELL to cover
        pass

    # place limited order
    order_id = con.order_amount(context.current_contract, target_amount, style=LimitOrder(price))
    last_price = price

    # wait for N sec and then check order status
    sleep(10)
    order_info = context.con.order_dict[(client_id, order_id)]

    t = Timer(60, order_timeout, (context, data, order_id))
    context.timeout_flag = False
    t.start()

    while order_info['filled'] is False and context.timeout_flag is False:
        # update price
        spread = (tick_data['askPrice1'] - tick_data['bidPrice1'])
        if spread > PRICE_UNIT:
            price = tick_data['bidPrice1'] + PRICE_UNIT
        else:
            if tick_data['bidVolume1'] > tick_data['askVolume1']:
                price = tick_data['bidPrice1'] + PRICE_UNIT
            else:
                price = tick_data['bidPrice1']

        if price != last_price:
            con.modify_order(order_id, context.current_contract, target_amount, style=LimitOrder(price))
            last_price = price
        sleep(10)

    if order_info['filled'] and context.timeout_flag is False:
        t.cancel()

    return

def s(context, data):
    """
    Called XXX.
    """
    if isin_tranding_hours() is False:
        print('%s: out of trading hour.' % (ctime()))
        return

    con = context.con
    client_id = context.con.client_id
    target_amt = -1*TARGET_AMOUNT
    # get bid data
    tick_data = context.tick_data
    # rt_price = context.rt_price
    # bidPrice = tick_data['bidPrice1']
    # askPrice = tick_data['askPrice1']
    # bidVolume = tick_data['bidVolume1']
    # askVolume = tick_data['askVolume1']

    # algo to cehck our bidding price
    spread = (tick_data['askPrice1'] - tick_data['bidPrice1'])
    if spread > PRICE_UNIT:
        price = tick_data['askPrice1'] - PRICE_UNIT
    else:
        if tick_data['bidVolume1'] > tick_data['askVolume1']:
            price = tick_data['askPrice1']
        else:
            price = tick_data['askPrice1'] - PRICE_UNIT

    # place limited order
    print('%s: placing order.... amount %d, price %f' % (ctime(), target_amt, price))
    order_id = con.order_amount(context.current_contract, target_amt, style=LimitOrder(price))
    last_price = price

    # wait for N sec and then check order status
    sleep(2)
    order_info = context.con.order_dict[(client_id, order_id)]
    print('%s: order filled? %s' % (ctime(), order_info['filled']))
    if order_info['filled']:
        return

    t = Timer(60, order_timeout, (context, data, order_id))
    context.timeout_flag = False
    t.start()

    while order_info['filled'] is False and context.timeout_flag is False:
        # update price
        spread = (tick_data['askPrice1'] - tick_data['bidPrice1'])
        if spread > PRICE_UNIT:
            price = tick_data['askPrice1'] - PRICE_UNIT
        else:
            if tick_data['bidVolume1'] > tick_data['askVolume1']:
                price = tick_data['askPrice1']
            else:
                price = tick_data['askPrice1'] - PRICE_UNIT

        if price != last_price:
            print('%s: modifying order.... amount %d, price %f' % (ctime(), target_amt, price))

            con.modify_order(order_id, context.current_contract, target_amt, style=LimitOrder(price))
            last_price = price
        sleep(10)

    if order_info['filled'] and context.timeout_flag is False:
        t.cancel()

    return


class DemoApp(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)

        # variables
        self.input_fn = None
        self.input_img = None

        # top level UI
        self.parent = parent
        self.parent.title("Trader Joe")
        self.pack(fill=BOTH, expand=1)
        style = Style()
        style.configure("TFrame", background="#333")

        # Menu bar
        menubar = Menu(self.parent)
        self.parent.config(menu=menubar)
        fileMenu = Menu(menubar)
        fileMenu.add_command(label="Open", command=self.open_file_handler)
        menubar.add_cascade(label="File", menu=fileMenu)

        #
        # Init the Price Chart
        # init_matplotlib()
        self.fig = Figure(figsize=(16, 6))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.parent)
        self.canvas.get_tk_widget().place(x=0, y=0)

        # TODO: how to setup min price unit
        self.fig.tight_layout(pad=2, h_pad=1, w_pad=2)               # This should be called after all axes have been added
        self.ax.grid(True)
        self.ax.set_autoscalex_on(False)      # turn off auto scale
        self.ax.set_autoscaley_on(False)      # turn off auto scale
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.xaxis.set_tick_params(top='off', direction='out', width=1)
        self.ax.yaxis.set_tick_params(right='off', direction='out', width=1)
        self.ax.set_ylim([10000, 10400])

        # Define time series (X)
        date_str = datetime.now().strftime('%Y%m%d')
        ts = pd.date_range(start=date_str+' 0900', end=date_str+' 1500', freq='T')
        self.price_chart_df = pd.DataFrame(np.nan, index=ts, columns=['Open', 'High', 'Low', 'Close', 'Volume'])
        # config X limits according to TS
        self.ax.set_xlim([ts.values[0], ts.values[-1]])
        self.ani = animation.FuncAnimation(self.fig, self.update_price_chart, frames=np.arange(100000),
                                           init_func=self.init_price_chart, interval=1*1000, repeat=True)

        # Buttons
        btn_con = Button(self, text='连接主机', command=self.button_connect_handler, width=16)
        btn_con.place(x=1, y=550)
        # Button - buy
        btn_discon = Button(self, text="断开连接", command=self.button_disconnect_handler, width=16)
        btn_discon.place(x=20*8, y=550)
        # Button - buy
        btn_buy = Button(self, text="买", command=self.button_buy_handler, width=16)
        btn_buy.place(x=20*16, y=550)
        # Button - sell
        btn_sell = Button(self, text="卖", command=self.button_sell_handler, width=16)
        btn_sell.place(x=20*24, y=550)
        # Button - sell
        btn_close = Button(self, text="平仓", command=self.button_close_handler, width=16)
        btn_close.place(x=20*32, y=550)

        # bind key
        self.bind_all("<Control-b>", self.key_buy_handler)
        self.bind_all("<Control-s>", self.key_sell_handler)
        self.bind_all("<Control-p>", self.button_close_handler)

        #
        self.parent.protocol("WM_DELETE_WINDOW", self.exit_handler)

        # Add txt box for system message output/displace
        Label(self, text='System Message', font='courier').place(x=1000, y=550)
        self.output_txtbox = ScrolledText(self.parent, width=30, height=10, font='courier')
        self.output_txtbox.place(x=1000, y=570)
        self.output_txtbox.insert('1.0', 'sample txt ouptput, %d\n' % (10))

    def open_file_handler(self):
        ftypes = [('Bitmap files', '*.bmp'), ('All files', '*')]
        dlg = tkFileDialog.Open(self.parent, filetypes=ftypes)
        self.input_fn = dlg.show()

        if self.input_fn != '':
            # Load image
            img = Image.open(self.input_fn)
            pic = ImageTk.PhotoImage(img)
            # display image
            self.input_label['image'] = pic
            self.input_img = pic

    def button_connect_handler(self):
        initialize(context)

        # Setup time related variables
        now = datetime.now()
        context.year = now.year
        context.month = now.month
        context.day = now.day

        # once connected to TWS, request hist price and copy to price_chart_df
        price_df = context.con.get_price_history(context.current_contract, datetime.now().strftime('%Y%m%d %H:%M:%S'), '2 D', 'minute')
        start = price_df.index[0]
        end   = price_df.index[-1]
        self.price_chart_df[start: end] = price_df[['Open', 'High', 'Low', 'Close', 'Volume']][start: end]

    def button_disconnect_handler(self):
        if context.con.connected:
            context.con.close()

    def button_buy_handler(self):
        threading.Thread(target = b, args=(context, data)).start()

    def button_sell_handler(self):
        threading.Thread(target = s, args=(context, data)).start()

    def button_close_handler(self):
        threading.Thread(target = c, args=(context, data)).start()

    def key_buy_handler(self, event):
        threading.Thread(target = b, args=(context, data)).start()

    def key_sell_handler(self, event):
        threading.Thread(target = s, args=(context, data)).start()

    def key_close_handler(self, event):
        threading.Thread(target = c, args=(context, data)).start()

    def exit_handler(self):
        if context.con.connected:
            context.con.close()
        self.parent.distroy()

    def init_price_chart(self):
        ''' Get price data from TWS and refresh (plot) price chart

        :return:
        '''
        # draw line
        df = self.price_chart_df
        if all(np.isnan(df['Close'].values)) is False:
            # refresh Y limits
            y_min = np.nanmin(df['Close'].values) + 15
            y_max = np.nanmax(df['Close'].values) + 15
            self.ax.set_ylim([y_min, y_max])

        self.price_chart_line, = self.ax.plot(self.price_chart_df.index.values, self.price_chart_df['Close'].values, color='blue')
        self.canvas.draw()

        return self.price_chart_line

    def update_price_chart(self, i):
        ''' Get price data from TWS and refresh (plot) price chart

        :return:
        '''
        # return if not connected to TWS yet
        if context.con is None:
            return self.init_price_chart()
        elif context.con.connected is False:
            return self.init_price_chart()
        elif isin_tranding_hours() is False:
            # TODO
            # if context.con.connected:
            #     price_df = context.con.get_price_history(context.current_contract, datetime.now().strftime('%Y%m%d %H:%M:%S'), '1 D', 'minute')
            #     start = price_df.index[0]
            #     end   = price_df.index[-1]
            #     self.price_chart_df[start: end] = price_df[['Open', 'High', 'Low', 'Close', 'Volume']][start: end]
            return self.init_price_chart()

        # get variables from context
        con = context.con
        fig = self.fig
        ax = self.ax
        canvas = self.canvas
        df = self.price_chart_df

        # Prep data
        data_header = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        chart_type = 'LINE' #'K'  # 'LINE'

        if len(context.rt_price) > 0:
            # TODO: Run-time error/bug in multi-thread enviroment; context.rt_price index and array length mismatch
            rt_df = pd.DataFrame(context.rt_price, columns=data_header)
            rt_df['Date'] = pd.to_datetime(rt_df['Date'], format='%Y%m%d %H:%M:%S')
            rt_df = rt_df.set_index('Date').sort_index()
            # resample rt_df price to min, and then copy to df
            rt_df_min = rt_df[['Open', 'High', 'Low', 'Close', 'Volume']].resample('T').last()
            start = rt_df_min.index[0]
            end   = rt_df_min.index[-1]
            df[start: end] = rt_df_min[start: end]

        if all(np.isnan(df['Close'].values)) is False:
            # refresh Y limits
            y_min = np.nanmin(df['Close'].values) * 0.997
            y_max = np.nanmax(df['Close'].values) * 1.003
            ax.set_ylim([y_min, y_max])
            #ax.xaxis.set_ticks([])
            #ax.yaxis.set_ticks([])

        # if chart_type == 'K':
        #     candlestick2_ochl(ax, df['Open'], df['Close'], df['High'], df['Low'], width=0.5,
        #                       colorup='g', colordown='r', alpha=0.75)
        self.price_chart_line.set_data(df.index.values, df['Close'].values)
        #self.ax.plot(self.price_chart_df.index.values, self.price_chart_df['Close'].values, color='blue')
        canvas.draw()

        return self.price_chart_line


def on_closing():
    if askokcancel("Quit", "Do you want to quit?"):
        if context.con is not None:
            if context.con.connected:
                context.con.close()
        root.destroy()


class IntraDayTsFormatter(Formatter):
    ''' Intra Day Time Series Formatter for matplotlib
    '''
    def __init__(self, dates, fmt='%H:%M:%S'):
        self.dates = dates
        self.fmt = fmt

    def __call__(self, x, pos=0):
        'Return the label for time x at position pos'
        ind = int(round(x))
        if ind >= len(self.dates) or ind < 0:
            return ''
        return self.dates[ind].strftime(self.fmt)


if __name__ == "__main__":
    root = Tk()
    ex = DemoApp(root)
    root.geometry("1200x680+30+30")
    root.protocol("WM_DELETE_WINDOW", on_closing)
    #root.resizable(0, 0)    # disable resize in x and y
    root.mainloop()


