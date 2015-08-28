#!/usr/bin/env python
#-*-coding:utf-8-*-

from kbrd import getch
import time, os, json
from spec import Spec

totalPrecision = 8
profitPrecision = 2
pair = 'btc_usd'

profitPercent = 2
deepPercent = 15
totalInvest = 5

import config
from spec import Spec
from cascade import Cascade
import os.path

key = None
secret = None

if os.path.isfile('../secrets.txt_bot1'):
	f = open('../secrets.txt_bot1', 'r')
	key = f.readline().strip()
	secret = f.readline().strip()
	f.close()

engine = Cascade(key, secret)
engine.setPair(pair)

engine.setProfitPercent(profitPercent)
engine.setDeepPercent(deepPercent)
engine.setTotalInvest(totalInvest)

print('\ncur Pair:\t{0}'.format(pair))
	
if os.path.isfile('cascade_trades'): #warning! not chek pair and another params
	file = open('cascade_trades', 'r+')
	cascade = json.load(file)
	file.close()
	print('Cascade is loading')
else:
	cascade = engine.createCascade()
	print('Cascade is generated')

"""	
cascade = engine.createOrders(cascade)
engine.setCascade(cascade)
engine.checkStatus()
"""

engine.printCascade(cascade)
quit()

file = open('cascade_trades', 'w+')
file.write(json.dumps(cascade))
file.close()

if engine.inWork():
	print('\nIn work')
	if engine.checkStatus():
		engine.cancelOrders()
		print('\nCascade COMPLETE.')
		print('Profit: {0}'.format(engine.getProfit()))
		quit()
	engine.createOrders()
	cascade = engine.getCascade()
	file = open('cascade_trades', 'w+')
	file.write(json.dumps(cascade))
	file.close()
	print('Repeat after few seconds.')
else:
	print('\nJust waiting')
	if engine.checkLastPrice():
		print('\nPrice change. Generate new cascade')
		engine.cancelOrders()
		if os.path.isfile('cascade_trades'):
			os.remove('cascade_trades')
		cascade = engine.createCascade()
		file = open('cascade_trades', 'w+')
		file.write(json.dumps(cascade))
		file.close()
	engine.createOrders()
	print('Repeat after few seconds.')


"""	
orderId = 753455999
res = curSite.getOrderStatus(orderId)
if res is False:
	print(curSite.getLastErrorMessage())
	quit()

print('OrderStatus: {0}'.format(res))
"""
