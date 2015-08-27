#-*-coding:utf-8-*-

from kbrd import getch
from spec import Spec

totalPrecision = 8
pair = 'nmc_usd'

profitPercent = 2
deepPercent = 15
totalInvest = 5

curSite = Spec()

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
print('lastPrice:\t{0}'.format(lastPrice))

startPrice = round(lastPrice * (100 - profitPercent) / 100, pricePrecision)
endPrice = round(startPrice * (100 - deepPercent) / 100, pricePrecision)
priceLength = startPrice - endPrice
investDensity = round((startPrice - endPrice) / totalInvest, totalPrecision)
investQuant = round(startPrice * minAmount * (100 + 2 * fee) / 100, pricePrecision)

priceStep = round(investQuant * investDensity, pricePrecision)
if priceStep == 0:
	print('ZERO priceStep: '+str(investQuant * investDensity))
	priceStep = 10 ** -pricePrecision

print('\nstartPrice:\t{0}'.format(startPrice))
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
	stage += 1
	curInvest -= investQuant
	curPrice -= priceStep