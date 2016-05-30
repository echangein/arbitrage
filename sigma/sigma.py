import time, os, json, datetime

from btce import Btce
from speculator import Speculator

class Sigma:
	stat = None
	exchange = None
	totalPrecision = 8
	
	sigma = None
	lastPrice = None
	conditions = None
	
	pair = None
	invest = None
	startIndent = 0.5
	totalIndent = 3.0
	minProfitPercent = 1.0
	
	maxStages = 150
	activeOrdersCount = 3
	
	
	## 
	#  @brief load lastPrise, sigma and trade conditions for specified pair
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] key Parameter_Description
	#  @param [in] secret Parameter_Description
	#  @param [in] pair Parameter_Description
	#  @return Return_Description
	#  
	#  @details Details
	#  	
	def __init__(self, key = None, secret = None, pair = None):
		if not pair:
			print('Sigma: Cant''t set init values without pair')
		
		self.pair = pair
		
		self.stat = Speculator()
		self.exchange = Btce(key, secret)
		
		self.sigma, error = self.stat.getSigmaAndAvg(pair)
		if not self.sigma:
			print(error)
			quit()
		
		res, error = self.exchange.getTicker([pair])
		if not res:
			print(error)
			quit()
		self.lastPrice = res[pair]['last']
		
		res, error = self.exchange.getConditions()
		if not res:
			print(error)
			quit()

		self.conditions = res['pairs'][pair]
	
	## 
	#  @brief Just print cascade struct
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] cascadeStruct Parameter_Description
	#  @return Return_Description
	#  
	#  @details Details
	#  	
	def printCascade(self, cascadeStruct):
		#TODO revers cascade
		
		print('created: {1} pair: {0[pair]} profit type: {0[profitType]} start price: {0[createLastPrice]} start sigma: {0[createSigma]}'.format(
			cascadeStruct['options'],
			datetime.datetime.fromtimestamp(cascadeStruct['options']['createTS']).strftime('%Y.%m.%d %H:%M:%S')
		))
		print('start indent: {0[startIndent]}, total indent: {0[totalIndent]} used: {0[invest]}'.format(
			cascadeStruct['options']
		))
		
		# =============== debug =============== #
		print('invest orders: {0}, profit orders: {1}'.format(len(cascadeStruct['investOrders']), len(cascadeStruct['profitOrders'])))
		# =============== debug =============== #
		
		invested = 0
		accepted = 0
		for stage in range(0, len(cascadeStruct['investOrders'])):
			invested += round( cascadeStruct['investOrders'][stage]['amount'] * cascadeStruct['investOrders'][stage]['price'], self.totalPrecision)
			accepted = round(cascadeStruct['profitOrders'][stage]['amount'] * cascadeStruct['profitOrders'][stage]['price'] * (100 - self.conditions['fee']) / 100, 6)
			profit = round(accepted - invested, 6)
			print('{0:>3} {1[type]} {1[amount]:<12} @ {1[price]:<12}inv {2:<14} {3[type]} {3[amount]:<12} @ {3[price]:<12} acc {4:<12} pft {5}'.format(
				stage, 
				cascadeStruct['investOrders'][stage], 
				invested, 
				cascadeStruct['profitOrders'][stage], 
				accepted,
				profit))
	
	
	#  @brief Brief
	#  
	#  @param [in] self Parameter_Description
	#  @return cascade
	#  
	#  @details Details
	#  	
	def createCascade(self, profitType = 'buy'):
		#TODO check revers cascade
		direction = -1
		investAction = 'sell'
		profitAction = 'buy'
		minInvest = self.conditions['min_amount'] / (100 - self.conditions['fee']) * 100
		investDiv = minInvest
		if profitType == 'buy':
			direction = 1
			investAction, profitAction = profitAction, investAction
			investDiv = minInvest * self.lastPrice
		
		options = {
			'version': '0.1',
			'pair': self.pair,
			'createTS': int(time.time()),
			'createLastPrice': self.lastPrice,
			'createSigma': self.sigma,
			'invest': self.invest, #will need for reverse
			'profitType': profitType, 
			'startIndent': self.startIndent,
			'totalIndent': self.totalIndent,
			'minProfitPercent': self.minProfitPercent
		}
		
		startPrice = self.lastPrice - self.startIndent * self.sigma * direction
		endPrice = self.lastPrice - self.totalIndent * self.sigma * direction
		steps = min(int(self.invest / investDiv), self.maxStages)
		options['totalStages'] = steps
		
		investQuant = self.invest / float(steps)
		options['investQuant'] = investQuant
		investOrders = self.__getInvestOrders(startPrice, endPrice, steps, investQuant, profitType)
		return {
			'options': options,
			'investOrders': investOrders,
			'profitOrders': self.__getProfitOrders(investOrders, [], profitType)
		}
	
	## 
	#  @brief generate invest orders for params
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] startPrice Parameter_Description
	#  @param [in] endPrice Parameter_Description
	#  @param [in] steps Parameter_Description
	#  @param [in] investQuant Parameter_Description
	#  @return Return_Description
	#  
	#  @details Details
	#  	
	def __getInvestOrders(self, startPrice, endPrice, steps, investQuant, profitType = 'buy'):
		#TODO revers cascade
		investAction = 'sell'
		profitAction = 'buy'
		if profitType == 'buy':
			investAction, profitAction = profitAction, investAction

		deltaPrice = (startPrice - endPrice) / float(steps)
		
		investOrders = []
		for stage in range(0, steps):
			price = startPrice - deltaPrice * stage
			amount = investQuant / price
			investOrders.append({
				'type': investAction,
				'amount': round(amount, self.totalPrecision),
				'price': round(price, self.conditions['decimal_places'])
			})
		return investOrders
	
	## 
	#  @brief generate profit order for invest order
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] investOrders Parameter_Description
	#  @param [in] profitOrders begin of exists profit orders sequence
	#  @param [in] profitType Parameter_Description
	#  @return Return_Description
	#  
	#  @details Details
	#  		
	def __getProfitOrders(self, investOrders = None, profitOrders = [], profitType = 'buy'):
		#TODO revers cascade
		investAction = 'sell'
		profitAction = 'buy'
		if profitType == 'buy':
			investAction, profitAction = profitAction, investAction
	
		invested = 0
		accepted = 0
		for order in investOrders:
			accepted += order['amount'] * (100 - self.conditions['fee']) / 100
			invested += order['amount'] * order['price']
			price = invested / accepted * (100 + self.minProfitPercent) / 100
			if profitOrders == [] or (len(profitOrders) and profitOrders[-1]['amount'] < accepted):
				profitOrders.append({
					'type': profitAction,
					'amount': round(accepted, self.totalPrecision),
					'price': round(price, self.conditions['decimal_places'])
				})
		return profitOrders
	
	## 
	#  @brief set class params from cascade options
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] cascadeStruct Parameter_Description
	#  @return Return_Description
	#  
	#  @details Details
	#  	
	def setParams(self, cascadeStruct):
		if not 'options' in cascadeStruct:
			print('options param not set in cascade struct')
			quit()
		
		self.pair = cascadeStruct['options']['pair']
		self.invest = cascadeStruct['options']['invest']
		self.startIndent = cascadeStruct['options']['startIndent']
		self.totalIndent = cascadeStruct['options']['totalIndent']
		self.minProfitPercent = cascadeStruct['options']['minProfitPercent']
		
	## 
	#  @brief only update order status
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] cascadeStruct Parameter_Description
	#  @return cascadeStruct, False or cascadeStruct, errorMessage
	#  
	#  @details 0 - active, 1 - excuted, 2 - canceled, 3 - canceled but partial executed
	#  
	def checkOrders(self, cascadeStruct):
		res, error = self.exchange.getActiveOrders(self.pair) #self.pair
		if not res and error <> 'no orders':
			return cascadeStruct, error
		
		orderIds = []
		if not isinstance(res, bool):
			orderIds = res.keys()
		
		for order in cascadeStruct['investOrders']:
			if self.__isActiveOrder(order) and not order['orderId'] in orderIds:
				order['status'] = 1
		
		for order in cascadeStruct['profitOrders']:
			if self.__isActiveOrder(order) and not order['orderId'] in orderIds:
				order['status'] = 1
		
		return cascadeStruct, False
	
	## 
	#  @brief True if exist executed invest order
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] cascadeStruct Parameter_Description
	#  @return True or False
	#  
	#  @details Details
	#  
	def inWork(self, cascadeStruct):
		for order in cascadeStruct['investOrders']:
			if self.__isCompleteOrder(order):
				return True
		
		return False

	## 
	#  @brief compare lastPrice and first invest order by start indent
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] cascadeStruct Parameter_Description
	#  @return True or False
	#  
	#  @details Details
	#  
	def needRestart(self, cascadeStruct):
		#TODO modify for sell profit type
		if self.lastPrice > cascadeStruct['investOrders'][0]['price'] + self.sigma * self.startIndent:
			return True
		
		return False
	
	## 
	#  @brief True if exists executed profit order
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] cascadeStruct Parameter_Description
	#  @return True or False
	#  
	#  @details Details
	#  
	def hasProfit(self, cascadeStruct):
		for order in cascadeStruct['profitOrders']:
			if self.__isCompleteOrder(order):
				return True
		
		return False

	## 
	#  @brief just print options and cascade
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] cascadeStruct Parameter_Description
	#  @return Return_Description
	#  
	#  @details Details
	#  		
	def reportProfit(self, cascadeStruct):
		#TODO modify for sell profit type
		cou = 0
		invested = 0
		for profitOrder in cascadeStruct['profitOrders']:
			invested += cascadeStruct['investOrders'][cou]['price'] * cascadeStruct['investOrders'][cou]['amount']
			if self.__isCompleteOrder(profitOrder):
				print('Stage {0} of {1}. Invested {3} of {4}. Profit percent: {5}. Profit: {2}'.format(
					cou,
					len(cascadeStruct['investOrders']) - 1, 
					profitOrder['amount'] * profitOrder['price'] * (100 - self.conditions['fee']) / 100 - invested,
					invested,
					cascadeStruct['options']['invest'],
					cascadeStruct['options']['minProfitPercent']
				))
				break
			cou += 1
	
	## 
	#  @brief True if exists executed invest order after executed profit order
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] cascadeStruct Parameter_Description
	#  @return True or Falase
	#  
	#  @details Details
	#  
	def hasPartialExecution(self, cascadeStruct):
		cou = 0
		for profitOrder in cascadeStruct['profitOrders']:
			if self.__isCompleteOrder(profitOrder):
				break
			cou += 1
		
		if cou == len(cascadeStruct['profitOrders']) - 1:
			return False
		
		for investOrder in cascadeStruct['investOrders'][cou + 1:]:
			if self.__isCompleteOrder(investOrder):
				return True
		
		return False
	
	## 
	#  @brief cut executed parts with profit and recalc profit order
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] cascadeStruct Parameter_Description
	#  @return cascade struct
	#  
	#  @details Details
	#  	
	def resizeAfterProfit(self, cascadeStruct):
		#TODO mb need modify for sell profit type
		cou = 0
		for profitOrder in cascadeStruct['profitOrders']:
			if self.__isCompleteOrder(profitOrder):
				break
			cou += 1
		
		cascadeStruct['investOrders'] = cascadeStruct['investOrders'][cou + 1:]
		cascadeStruct['profitOrders'] = self.__getProfitOrders(cascadeStruct['investOrders'])
		
		return cascadeStruct
		
	## 
	#  @brief cancel all orders
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] cascadeStruct Parameter_Description
	#  @return cascadeStruct, False or cascadeStruct, errorMessage
	#  
	#  @details 0 - active, 1 - excuted, 2 - canceled, 3 - canceled but partial executed
	#  	
	def cancelOrders(self, cascadeStruct):
		for order in cascadeStruct['investOrders']:
			if self.__isActiveOrder(order):
				res, error = self.exchange.cancelOrder(order['orderId'])
				if res:
					order['status'] = 2
				else:
					return cascadeStruct, error
		
		for order in cascadeStruct['profitOrders']:
			if self.__isActiveOrder(order):
				res, error = self.exchange.cancelOrder(order['orderId'])
				if res:
					order['status'] = 2
				else:
					return cascadeStruct, error
		
		return cascadeStruct, False

	## 
	#  @brief create invest orders to self.activeOrdersCount counts
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] cascadeStruct Parameter_Description
	#  @return cascadeStruct, False or cascadeStruct, errorMessage
	#  
	#  @details 0 - active, 1 - excuted, 2 - canceled, 3 - canceled but partial executed
	#  		
	def createOrders(self, cascadeStruct):
		ordersCount = 0
		lastIdx = 0
		for order in cascadeStruct['investOrders']:
			if self.__isActiveOrder(order):
				ordersCount += 1
			if not self.__isCreatedOrder(order):
				break;
			lastIdx += 1
		
		if lastIdx >= len(cascadeStruct['investOrders']): # all invest orders complete
			return cascadeStruct, False
		
		print('active ordersCount {0} lastIdx {1}'.format(ordersCount, lastIdx))
		print(range(lastIdx, lastIdx + self.activeOrdersCount - ordersCount))
		
		for idx in range(lastIdx, lastIdx + self.activeOrdersCount - ordersCount):
			if idx < len(cascadeStruct['investOrders']):
				orderId, error = self.__createOrder(cascadeStruct['investOrders'][idx])
				if orderId is False:
					return cascadeStruct, error
				else:
					cascadeStruct['investOrders'][idx]['orderId'] = orderId
					if orderId == 0:
						cascadeStruct['investOrders'][idx]['status'] = 1
					else:
						cascadeStruct['investOrders'][idx]['status'] = 0
		
		return cascadeStruct, False
	
	## 
	#  @brief Brief
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] order Parameter_Description
	#  @return orderId, False or 0, False or False, error
	#  
	#  @details Details
	#  	
	def __createOrder(self, order):
		res, error = self.exchange.createOrder(self.pair, order['type'], order['price'], order['amount'])
		if res:
			return int(res['order_id']), False
		else:
			return False, error
		
	
	## 
	#  @brief recalc not active invest and profitorder
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] cascadeStruct Parameter_Description
	#  @return cascadeStruct
	#  
	#  @details Details
	#  
	def shiftOrders(self, cascadeStruct):
		print('shiftOrders is not implement')
		quit()
	
	## 
	#  @brief move profit order to last executed invest order
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] cascadeStruct Parameter_Description
	#  @return cascadeStruct, False or cascadeStruct, errorMessage
	#  
	#  @details Details
	#  
	def moveProfitOrder(self, cascadeStruct):
		print('moveProfitOrder is not implement')
		quit()
	
	## 
	#  @brief order is created but not compete
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] order Parameter_Description
	#  @return Return_Description
	#  
	#  @details 0 - active, 1 - excuted, 2 - canceled, 3 - canceled but partial executed
	#  		
	def __isActiveOrder(self, order):
		if 'orderId' in order and 'status' in order and order['status'] == 0:
			return True
		return False
		
	## 
	#  @brief order was be created
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] order Parameter_Description
	#  @return Return_Description
	#  
	#  @details 0 - active, 1 - excuted, 2 - canceled, 3 - canceled but partial executed
	#  		
	def __isCreatedOrder(self, order):
		if 'orderId' in order:
			return True
		return False
		
	## 
	#  @brief order is executed
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] order Parameter_Description
	#  @return Return_Description
	#  
	#  @details 0 - active, 1 - excuted, 2 - canceled, 3 - canceled but partial executed
	#  		
	def __isCompleteOrder(self, order):
		if 'orderId' in order and 'status' in order and order['status'] == 1:
			return True
		return False
