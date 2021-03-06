from spec import Spec
import os, json

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
	
	allowRevers = False
	
	
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
	
	def setAllowRevers(self, allowRevers):
		self.allowRevers = allowRevers
		
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
		
	
	def createCascade(self, instrumentVolume = None, orderId = None, maxStages = 150):
		self.setPair(self.pair)
		
		if not instrumentVolume is None:
			instrumentVolume = float(instrumentVolume)
		self.totalInvest = float(self.totalInvest)
		
		if orderId:
			startPrice = round(self.lastPrice * (100 + self.startPercent) / 100, self.pricePrecision)
			endPrice = round(startPrice * (100 + self.deepPercent) / 100, self.pricePrecision)
			priceLength = endPrice - startPrice
			investFreq = round(instrumentVolume / priceLength, self.totalPrecision)
			investQuant = round(self.minAmount * (100 + 2 * self.fee) / 100, self.totalPrecision)
			priceStep = priceLength * investQuant / instrumentVolume
			#priceStep = round(priceLength * investQuant / instrumentVolume, self.pricePrecision)
			
			if priceStep < 10 ** -self.pricePrecision:
				priceStep = 10 ** -self.pricePrecision
				investQuant = round(priceStep * investFreq, self.pricePrecision)
			
			if instrumentVolume // investQuant > maxStages:
				investQuant = round(instrumentVolume / maxStages, self.totalPrecision)
				priceStep = priceLength / maxStages
				#priceStep = round(priceLength / maxStages, self.pricePrecision)
			else:
				maxStages = int(instrumentVolume // investQuant)
				investQuant = round(instrumentVolume / (instrumentVolume // investQuant), self.totalPrecision)
				priceStep = priceLength / (instrumentVolume // investQuant)
				#priceStep = round(priceLength / (instrumentVolume // investQuant), self.pricePrecision)
			
			acceptedSumm = 0
			cascade = []
			for stage in range(0, maxStages):
				curPrice = round(startPrice + priceStep * stage, self.pricePrecision)
				accepted = investQuant * (stage + 1)
				acceptedSumm += round(investQuant * curPrice * (100 - self.fee) / 100, self.pricePrecision)
				buyAmount = round(accepted * 100 / (100 - self.fee), self.totalPrecision)
				buyPrice = round(acceptedSumm / accepted * (100 - self.profitPercent) / 100, self.pricePrecision)
				cascade.append({
					'stage': stage, 
					'buyOrder': {'pair': self.pair, 'action': 'buy', 'price': buyPrice, 'operationAmount': buyAmount}, 
					'sellOrder': {'pair': self.pair, 'action': 'sell', 'price': curPrice, 'operationAmount': investQuant}, 
					'options' : {'order_id': orderId, 'amount': instrumentVolume}})
			return cascade
			

		startPrice = round(self.lastPrice * (100 - self.startPercent) / 100, self.pricePrecision)
		endPrice = round(startPrice * (100 - self.deepPercent) / 100, self.pricePrecision)
		priceLength = startPrice - endPrice
		investFreq = round((startPrice - endPrice) / self.totalInvest, self.totalPrecision)
		investQuant = round(startPrice * self.minAmount * (100 + 2 * self.fee) / 100, self.totalPrecision)
		priceStep = investQuant * investFreq
		#priceStep = round(investQuant * investFreq, self.pricePrecision)
		
		if investQuant * investFreq < 10 ** -self.pricePrecision:
			priceStep = 10 ** -self.pricePrecision
			investQuant = round(priceStep / investFreq, self.totalPrecision)
		
		if self.totalInvest // investQuant > maxStages:
			investQuant = round(self.totalInvest / maxStages, self.totalPrecision)
			priceStep = priceLength / maxStages
			#priceStep = round(priceLength / maxStages, self.pricePrecision)
		else:
			maxStages = int(self.totalInvest // investQuant)
			investQuant = round(self.totalInvest / (self.totalInvest // investQuant), self.totalPrecision)
			priceStep = priceLength / (self.totalInvest // investQuant)
			#priceStep = round(priceLength / (self.totalInvest // investQuant), self.pricePrecision)
			
		sellAmount = 0
		cascade = []
		for stage in range(0, maxStages):
			curPrice = round(startPrice - priceStep * stage, self.pricePrecision)
			curAmount = round(investQuant / curPrice, self.totalPrecision)
			if curAmount < self.minAmount:
				curAmount = self.minAmount
			invested = investQuant * (stage + 1)
			sellAmount += round(curAmount * (100 - self.fee) / 100, self.totalPrecision)
			sellPrice = round(invested / sellAmount * (100 + self.profitPercent) / 100, self.pricePrecision)
			cascade.append({'stage': stage, 'buyOrder': {'pair': self.pair, 'action': 'buy', 'price': curPrice, 'operationAmount': curAmount}, 'sellOrder': {'pair': self.pair, 'action': 'sell', 'price': sellPrice, 'operationAmount': sellAmount}})

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
		if not self.allowRevers:
			return False
		
		idx = len(cascade) - 1
		if 'status' in cascade[idx]['buyOrder'] and 'status' in cascade[idx]['sellOrder']:
			if cascade[idx]['buyOrder']['status'] == 1 and cascade[idx]['sellOrder']['status'] == 0:
				if round(self.lastPrice * (100 + self.startPercent) / 100, self.pricePrecision) < cascade[idx]['sellOrder']['price']:
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
		
		workAction = 'buyOrder'
		profitAction = 'sellOrder'
		
		if self.isRevers(cascade):
			workAction, profitAction = profitAction, workAction
		
		byedStage = None
		createdOrderCount = 0
		for element in cascade:
			if self.__isActiveOrder(element[workAction]):
				createdOrderCount += 1
			if createdOrderCount < self.activeOrdersCount and not self.__isCreatedOrder(element[workAction]):
				orderId = self.spec.createOrder(element[workAction])
				if orderId is False:
					print(self.spec.getLastErrorMessage())
					break
				element[workAction]['orderId'] = orderId
				if orderId is None:
					element[workAction]['status'] = 1
				else:
					element[workAction]['status'] = 0
				createdOrderCount += 1
			
			if self.__isCompleteOrder(element[workAction]):
				byedStage = element['stage']
		
		soldAmount = None
		for element in cascade:
			if element['stage'] > byedStage:
				break
			
			if not soldAmount is None:
				element[profitAction]['operationAmount'] -= soldAmount
			
			if element['stage'] < byedStage and self.__isCompleteOrder(element[profitAction]):
				print('Partial execution in stage {0}'.format(element['stage']))
				element[profitAction]['status'] = 2
				soldAmount = round(element[profitAction]['operationAmount'], self.totalPrecision)
			
			if element['stage'] < byedStage and self.__isActiveOrder(element[profitAction]):
				res = self.spec.cancelOrder(element[profitAction]['orderId'])
				if not res:
					print(self.spec.getLastErrorMessage())
					break
				element[profitAction]['status'] = 2
			
			if element['stage'] == byedStage and not self.__isCreatedOrder(element[profitAction]):
				orderId = self.spec.createOrder(element[profitAction])
				if orderId is False:
					print(self.spec.getLastErrorMessage())
					break
				element[profitAction]['orderId'] = orderId
				if orderId is None:
					element[profitAction]['status'] = 1
				else:
					element[profitAction]['status'] = 0
			
		# fix rest profit orders in partial execution case
		if not soldAmount is None:
			for element in cascade:
				if element['stage'] > byedStage:
					element[profitAction]['operationAmount'] -= soldAmount
		
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
	
	## 
	#  @brief Brief
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] cascade Parameter_Description
	#  @param [in] cascadeFileName Parameter_Description
	#  @return true in success case
	#  
	#  @details cancel last sell order and save direct cascade
	#  	
	def saveCascade(self, cascade = None, cascadeFileName = None):
		if (cascade is None):
			cascade = self.cascade
		if (cascade is None):
			print('saveCascade. Cascade element not defined')
			return False
		if cascadeFileName is None:
			print('saveCascade. Cascade file name not defined')
			return False
		
		idx = len(cascade) - 1
		
		if not self.__isActiveOrder(cascade[idx]['sellOrder']):
			print('saveCascade. Last save order is not active')
			return False
		
		res = self.spec.cancelOrder(cascade[idx]['sellOrder']['orderId'])
		if not res:
			print('saveCascade. Cancel order error ' + self.spec.getLastErrorMessage())
			return False

		os.rename(cascadeFileName, cascadeFileName + '.bkp')
		return True
	
	## 
	#  @brief Brief
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] cascade Parameter_Description
	#  @param [in] cascadeFileName Parameter_Description
	#  @return Return_Description
	#  
	#  @details Details
	#  	
	def restoreCascade(self, cascade = None, cascadeFileName = None):
		if (cascade is None):
			cascade = self.cascade
		if (cascade is None):
			print('saveCascade. Cascade element is not defined')
			return False
		if cascadeFileName is None:
			print('saveCascade. Cascade file name is not defined')
			return False
	
		os.rename(cascadeFileName + '.bkp', cascadeFileName)
		
		file = open(cascadeFileName, 'r+')
		cascade = json.load(file)
		file.close()
		
		idx = len(cascade) - 1
		
		orderId = self.spec.createOrder(cascade[idx]['sellOrder'])
		if orderId is False:
			print('restoreCascade. Create order error ' + self.spec.getLastErrorMessage())
			return False
			
		cascade[idx]['sellOrder']['orderId'] = orderId
		if orderId is None:
			cascade[idx]['sellOrder']['status'] = 1
		else:
			cascade[idx]['sellOrder']['status'] = 0
		
		file = open(cascadeFileName, 'w+')
		file.write(json.dumps(cascade))
		file.close()
			
		return True

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
