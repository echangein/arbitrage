from spec import Spec

class Cascade:
	checkTimeout = 10
	spec = None
	cascade = None
	
	lastPrice = None
	pricePrecision = None
	minAmount = None
	fee = None
	
	activeOrdersCount = 5
	totalPrecision = 8
	profitPrecision = 2
	pair = 'btc_usd'
	
	profitPercent = 1
	deepPercent = 10
	totalInvest = 5
	
	
	def setActiveOrdersCount(self, activeOrdersCount):
		self.activeOrdersCount = activeOrdersCount
	
	def setTotalPrecision(self, totalPrecision):
		self.totalPrecision = totalPrecision
	
	def setProfitPrecision(self, profitPrecision):
		self.profitPrecision = profitPrecision
	
	def setPair(self, pair):
		self.pair = pair
		if not self.spec.checkConnection():
			quit()
			
		if not self.spec.loadTradeConditions():
			quit()

		if not self.spec.loadTickers([pair]):
			quit()
		
		self.lastPrice = self.spec.tickers[pair]['last']
		self.pricePrecision = self.spec.pairs[pair]['decimal_places']
		self.minAmount = self.spec.pairs[pair]['min_amount']
		self.fee = self.spec.pairs[pair]['fee']

	def setProfitPercent(self, profitPercent):
		self.profitPercent = profitPercent
		
	def setDeepPercent(self, deepPercent):
		self.deepPercent = deepPercent
	
	def setTotalInvest(self, totalInvest):
		self.totalInvest = totalInvest
		
	def __init__(self, key = None, secret = None):
		self.spec = Spec(key, secret)
	
	def setCascade(self, cascade):
		self.cascade = cascade
	
	def getCascade(self):
		return self.cascade
	
	def printCascade(self, cascade = None):
		if (cascade is None):
			print('Cascade element not defined')
			quit()
			
		invested = 0
		for item in cascade:
			invested += round(item['buyOrder']['price'] * item['buyOrder']['operationAmount'], self.totalPrecision)
			accepted = round(item['sellOrder']['price'] * item['sellOrder']['operationAmount'] * (100 - self.fee) / 100, self.totalPrecision)
			profit = round(accepted - invested, self.profitPrecision)
			print('{0[stage]:>3} buy {1[operationAmount]:<12}@ {1[price]:<12}inv: {3:<12}sell: {2[operationAmount]:<12}@ {2[price]:<12}accp: {4:<14} {5:<2}'.format(item, item['buyOrder'], item['sellOrder'], invested, accepted, profit))
		
	
	def createCascade(self):
		self.setPair(self.pair)
		startPrice = round(self.lastPrice * (100 - self.profitPercent) / 100, self.pricePrecision)
		endPrice = round(startPrice * (100 - self.deepPercent) / 100, self.pricePrecision)
		priceLength = startPrice - endPrice
		investDensity = round((startPrice - endPrice) / self.totalInvest, self.totalPrecision)
		investQuant = round(startPrice * self.minAmount * (100 + 2 * self.fee) / 100, self.pricePrecision)

		priceStep = round(investQuant * investDensity, self.pricePrecision)
		
		if priceStep == 0:
			priceStep = 10 ** -self.pricePrecision
		
		curInvest = self.totalInvest
		curPrice = startPrice
		invested = 0
		stage = 0
		sellAmount = 0
		cascade = []
		while curInvest >= investQuant:
			curAmount = round(investQuant / curPrice, self.totalPrecision)
			if curAmount < self.minAmount:
				curAmount = self.minAmount
				
			invested += investQuant
			sellAmount += round(curAmount * (100 - self.fee) / 100, self.totalPrecision)
			sellPrice = round(invested / sellAmount * (100 + self.profitPercent) / 100, self.pricePrecision)
			cascade.append({'stage': stage, 'buyOrder': {'pair': self.pair, 'action': 'buy', 'price': curPrice, 'operationAmount': curAmount}, 'sellOrder': {'pair': self.pair, 'action': 'sell', 'price': sellPrice, 'operationAmount': sellAmount}})
			stage += 1
			curInvest -= investQuant
			curPrice -= priceStep			
		
		return cascade
	
	def inWork(self, cascade = None):
		if (cascade is None):
			cascade = self.cascade
		if (cascade is None):
			print('Cascade element not defined')
			quit()
		
		byedStage = None
		for element in cascade:
			if self.__isCompleteOrder(element['buyOrder']):
				byedStage = element['stage']
		
		if byedStage is None:
			return False
		
		for element in cascade:
			if element['stage'] == byedStage:
				if 'orderId' in element['sellOrder'] and 'status' in element['sellOrder'] and element['sellOrder']['status'] == 1:
					return False
		
		return True
	
	def checkLastPrice(self, cascade = None):
		if (cascade is None):
			cascade = self.cascade
		if (cascade is None):
			print('Cascade element not defined')
			quit()

		if not self.spec.loadTickers([self.pair]):
			quit()
		
		lastPrice = self.spec.tickers[self.pair]['last']
		cascadeStartPrice = self.cascade[0]['buyOrder']['price']
		
		print('{0} <> {1}'.format(lastPrice, cascadeStartPrice * (100 + self.profitPercent * 2 ) / 100))
		
		if lastPrice > cascadeStartPrice * (100 + self.profitPercent * 2 ) / 100:
			return True
		
		return False
		
	def createOrders(self, cascade = None):
		if (cascade is None):
			cascade = self.cascade
		if (cascade is None):
			print('Cascade element not defined')
			quit()
		
		byedStage = None
		createdOrderCount = 0
		for element in cascade:
			if self.__isActiveOrder(element['buyOrder']):
				createdOrderCount += 1
			if createdOrderCount < self.activeOrdersCount and not self.__isCreatedOrder(element['buyOrder']):
				orderId = self.spec.createOrder(element['buyOrder'])
				if orderId is False:
					print(self.spec.getLastErrorMessage())
					quit()
				element['buyOrder']['orderId'] = orderId
				if orderId is None:
					element['buyOrder']['status'] = 1
				else:
					element['buyOrder']['status'] = 0
				createdOrderCount += 1
			
			if self.__isCompleteOrder(element['buyOrder']):
				byedStage = element['stage']
				
		for element in cascade:
			if element['stage'] > byedStage:
				break
			
			if element['stage'] < byedStage and self.__isActiveOrder(element['sellOrder']):
				res = self.spec.cancelOrder(element['sellOrder']['orderId'])
				if not res:
					print(self.spec.getLastErrorMessage())
					quit()
			
			if element['stage'] == byedStage and not self.__isCreatedOrder(element['sellOrder']):
				orderId = self.spec.createOrder(element['sellOrder'])
				if orderId is False:
					print(self.spec.getLastErrorMessage())
					quit()
				element['sellOrder']['orderId'] = orderId
				if orderId is None:
					element['sellOrder']['status'] = 1
				else:
					element['sellOrder']['status'] = 0
		
		return cascade
	
	def __isActiveOrder(self, order):
		if 'orderId' in order and 'status' in order and order['status'] == 0:
			return True
		return False
		
	def __isCreatedOrder(self, order):
		if 'orderId' in order:
			return True
		return False
		
	def __isCompleteOrder(self, order):
		if 'orderId' in order and 'status' in order and order['status'] == 1:
			return True
		return False