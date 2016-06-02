#!/usr/bin/env python
#-*-coding:utf-8-*-

from kbrd import getch
import time, os, json, sys, datetime

from btce import Btce
from speculator import Speculator

stat = Speculator()
exchange = Btce()

dt = int(time.time())
print(dt, datetime.datetime.fromtimestamp(dt).strftime('%Y.%m.%d %H:%M:%S'))

pair = raw_input('enter pair: ')
sigma, avg = stat.getSigmaAndAvg(pair)
if not sigma:
	print(avg)
	quit()


res, error = exchange.getTicker([pair])
if not res:
	print(error)
	quit()
	
print('{2} from {0} to {1}'.format(res[pair]['last'] - 3 * sigma, res[pair]['last'] + 3 * sigma, pair))
print('deep 3 sigma percent: {0}'.format(3 * sigma / res[pair]['last'] * 100))

quit()

from sigma import Sigma

pair = 'btc_rur'

sigma = Sigma(None, None, pair)
sigma.invest = 9000.0
sigma.totalIndent = 3.0
sigma.startIndent = 0.5
sigma.minProfitPercent = 1

cascade = sigma.createCascade()
sigma.printCascade(cascade)

# 0 - active, 1 - excuted, 2 - canceled, 3 - canceled but partial executed
cou = 0
for order in cascade['investOrders']:
	if cou < 5:
		order['orderId'] = 666
		order['status'] = 1
	cou += 1
#cascade['investOrders'][5]['orderId'] = 666
#cascade['investOrders'][5]['status'] = 0
cascade['profitOrders'][4]['orderId'] = 666
cascade['profitOrders'][4]['status'] = 1

sigma.reportProfit(cascade)

quit()


# set in work
"""
for order in cascade['investOrders']:
	order['orderId'] = 666
	order['status'] = 1
"""
cascade['investOrders'][0]['orderId'] = 666
cascade['investOrders'][0]['status'] = 1
#cascade['investOrders'][1]['orderId'] = 666
#cascade['investOrders'][1]['status'] = 1
# set in work

print('inv: {0} prof: {1}'.format(len(cascade['investOrders']), len(cascade['profitOrders'])))

quit()


pair = 'ltc_rur'
silent = False

profitPercent = 1.2
startPercent = 0.9
deepPercent = 19
totalInvest = 5000
activeOrdersCount = 5

profitPrecision = 4

import config
from cascade import Cascade
import os.path, json


cascadeFile = 'trades_btc_usd_btc_usd_key'

dirname, filename = os.path.split(os.path.abspath(__file__))
cascadeFileName = dirname + '/../' + cascadeFile
cascadeFileName = dirname + '/../bool'

key = None
secret = None

engine = Cascade(key, secret, silent)

engine.setPair(pair)

engine.setProfitPercent(profitPercent)
engine.setStartPercent(startPercent)
engine.setDeepPercent(deepPercent)
engine.setTotalInvest(totalInvest)
engine.setActiveOrdersCount(activeOrdersCount)

engine.setProfitPrecision(profitPrecision)

cascade = engine.createCascade(17.99, 666) #43.93, 666
engine.printCascade(cascade)
