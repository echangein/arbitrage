#-*-coding:utf-8-*-

from kbrd import getch
import time, os, json
from spec import Spec

totalPrecision = 8
profitPrecision = 2
pair = 'btc_usd'

profitPercent = 1
deepPercent = 10
totalInvest = 5

def printCascade(cascade):
	invested = 0
	for item in cascade:
		invested += round(item['buyOrder']['rate'] * item['buyOrder']['amount'], totalPrecision)
		accepted = round(item['sellOrder']['rate'] * item['sellOrder']['amount'] * (100 - fee) / 100, totalPrecision)
		profit = round(accepted - invested, profitPrecision)
		print('{0[stage]:>3} buy {1[amount]:<12}@ {1[rate]:<12}inv: {3:<12}sell: {2[amount]:<12}@ {2[rate]:<12}accp: {4:<14} {5:<2}'.format(item, item['buyOrder'], item['sellOrder'], invested, accepted, profit))

import config
from spec import Spec
import os.path

key = None
secret = None

if os.path.isfile('../secrets.txt_bot1'):
	f = open('../secrets.txt_bot1', 'r')
	key = f.readline().strip()
	secret = f.readline().strip()
	f.close()

curSite = Spec(key, secret)

if not curSite.checkConnection():
	quit()


	
if not curSite.loadTradeConditions():
	quit()

if not curSite.loadTickers([pair]):
	quit()

lastPrice = curSite.tickers[pair]['last']
pricePrecision = curSite.pairs[pair]['decimal_places']
minAmount = curSite.pairs[pair]['min_amount']
fee = curSite.pairs[pair]['fee']

print('\nSelected pair:\t{0}'.format(pair))
print('lastPrice:\t{0}\n'.format(lastPrice))

startPrice = round(lastPrice * (100 - profitPercent) / 100, pricePrecision)
endPrice = round(startPrice * (100 - deepPercent) / 100, pricePrecision)
priceLength = startPrice - endPrice
investDensity = round((startPrice - endPrice) / totalInvest, totalPrecision)
investQuant = round(startPrice * minAmount * (100 + 2 * fee) / 100, pricePrecision)

priceStep = round(investQuant * investDensity, pricePrecision)
if priceStep == 0:
	priceStep = 10 ** -pricePrecision
	
if not os.path.isfile('cascade'):	
	print('startPrice:\t{0}'.format(startPrice))
	print('endPrice:\t{0}'.format(endPrice))
	print('\nPrice lenght:\t{0}'.format(priceLength))
	print('investDensity:\t{0}'.format(investDensity))
	print('investQuant:\t{0}'.format(investQuant))
	print('priceStep:\t{0}\n'.format(priceStep))

	curInvest = totalInvest
	curPrice = startPrice
	invested = 0
	stage = 0
	sellAmount = 0
	cascade = []
	while curInvest >= investQuant:
		curAmount = round(investQuant / curPrice, totalPrecision)
		if curAmount < minAmount:
			curAmount = minAmount
			
		invested += investQuant
		sellAmount += round(curAmount * (100 - fee) / 100, totalPrecision)
		sellPrice = round(invested / sellAmount * (100 + profitPercent) / 100, pricePrecision)
		cascade.append({'stage': stage, 'buyOrder': {'pair': pair, 'type': 'buy', 'rate': curPrice, 'amount': curAmount}, 'sellOrder': {'pair': pair, 'type': 'sell', 'rate': sellPrice, 'amount': sellAmount}})
		stage += 1
		curInvest -= investQuant
		curPrice -= priceStep

	file = open('cascade', 'w+')
	file.write(json.dumps(cascade))
	file.close()
else:
	file = open('cascade', 'r+')
	cascade = json.load(file)
	file.close()

printCascade(cascade)

"""
print(cascade[1]['sell_order']['amount']) #['sell_order']['amount']
print(cascade[2]['sell_order']['amount']) #['sell_order']['amount']
print(cascade[3]['sell_order']['amount']) #['sell_order']['amount']
"""

"""	
orderId = 753455999
res = curSite.getOrderStatus(orderId)
if res is False:
	print(curSite.getLastErrorMessage())
	quit()

print('OrderStatus: {0}'.format(res))
"""