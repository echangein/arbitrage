#!/usr/bin/env python
#-*-coding:utf-8-*-

from kbrd import getch
import time, os, json, sys, datetime

from sigma import Sigma

keyFile = 'secret.key'
dirname, filename = os.path.split(os.path.abspath(__file__))
keyFileName = dirname + '/../' + keyFile
f = open(keyFileName, 'r')
key = f.readline().strip()
secret = f.readline().strip()
f.close()

pair = 'btc_rur'

sigma = Sigma(key, secret, pair)
sigma.invest = 9000.0
sigma.totalIndent = 3.0
sigma.startIndent = 0.5
sigma.minProfitPercent = 1.0

cascade = sigma.createCascade()
sigma.printCascade(cascade)

# 0 - active, 1 - excuted, 2 - canceled, 3 - canceled but partial executed

cou = 0
for order in cascade['investOrders']:
	if cou < 5:
		order['orderId'] = 666
		order['status'] = 0
	cou += 1
#cascade['investOrders'][0]['orderId'] = 666
#cascade['investOrders'][0]['status'] = 0

key = 0
while key != 27:
	cascade = sigma.shiftOrders(cascade)
	sigma.printCascade(cascade)
	key = ord(getch())
	
quit()

#profitIdx = len(cascade['profitOrders']) / 2

#print('profitIdx: {0}'.format(profitIdx))

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

#cascade, error = sigma.moveProfitOrder(cascade)
#print(cascade)
#sigma.printCascade(cascade)
#print('inv: {0} prof: {1}'.format(len(cascade['investOrders']), len(cascade['profitOrders'])))

quit()

from btce import Btce
from speculator import Speculator

stat = Speculator()
exchange = Btce(key, secret)

#print(exchange.getConditions())

dt = int(time.time())
print(dt, datetime.datetime.fromtimestamp(dt).strftime('%Y.%m.%d %H:%M:%S'))

#time.gmtime(), time.strftime('%Y.%m.%d %H:%M:%S', time.gmtime())

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
