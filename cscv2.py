#!/usr/bin/env python
#-*-coding:utf-8-*-

import time, os, json, sys

dirName, ownFileName = os.path.split(os.path.abspath(__file__))

def isExistsCascadeFile(fileName = None):
	return os.path.isfile(dirName + '/../' + fileName)

def loadCascadeFile(fileName = None):
	file = open(dirName + '/../' + fileName, 'r+')
	ret = json.load(file)
	file.close()
	return ret
	
def saveCascadeFile(fileName = None, cascadeStruct = None):
	file = open(dirName + '/../' + fileName, 'w+')
	file.write(json.dumps(cascadeStruct))
	file.close()

def removeCascadeFile(fileName = None):
	os.remove(dirName + '/../' + fileName)

def getStat(fileName = None):
	statusFileName = dirName + '/../' + fileName
	ret = 'waiting'
	if os.path.isfile(statusFileName):
		f = open(statusFileName, 'r+')
		ret = f.readline().strip()
		f.close()
	return ret

def setStat(fileName = None, val = 'waiting'):
	statusFileName = dirName + '/../' + fileName
	f = open(statusFileName, 'w+')
	f.write(val)
	f.close()

from sigma import Sigma
	
# ================== define cascade params ================== #
configFile = 'ltc_rur.cfg'
keyFile = 'ltc_rur.key'
for key, val in [s.split('=') for s in sys.argv[1:]]:
	if key == 'conf':
		configFile = val
	if key == 'key':
		keyFile = val

cascadeFileName = configFile + '_' + keyFile + '.csc'
statusFileName = configFile + '_' + keyFile + '.sts'

keyFileName = dirName + '/../' + keyFile
configFileName = dirName + '/../' + configFile

if os.path.isfile(configFileName):
	file = open(configFileName, 'r+')
	config = json.load(file)
	file.close()
	if 'pair' in config:
		pair = config['pair']
	if 'invest' in config:
		invest = config['invest']
	if 'startIndent' in config:
		startIndent = config['startIndent']
	if 'totalIndent' in config:
		totalIndent = config['totalIndent']
	if 'minProfitPercent' in config:
		minProfitPercent = config['minProfitPercent']
# ================== define cascade params ================== #

key = None
secret = None

if os.path.isfile(keyFileName):
	f = open(keyFileName, 'r')
	key = f.readline().strip()
	secret = f.readline().strip()
	f.close()

sigma = Sigma(key, secret, pair)

sigma.invest = invest
sigma.startIndent = startIndent
sigma.totalIndent = totalIndent
sigma.minProfitPercent = minProfitPercent

if isExistsCascadeFile(cascadeFileName):
	cascadeStruct = loadCascadeFile(cascadeFileName)
	sigma.setParams(cascadeStruct)
else:
	cascadeStruct = sigma.createCascade()
	setStat(statusFileName, 'waiting')
	
cascadeStruct, error = sigma.checkOrders(cascadeStruct) #checkOrdersStatus
if error:
	print('error with checkOrders in init: {0}'.format(error)) #reportCheckOrdersStatusError()
	saveCascadeFile(cascadeFileName, cascadeStruct)
	quit()

# ================== check inWork status ================== #
if sigma.inWork(cascadeStruct):
	if getStat(statusFileName) <> 'inWork':
		sigma.printCascade(cascadeStruct)
		setStat(statusFileName, 'inWork')
# ================== check inWork status ================== #

# ================== restart cascade ================== #
if not sigma.inWork(cascadeStruct) and sigma.needRestart(cascadeStruct):
	cascadeStruct, error = sigma.cancelOrders(cascadeStruct)
	if error:
		print('error with cancelOrders in restart cascade: {0}'.format(error)) #reportCancelOrdersError()
		saveCascadeFile(cascadeFileName, cascadeStruct)
		quit()
		
	cascadeStruct = sigma.createCascade()
	cascadeStruct, error = sigma.checkOrders(cascadeStruct) #checkOrdersStatus
	if error:
		print('error with checkOrders in restart: {0}'.format(error)) #reportCheckOrdersStatusError()
		saveCascadeFile(cascadeFileName, cascadeStruct)
		quit()
# ================== restart cascade ================== #

# ================== cascade get profit ================== #
if sigma.hasProfit(cascadeStruct): #sell order complete
	sigma.reportProfit(cascadeStruct)
	sigma.printCascade(cascadeStruct)
	if sigma.hasPartialExecution(cascadeStruct): # need check executed next buy order
		print('partial execution')
		cascadeStruct = sigma.resizeAfterProfit(cascadeStruct)
		sigma.setParams(cascadeStruct)
	else:
		cascadeStruct, error = sigma.cancelOrders(cascadeStruct)
		if error:
			print('error with cancelOrders in cascade get profit: {0}'.format(error)) #reportCancelOrdersError()
			saveCascadeFile(cascadeFileName, cascadeStruct)
			quit()
		removeCascadeFile(cascadeFileName)
		quit()
#		if hasParnet(cascadeStruct): # for reverse
#			restoreParent(cascadeStruct)
#			quit()
# ================== cascade get profit ================== #

# ================== create revers cascade ================== #
# ================== create revers cascade ================== #

# ================== create order sequence ================== #
cascadeStruct, error = sigma.createOrders(cascadeStruct)
if error:
	print('error with createOrders in create order sequence: {0}'.format(error))
cascadeStruct = sigma.shiftOrders(cascadeStruct)

cascadeStruct, error = sigma.moveProfitOrder(cascadeStruct)
if error:
	print('error with moveProfitOrder in create order sequence: {0}'.format(error)) #reportMoveProfitOrderError()
# ================== create order sequence ================== #

saveCascadeFile(cascadeFileName, cascadeStruct)