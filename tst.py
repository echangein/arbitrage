#!/usr/bin/env python
#-*-coding:utf-8-*-

from kbrd import getch
import time, os, json, sys
#from spec import Spec


pair = 'ltc_btc'
silent = False

profitPercent = 1.1
startPercent = 1
deepPercent = 18
totalInvest = 45.5
activeOrdersCount = 5

profitPrecision = 2

import config
#from spec import Spec
from cascade import Cascade
import os.path

cascadeFile = 'trades_btc_rur_btc_rur_key'
#cascadeFile = 'trades_btc_usd_btc_usd_key'
#cascadeFile = 'trades_ltc_btc_ltc_btc_key'
#cascadeFile = 'trades_ltc_rur_rur'
#cascadeFile = 'trades_ltc_usd_usd'

dirname, filename = os.path.split(os.path.abspath(__file__))
cascadeFileName = dirname + '/../' + cascadeFile

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

#cascade = engine.createCascade(17.99258339, 666) #

#print(cascade)
#print(cascade[0]['sellOrder']['operationAmount'])

file = open(cascadeFileName, 'r+')
cascade = json.load(file)
file.close()


engine.printCascade(cascade)

if engine.needReverse(cascade):
	print('need Reverse')
else:
	print('still wait')

#engine.needReverse(cascade)	
	
if len(cascade) > 0 and 'options' in cascade[0]:
	print('cascade is revers')
else:
	print('cascade is normal')