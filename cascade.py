#!/usr/bin/env python
#-*-coding:utf-8-*-

from kbrd import getch
import time, os, json, sys
#from spec import Spec

totalPrecision = 8
profitPrecision = 2
pair = 'ltc_usd'
silent = False

profitPercent = 1.1
startPercent = 1
deepPercent = 15
totalInvest = 5.2
activeOrdersCount = 5
allowRevers = False
allowStop = False

import config
#from spec import Spec
from cascade import Cascade
import os.path

keyFile = 'secrets.txt_bot1'
#cascadeFile = 'trades_ltc_usd'
#statusFile = 'status'
configFile = 'none'

for key, val in [s.split('=') for s in sys.argv[1:]]:
	if key == 'conf':
		configFile = val
	if key == 'key':
		keyFile = val

cascadeFile = 'trades_' + configFile  + '_' + keyFile
statusFile = 'status_' + configFile  + '_' + keyFile

"""
if len(sys.argv) > 1:
	if sys.argv[1] == 'crone':
		silent = True
"""

dirname, filename = os.path.split(os.path.abspath(__file__))

cascadeFileName = dirname + '/../' + cascadeFile
keyFileName = dirname + '/../' + keyFile
statusFileName = dirname + '/../' + statusFile
configFileName = dirname + '/../' + configFile

# set config from file

if os.path.isfile(configFileName):
	file = open(configFileName, 'r+')
	config = json.load(file)
	file.close()
	if 'profitPercent' in config:
		profitPercent = config['profitPercent']
	if 'startPercent' in config:
		startPercent = config['startPercent']
	if 'deepPercent' in config:
		deepPercent = config['deepPercent']
	if 'totalInvest' in config:
		totalInvest = config['totalInvest']
	if 'pair' in config:
		pair = config['pair']
	if 'activeOrdersCount' in config:
		activeOrdersCount = config['activeOrdersCount']
	if 'profitPrecision' in config:
		profitPrecision = config['profitPrecision']
	if 'silent' in config:
		silent = config['silent']
	if 'allowRevers' in config:
		allowRevers = config['allowRevers']
	if 'allowStop' in config:
		allowStop = config['allowStop']
	
# set config from file

def getPrevStat():
	ret = 'waiting'
	if os.path.isfile(statusFileName):
		f = open(statusFileName, 'r+')
		ret = f.readline().strip()
		f.close()
	return ret

def setPrevStat(val):
	f = open(statusFileName, 'w+')
	f.write(val)
	f.close()

if getPrevStat() == 'stopped':
	quit()
	
key = None
secret = None

if os.path.isfile(keyFileName):
	f = open(keyFileName, 'r')
	key = f.readline().strip()
	secret = f.readline().strip()
	f.close()

engine = Cascade(key, secret, silent)
engine.setPair(pair)

engine.setProfitPercent(profitPercent)
engine.setStartPercent(startPercent)
engine.setDeepPercent(deepPercent)
engine.setTotalInvest(totalInvest)

engine.setProfitPrecision(profitPrecision)
engine.setActiveOrdersCount(activeOrdersCount)
engine.setAllowRevers(allowRevers)

if not silent:
	print('\ncur Pair:\t{0}'.format(pair))
	
if os.path.isfile(cascadeFileName): #warning! not chek pair and another params
	file = open(cascadeFileName, 'r+')
	cascade = json.load(file)
	file.close()
	if not silent:
		print('Cascade is loading')
else:
	cascade = engine.createCascade()
	file = open(cascadeFileName, 'w+')
	file.write(json.dumps(cascade))
	file.close()
	if not silent:
		print('Cascade is generated')

if not silent:
	engine.printCascade(cascade)

cascade = engine.checkOrders(cascade)

if engine.inWork(cascade):
	if not silent:
		print('\nIn work')
	if getPrevStat() <> 'inWork':
		print('In work')
		engine.printCascade(cascade)
	setPrevStat('inWork')

	if engine.needReverse(cascade):
		volume, orderId = engine.getReverseParams(cascade)
		if engine.saveCascade(cascade, cascadeFileName):
			cascade = engine.createCascade(volume, orderId)
			setPrevStat('waiting')
else:
	setPrevStat('waiting')
	if not silent:
		print('\nJust waiting')
	profit = engine.getProfit(cascade)
	if not profit is False:
		engine.cancelOrders(cascade)
		print('\nCascade COMPLETE.')
		print('Profit: {0}'.format(profit))
		engine.printCascade(cascade)
		
		if os.path.isfile(cascadeFileName):
			os.remove(cascadeFileName)
		if engine.isRevers(cascade):
			engine.restoreCascade(cascade, cascadeFileName)
			setPrevStat('inWork')
		elif allowStop:
			setPrevStat('stopped')
		quit()
	
	if engine.needRestart(cascade):
		if not silent:
			print('\nPrice change. Generate new cascade')
		engine.cancelOrders(cascade)
		if os.path.isfile(cascadeFileName):
			os.remove(cascadeFileName)
		
		if engine.isRevers(cascade):
			volume, orderId = engine.getReverseParams(cascade)
			cascade = engine.createCascade(volume, orderId)
		else:
			cascade = engine.createCascade()
		
		file = open(cascadeFileName, 'w+')
		file.write(json.dumps(cascade))
		file.close()

cascade = engine.createOrders(cascade)

file = open(cascadeFileName, 'w+')
file.write(json.dumps(cascade))
file.close()

if not silent:	
	print('Repeat after few seconds.')
