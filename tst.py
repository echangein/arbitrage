#!/usr/bin/env python
#-*-coding:utf-8-*-

from kbrd import getch
import time, os, json, sys

from interface import Interface

key = '2ZBRTHMR-VCMKM1BA-W1IX3TL8-4UVRYGJQ-ZIC6T51Y'
secret = 'bf0c5be346ea2678e1b8642be0de22faf60569493cdab4dc6eb3d0574d262b64'

inter = Interface(key, secret)
res = inter.sendPost({'method': 'getInfo'})
print(res)
print(inter.lastErrorMessage, inter.lastResult)
#if not res:
#			self.lastErrorMessage = self.int.getLastErrorMessage()
#			return False
#quit()
"""
# new test connection
import httplib

headers = {"Content-type": "application/x-www-form-urlencoded"}
conn = httplib.HTTPSConnection("btc-e.com")
conn.request("GET", "/api/3/info", {}, headers)
response = conn.getresponse()


print response.status, response.reason
print json.load(response)

quit()
"""

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

key = 'VG4PRAAN-12QORIZE-KZCLUQY8-M1EQUY0Y-QH756KNR'
secret = '75a758d5b16835c92fdda55deb19ff0e1f256c15f27df7fa2be9d8de62524a9e'

engine = Cascade(key, secret, silent)

engine.setPair(pair)
#cancel_order(968200187, 17)
print(engine.spec.checkAmount(100, 'usd'))

quit()
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
"""
file = open(cascadeFileName, 'w+')
file.write(json.dumps(True))
file.close()
"""

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
