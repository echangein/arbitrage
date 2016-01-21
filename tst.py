#!/usr/bin/env python
#-*-coding:utf-8-*-

from kbrd import getch
import time, os, json, sys
#from spec import Spec


pair = 'ltc_btc'
silent = False

profitPercent = 1
startPercent = 0.8
deepPercent = 22
totalInvest = 0.4295
activeOrdersCount = 5

profitPrecision = 4

import config
#from spec import Spec
from cascade import Cascade
import os.path, json

cascadeFile = 'trades_btc_rur_btc_rur_key'
cascadeFile = 'trades_btc_usd_btc_usd_key'
cascadeFile = 'trades_ltc_btc_ltc_btc_key'
#cascadeFile = 'trades_ltc_rur_rur'
#cascadeFile = 'trades_ltc_usd_usd'

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

#cascade = engine.createCascade() #43, 666

#print(engine.getProfit(cascade))
#print(cascade)
#print(cascade[0]['sellOrder']['operationAmount'])

"""
file = open(cascadeFileName, 'r+')
cascade = json.load(file)
file.close()

engine.printCascade(cascade)

if engine.isRevers(cascade):
	print('restore cascade')
	os.remove(cascadeFileName)
	engine.restoreCascade(cascade, cascadeFileName)
	quit()
else:
	if engine.needReverse(cascade):
		print('create revers')
		volume, orderId = engine.getReverseParams(cascade)
		if engine.saveCascade(cascade, cascadeFileName):
			cascade = engine.createCascade(volume, orderId)
		else:
			print('save cascade fail')

file = open(cascadeFileName, 'w+')
file.write(json.dumps(cascade))
file.close()
"""

file = open(cascadeFileName, 'w+')
file.write(json.dumps(True))
file.close()


"""
if engine.needReverse(cascade):
	print('need Reverse')
	vol, id = engine.getReverseParams(cascade)
	cascade = engine.createCascade(vol, id)
	#print(engine.getReverseParams())
else:
	print('still wait')
	
if len(cascade) > 0 and 'options' in cascade[0]:
	print('cascade is revers')
else:
	print('cascade is normal')
"""