#!/usr/bin/env python
#-*-coding:utf-8-*-

import time, os, json, sys, datetime

dirName, ownFileName = os.path.split(os.path.abspath(__file__))
startDT = int(time.time())

def getMarkFileName():
	return dirName + '/../' + os.path.splitext(ownFileName)[0] + '.mark'

def hasExecutedScript():
	return os.path.isfile(getMarkFileName())

def isOvertime():
	return False

def markStartExecution():
	file = open(getMarkFileName(), 'w+')
	file.write(json.dumps(startDT))
	file.close()

	print('markStartExecution {0}'.format(startDT))
	return


#print('dirName ' + dirName)
#print('ownFileName ' + ownFileName)


if hasExecutedScript():
	if isOvertime():
		print('overtime for ' + ownFileName + 'script')
	quit()	

markStartExecution()

print(os.path.splitext(ownFileName)[0] + ' body') # 

quit()




checkExecutedScript()

import config
from spec import Spec
import os.path

key = None
secret = None

if os.path.isfile('../arbitrage.key'):
	f = open('../arbitrage.key', 'r')
	key = f.readline().strip()
	secret = f.readline().strip()
	f.close()

curSite = Spec(key, secret, True) #silent mode

if not curSite.checkConnection():
	quit()

if not curSite.loadTradeConditions():
	quit()
