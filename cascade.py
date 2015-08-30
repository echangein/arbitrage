#!/usr/bin/env python
#-*-coding:utf-8-*-

from kbrd import getch
import time, os, json
from spec import Spec

totalPrecision = 8
profitPrecision = 2
pair = 'ltc_usd'
cascadeFileName = 'cascade_trades'

profitPercent = 1.1
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
	
if os.path.isfile(cascadeFileName): #warning! not chek pair and another params
	file = open(cascadeFileName, 'r+')
	cascade = json.load(file)
	file.close()
	print('Cascade is loading')
else:
	cascade = engine.createCascade()
	file = open(cascadeFileName, 'w+')
	file.write(json.dumps(cascade))
	file.close()
	print('Cascade is generated')

engine.printCascade(cascade)

cascade = engine.checkOrders(cascade)

if engine.inWork(cascade):
	print('\nIn work')
else:
	print('\nJust waiting')
	profit = engine.getProfit(cascade)
	if not profit is False:
		engine.cancelOrders(cascade)
		print('\nCascade COMPLETE.')
		print('Profit: {0}'.format(profit))
		engine.printCascade(cascade)
		if os.path.isfile(cascadeFileName):
			os.remove(cascadeFileName)
		quit()
	
	if engine.needRestart(cascade):
		print('\nPrice change. Generate new cascade')
		engine.cancelOrders(cascade)
		if os.path.isfile(cascadeFileName):
			os.remove(cascadeFileName)
		cascade = engine.createCascade()
		file = open(cascadeFileName, 'w+')
		file.write(json.dumps(cascade))
		file.close()

cascade = engine.createOrders(cascade)

file = open(cascadeFileName, 'w+')
file.write(json.dumps(cascade))
file.close()
	
print('Repeat after few seconds.')
