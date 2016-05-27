#!/usr/bin/env python
#-*-coding:utf-8-*-

from kbrd import getch
import time, os, json, sys

from btce import Btce
from speculator import Speculator

keyFile = 'secret.key'
dirname, filename = os.path.split(os.path.abspath(__file__))
keyFileName = dirname + '/../' + keyFile
f = open(keyFileName, 'r')
key = f.readline().strip()
secret = f.readline().strip()
f.close()

stat = Speculator()
exchange = Btce(key, secret)

#print(exchange.getConditions())

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
