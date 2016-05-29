#!/usr/bin/env python
#-*-coding:utf-8-*-

from kbrd import getch
import time, os, json, sys, datetime

import requests
def fileno(self):
    return self.socket.fileno()


def close(self):
    return self.connection.shutdown()


requests.pyopenssl.WrappedSocket.close = close
requests.pyopenssl.WrappedSocket.fileno = fileno

# look here http://stackoverflow.com/questions/33972671/downloading-https-pages-with-urllib-error14077438ssl-routinesssl23-get-serve

url = 'https://speculator.in/ax/stat/?pair=btc_rur'
print(requests.get(url))

quit()

from btce import Btce
from speculator import Speculator
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
sigma.minProfitPercent = 1.0

cascade = sigma.createCascade()
sigma.printCascade(cascade)

sigma.setParams(cascade)
cascade, error = sigma.checkOrders(cascade)

print(cascade, error)

quit()


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
