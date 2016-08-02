#!/usr/bin/env python
#-*-coding:utf-8-*-

configFileName = raw_input('enter config file name: ')
keyFileName = raw_input('enter key file name: ')

import time, os, json, sys

dirName, ownFileName = os.path.split(os.path.abspath(__file__))

def isExistsFile(fileName = None):
	return os.path.isfile(dirName + '/../' + fileName)

if not isExistsFile(configFileName):
	print('config file: {0} not found'.format(configFileName))
	quit()

if not isExistsFile(keyFileName):
	print('key file: {0} not found'.format(keyFileName))
	quit()

cascadeFileName = configFileName + '_' + keyFileName + '.csc'

if not isExistsFile(cascadeFileName):
	print('cascade file: {0} not found'.format(cascadeFileName))
	quit()
	
def loadCascadeFile(fileName = None):
	file = open(dirName + '/../' + fileName, 'r+')
	ret = json.load(file)
	file.close()
	return ret
	
def saveCascadeFile(fileName = None, cascadeStruct = None):
	file = open(dirName + '/../' + fileName, 'w+')
	file.write(json.dumps(cascadeStruct))
	file.close()
	
from sigma import Sigma

cascade = loadCascadeFile(cascadeFileName)

# ================== define cascade params ================== #
if isExistsFile(configFileName):
	file = open(dirName + '/../' + configFileName, 'r+')
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
	incInvest = 0.0
	if 'incInvest' in config:
		incInvest = config['incInvest']
# ================== define cascade params ================== #


key = None
secret = None

cfgFileName = dirName + '/../conf.cfg'
if os.path.isfile(cfgFileName):
	file = open(cfgFileName, 'r+')
	config = json.load(file)
	file.close()
	if 'db' in config:
		db = config['db']
	if 'user' in config:
		user = config['user']
	if 'pswd' in config:
		pswd = config['pswd']

sigma = Sigma(key, secret, pair, db, user, pswd)

sigma.invest = invest
sigma.startIndent = startIndent
sigma.totalIndent = totalIndent
sigma.minProfitPercent = minProfitPercent
sigma.incInvest = incInvest

sigma.printCascade(cascade)
#print(cascade['investOrders'][-1])

cascade = sigma.incCascade(cascade)
sigma.printCascade(cascade)
saveCascadeFile(cascadeFileName, cascade)