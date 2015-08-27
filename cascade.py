#-*-coding:utf-8-*-

from kbrd import getch
import time, os, json
from spec import Spec

def printCascade(cascade):
	for item in cascade:
		#print(item['stage'])
		print('{0[stage]:>3} buy {1[amount]:<12}@ {1[rate]:<12}sell: {2[amount]:<12}@ {2[rate]:<12}'.format(item, item['buyOrder'], item['sellOrder']))
		"""
		print('{stage:>3} buy {1:<12}@ {2:<12}inv: {3:<12}sell: {4:<12}@ {5:<12}accp: {6:<14} {7:<2}'.format(stage, curAmount, curPrice, invested, sellAmount, sellPrice, accepted, profit))
	
		curAmount = round(investQuant / curPrice, totalPrecision)
		if curAmount < minAmount:
			curAmount = minAmount
			
		invested += investQuant
		sellAmount += round(curAmount * (100 - fee) / 100, totalPrecision)
		sellPrice = round(invested / sellAmount * (100 + profitPercent) / 100, pricePrecision)
		accepted = round(sellAmount * sellPrice * (100 - fee) / 100, totalPrecision)
		profit = round(accepted - invested, 3)
		print('{0:>3} buy {1:<12}@ {2:<12}inv: {3:<12}sell: {4:<12}@ {5:<12}accp: {6:<14} {7:<2}'.format(stage, curAmount, curPrice, invested, sellAmount, sellPrice, accepted, profit))
		cascade.append({'stage': stage, 'buy_order': {'pair': pair, 'type': 'buy', 'rate': curPrice, 'amount': curAmount}, 'sell_order': {'pair': pair, 'type': 'sell', 'rate': sellPrice, 'amount': sellAmount}})
		stage += 1
		curInvest -= investQuant
		curPrice -= priceStep
	"""

totalPrecision = 8
pair = 'ltc_usd'

profitPercent = 2
deepPercent = 20
totalInvest = 5

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
		accepted = round(sellAmount * sellPrice * (100 - fee) / 100, totalPrecision)
		profit = round(accepted - invested, 3)
		print('{0:>3} buy {1:<12}@ {2:<12}inv: {3:<12}sell: {4:<12}@ {5:<12}accp: {6:<14} {7:<2}'.format(stage, curAmount, curPrice, invested, sellAmount, sellPrice, accepted, profit))
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