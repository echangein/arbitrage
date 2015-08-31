#!/usr/bin/env python
#-*-coding:utf-8-*-

from kbrd import getch
import time, os, json, sys
from spec import Spec

totalPrecision = 8
profitPrecision = 2
pair = 'ltc_usd'
silent = False

if len(sys.argv) > 1:
	if sys.argv[1] == 'crone'
		silent = True

profitPercent = 1.1
deepPercent = 15
totalInvest = 5

import config
from spec import Spec
from cascade import Cascade
import os.path

keyFile = '/../secrets.txt_bot1'
cascadeFile = '/../trades_ltc_usd'
statusFile = '/../status'

key = None
secret = None

dirname, filename = os.path.split(os.path.abspath(__file__))

cascadeFileName = dirname + cascadeFile
keyFileName = dirname + keyFile
statusFileName = dirname + statusFile

if os.path.isfile(keyFileName):
	f = open(keyFileName, 'r')
	key = f.readline().strip()
	secret = f.readline().strip()
	f.close()

engine = Cascade(key, secret, silent)
engine.setPair(pair)

engine.setProfitPercent(profitPercent)
engine.setDeepPercent(deepPercent)
engine.setTotalInvest(totalInvest)

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

engine.printCascade(cascade)

cascade = engine.checkOrders(cascade)

if engine.inWork(cascade):
	if not silent:
		print('\nIn work')
else:
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
		quit()
	
	if engine.needRestart(cascade):
		if not silent:
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

if not silent:	
	print('Repeat after few seconds.')