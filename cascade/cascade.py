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
	startPercent = 1
	deepPercent = 15
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
		
	def setStartPercent(self, startPercent):
		self.startPercent = startPercent
		
	def setDeepPercent(self, deepPercent):
		self.deepPercent = deepPercent
	
	def setTotalInvest(self, totalInvest):
		self.totalInvest = totalInvest
		
	def __init__(self, key = None, secret = None, silent = False):
		self.spec = Spec(key, secret, silent)
	
	def setCascade(self, cascade):
		self.cascade = cascade
	
	def getCascade(self):
		return self.cascade
	
	def printCascade(self, cascade = None):
		if (cascade is None):
			print('printCascade. Cascade element not defined')
			quit()
		
		if len(cascade) > 0 and 'options' in cascade[0]:
			returned = 0
			accepted = 0
			profit = 0
			
			for item in cascade:
				accepted += round(item['sellOrder']['price'] * item['sellOrder']['operationAmount'] * (100 - self.fee) / 100, self.pricePrecision)
				returned = round(item['buyOrder']['operationAmount'] * (100 - self.fee) / 100, self.totalPrecision)
				profit = round(accepted - item['buyOrder']['operationAmount'] * item['buyOrder']['price'], self.profitPrecision)
				
				print('{0[stage]:>3} sell {1[operationAmount]:<12}@ {1[price]:<12}acc: {3:<12} buy: {2[operationAmount]:<12}@ {2[price]:<12}ret: {4:<14} {5:<2}'.format(item, item['sellOrder'], item['buyOrder'], accepted, returned, profit))
		
			return
			
		invested = 0
		for item in cascade:
			invested += round(item['buyOrder']['price'] * item['buyOrder']['operationAmount'], self.totalPrecision)
			accepted = round(item['sellOrder']['price'] * item['sellOrder']['operationAmount'] * (100 - self.fee) / 100, self.totalPrecision)
			profit = round(accepted - invested, self.profitPrecision)
			print('{0[stage]:>3} buy {1[operationAmount]:<12}@ {1[price]:<12}inv: {3:<12} sell: {2[operationAmount]:<12}@ {2[price]:<12}accp: {4:<14} {5:<2}'.format(item, item['buyOrder'], item['sellOrder'], invested, accepted, profit))
		
	
	def createCascade(self, instrumentVolume = None, orderId = None):
		self.setPair(self.pair)
		
		if orderId:
			startPrice = round(self.lastPrice * (100 + self.startPercent) / 100, self.pricePrecision)
			endPrice = round(startPrice * (100 + self.deepPercent) / 100, self.pricePrecision)
			priceLength = endPrice - startPrice
			investFreq = round(instrumentVolume / priceLength, self.totalPrecision)
			investQuant = round(self.minAmount * (100 + 2 * self.fee) / 100, self.totalPrecision)
			priceStep = round(priceLength * investQuant / instrumentVolume, self.pricePrecision)
			
			if priceStep < 10 ** -self.pricePrecision: #priceStep == 0
				#print('ZERO step')
				priceStep = 10 ** -self.pricePrecision
				investQuant = round(priceStep * investFreq, self.pricePrecision)
			
			
			#print('startPrice: {0}, endPrice: {1}, priceLength: {2}, investQuant: {3}, priceStep: {4}, investFreq: {5}'.format(startPrice, endPrice, priceLength, investQuant, priceStep, investFreq))
			
			curSelld = instrumentVolume
			curPrice = startPrice
			stage = 0
			
			acceptedSumm = 0
			accepted = 0
			cascade = []
			while curSelld >= investQuant:
				
				"""curAmount = round(investQuant / curPrice, self.totalPrecision)
				if curAmount < self.minAmount:
					curAmount = self.minAmount"""
					
				accepted += investQuant
				acceptedSumm += round(investQuant * curPrice * (100 - self.fee) / 100, self.pricePrecision)
				buyAmount = round(accepted * 100 / (100 - self.fee), self.totalPrecision)
				buyPrice = round(acceptedSumm / accepted * (100 - self.profitPercent) / 100, self.pricePrecision)
				#acceptedPrice = round(invested / sellAmount * (100 + self.profitPercent) / 100, self.pricePrecision)
				#sellAmount += round(curAmount * (100 - self.fee) / 100, self.totalPrecision)
				#sellPrice = round(invested / sellAmount * (100 + self.profitPercent) / 100, self.pricePrecision)
				cascade.append({
					'stage': stage, 
					'buyOrder': {'pair': self.pair, 'action': 'buy', 'price': buyPrice, 'operationAmount': buyAmount}, 
					'sellOrder': {'pair': self.pair, 'action': 'sell', 'price': curPrice, 'operationAmount': investQuant}, 
					'options' : {'order_id': orderId, 'amount': instrumentVolume}})
				stage += 1
				curSelld -= investQuant
				curPrice += priceStep			
			return cascade

		startPrice = round(self.lastPrice * (100 - self.startPercent) / 100, self.pricePrecision)
		endPrice = round(startPrice * (100 - self.deepPercent) / 100, self.pricePrecision)
		priceLength = startPrice - endPrice
		investFreq = round((startPrice - endPrice) / self.totalInvest, self.totalPrecision)
		investQuant = round(startPrice * self.minAmount * (100 + 2 * self.fee) / 100, self.pricePrecision)

		priceStep = round(investQuant * investFreq, self.pricePrecision)
		
		if investQuant * investFreq < 10 ** -self.pricePrecision: #priceStep == 0
			priceStep = 10 ** -self.pricePrecision
			investQuant = round(priceStep / investFreq, self.pricePrecision)
		
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

	## 
	#  @brief Brief
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] cascade Parameter_Description
	#  @return True if can start reverse cascade, False in other case
	#  
	#  @details 0 - active, 1 - complete, 2 - canceled
	#  		
	def needReverse(self, cascade = None):
		if (cascade is None):
			cascade = self.cascade
		
		if (cascade is None):
			return False
		if len(cascade) == 0:
			return False
		if 'options' in cascade[0]:
			return False
		
		idx = len(cascade) - 1
		if 'status' in cascade[idx]['buyOrder'] and 'status' in cascade[idx]['sellOrder']:
			if cascade[idx]['buyOrder']['status'] == 1 and cascade[idx]['sellOrder']['status'] == 0:
				if round(self.lastPrice * (100 + self.startPercent) / 100, self.pricePrecision) < cascade[idx]['buyOrder']['price']:
					return True
		
		return False
	
	## 
	#  @brief detect type of cascade True - reverse, False - Normal
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] cascade Parameter_Description
	#  @return Return_Description
	#  
	#  @details what doing with incorrect cascade structure?
	#  	
	def isRevers(self, cascade = None):
		if len(cascade) > 0 and 'options' in cascade[0]:
			return True
		
		return False
	
	## 
	#  @brief Brief
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] cascade Parameter_Description
	#  @return instrumentVolume, orderId or None, None
	#  
	#  @details Details
	#  	
	def getReverseParams(self, cascade = None):
		if len(cascade) > 0 and 'options' in cascade[0]:
			#case reverse cascade
			return cascade[0]['options']['amount'], cascade[0]['options']['order_id']
			
		idx = len(cascade) - 1
		if 'orderId' in cascade[idx]['sellOrder'] and cascade[idx]['sellOrder']['status'] == 0:
			#case direct cascade
			return cascade[idx]['sellOrder']['operationAmount'], cascade[idx]['sellOrder']['orderId']
		
		return None, None
	
	def inWork(self, cascade = None):
		if (cascade is None):
			cascade = self.cascade
		if (cascade is None):
			print('inWork. Cascade element not defined')
			quit()
		
		workAction = 'buyOrder'
		profitAction = 'sellOrder'
		
		if self.isRevers(cascade):
			workAction, profitAction = profitAction, workAction
		
		byedStage = None
		for element in cascade:
			if self.__isCompleteOrder(element[workAction]):
				byedStage = element['stage']
		
		if byedStage is None:
			return False
		
		for element in cascade:
			if element['stage'] == byedStage:
				if self.__isCompleteOrder(element[profitAction]):
					return False
		
		return True
	
	def needRestart(self, cascade = None):
		if (cascade is None):
			cascade = self.cascade
		if (cascade is None):
			print('needRestart. Cascade element not defined')
			quit()

		if not self.spec.loadTickers([self.pair]):
			quit()
		
		lastPrice = self.spec.tickers[self.pair]['last']
		if self.isRevers(cascade):
			cascadeStartPrice = cascade[0]['sellOrder']['price']
			if lastPrice < cascadeStartPrice * (100 - self.startPercent * 2 ) / 100:
				return True
		else:
			cascadeStartPrice = cascade[0]['buyOrder']['price']
			
			if lastPrice > cascadeStartPrice * (100 + self.startPercent * 2 ) / 100:
				return True
		
		return False
		
	def createOrders(self, cascade = None):
		if (cascade is None):
			cascade = self.cascade
		if (cascade is None):
			print('createOrders. Cascade element not defined')
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
					break
				element['buyOrder']['orderId'] = orderId
				if orderId is None:
					element['buyOrder']['status'] = 1
				else:
					element['buyOrder']['status'] = 0
				createdOrderCount += 1
			
			if self.__isCompleteOrder(element['buyOrder']):
				byedStage = element['stage']
		
		soldAmount = None
		for element in cascade:
			if element['stage'] > byedStage:
				break
			
			if not soldAmount is None:
				element['sellOrder']['operationAmount'] -= soldAmount
			
			if element['stage'] < byedStage and self.__isCompleteOrder(element['sellOrder']):
				print('Partial execution in stage {0}'.format(element['stage']))
				element['sellOrder']['status'] = 2
				soldAmount = round(element['sellOrder']['operationAmount'], self.totalPrecision)
			
			if element['stage'] < byedStage and self.__isActiveOrder(element['sellOrder']):
				res = self.spec.cancelOrder(element['sellOrder']['orderId'])
				if not res:
					print(self.spec.getLastErrorMessage())
					break
				element['sellOrder']['status'] = 2
			
			if element['stage'] == byedStage and not self.__isCreatedOrder(element['sellOrder']):
				orderId = self.spec.createOrder(element['sellOrder'])
				if orderId is False:
					print(self.spec.getLastErrorMessage())
					break
				element['sellOrder']['orderId'] = orderId
				if orderId is None:
					element['sellOrder']['status'] = 1
				else:
					element['sellOrder']['status'] = 0
			
		# fix rest sell orders in partial execution case
		if not soldAmount is None:
			for element in cascade:
				if element['stage'] > byedStage:
					element['sellOrder']['operationAmount'] -= soldAmount
		
		return cascade
	
	def cancelOrders(self, cascade = None):
		if (cascade is None):
			cascade = self.cascade
		if (cascade is None):
			print('cancelOrders. Cascade element not defined')
			quit()
		
		workAction = 'buyOrder'
		profitAction = 'sellOrder'
		
		if self.isRevers(cascade):
			workAction, profitAction = profitAction, workAction

		for element in cascade:
			if self.__isActiveOrder(element[workAction]):
				res = self.spec.cancelOrder(element[workAction]['orderId'])
				if not res:
					print(self.spec.getLastErrorMessage())
					break
				element[workAction]['status'] = 2
			
			if self.__isActiveOrder(element[profitAction]):
				print('CANCEL profit order!')
				res = self.spec.cancelOrder(element[profitAction]['orderId'])
				if not res:
					print(self.spec.getLastErrorMessage())
					break
				element[profitAction]['status'] = 2
		
		return cascade
	
	def checkOrders(self, cascade = None):
		if (cascade is None):
			cascade = self.cascade
		if (cascade is None):
			print('checkOrders. Cascade element not defined')
			quit()
		
		for element in cascade:
			if self.__isActiveOrder(element['buyOrder']):
				status = self.spec.getOrderStatus(element['buyOrder']['orderId'])
				if status is False:
					print(self.spec.getLastErrorMessage())
					break
				element['buyOrder']['status'] = status
			
			if self.__isActiveOrder(element['sellOrder']):
				status = self.spec.getOrderStatus(element['sellOrder']['orderId'])
				if status is False:
					print(self.spec.getLastErrorMessage())
					break
				element['sellOrder']['status'] = status
		
		return cascade
	
	def getProfit(self, cascade = None):
		if (cascade is None):
			cascade = self.cascade
		if (cascade is None):
			print('getProfit. Cascade element not defined')
			quit()
		
		profit = False
		
		if self.isRevers(cascade):
			accepted = 0
			for element in cascade:
				accepted += round(element['sellOrder']['price'] * element['sellOrder']['operationAmount'] * (100 - self.fee) / 100, self.pricePrecision)
				if self.__isCompleteOrder(element['buyOrder']):
					used = round(element['buyOrder']['price'] * element['buyOrder']['operationAmount'], self.totalPrecision)
					profit = accepted - used
					print('Stage: {0}, profit: {1}'.format(element['stage'], profit))
					profit = round(profit, self.profitPrecision)
		else:
			invested = 0
			for element in cascade:
				invested += round(element['buyOrder']['price'] * element['buyOrder']['operationAmount'], self.totalPrecision)
				if self.__isCompleteOrder(element['sellOrder']):
					accepted = round(element['sellOrder']['price'] * element['sellOrder']['operationAmount'] * (100 - self.fee) / 100, self.totalPrecision)
					profit = accepted - invested
					print('Stage: {0}, profit: {1}'.format(element['stage'], profit))
					profit = round(profit, self.profitPrecision)
		
		return profit
			
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
