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

# ================== define cascade params ================== #
configFile = 'ltc_rur.cfg'
keyFile = 'ltc_rur.key'
for key, val in [s.split('=') for s in sys.argv[1:]]:
	if key == 'conf':
		configFile = val
	if key == 'key':
		keyFile = val

cascadeFileName = configFile  + '_' + keyFile + '.csc'
statusFileName = configFile  + '_' + keyFile + '.sts'
# ================== define cascade params ================== #

if isExistsCascadeFile(cascadeFileName):
	cascadeStruct = loadCascadeFile(cascadeFileName)
	sigma.setParams(cascadeStruct)
else
	cascadeStruct = sigma.createCascade()
	
cascadeStruct, error = sigma.checkOrders(cascadeStruct) #checkOrdersStatus
if error:
	print('error with checkOrders in init: {0}'.format(error)) #reportCheckOrdersStatusError()
	saveCascadeFile(cascadeFileName, cascadeStruct)
	quit()

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
	if sigma.hasPartialExecution(cascadeStruct): # need check executed next buy order
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