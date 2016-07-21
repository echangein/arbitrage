#!/usr/bin/env python
#-*-coding:utf-8-*-

from kbrd import getch
import time, os, json, sys, datetime

from sigma import Sigma

dirName, ownFileName = os.path.split(os.path.abspath(__file__))
configFileName = dirName + '/../conf.cfg'
if os.path.isfile(configFileName):
	file = open(configFileName, 'r+')
	config = json.load(file)
	file.close()
	if 'db' in config:
		db = config['db']
	if 'user' in config:
		user = config['user']
	if 'pswd' in config:
		pswd = config['pswd']


pair = 'ltc_usd'

sigma = Sigma(None, None, pair, db, user, pswd)
sigma.invest = 16.93
sigma.totalIndent = 3.0
sigma.startIndent = 0.2
sigma.minProfitPercent = 1.1
sigma.incInvest = 5.0

cascade = sigma.createCascade('sell')
sigma.printCascade(cascade)

cou = 0
for investOrder in cascade['investOrders']:
	investOrder['orderId'] = 666
	if cou > len(cascade['investOrders']) / 2:
		cascade['profitOrders'][cou]['orderId'] = 666
		cascade['profitOrders'][cou]['status'] = 1
		break
	cou += 1

sigma.reportProfit(cascade)

quit()


print('\n\rincInvest = 1.0')
cascade = sigma.createCascade()
sigma.printCascade(cascade)


print('\n\rshiftOrders')
cascade = sigma.shiftOrders(cascade)
sigma.printCascade(cascade)