import time, os, json

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
	activeOrders = 3
	
	
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
			'pair': self.pair,
			'createTS': int(time.time()),
			'createLastPrice': self.lastPrice,
			'createSigma': self.sigma,
			'version': '0.1'
		}
		
		startPrice = self.lastPrice - self.startIndent * self.sigma * direction
		endPrice = self.lastPrice - self.totalIndent * self.sigma * direction
		steps = min(int(self.invest / investDiv), self.maxStages)
		options['stages'] = steps
		
		investQuant = self.invest / float(steps)
		options['investQuant'] = investQuant
		investOrders = self.__getInvestOrders(startPrice, endPrice, steps, investQuant)
		return {
			'options': options,
			'investOrders': investOrders,
			'profitOrders': self.__getProfitOrders(investOrders, profitType)
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
	#  @return Return_Description
	#  
	#  @details Details
	#  		
	def __getProfitOrders(self, investOrders = None, profitType = 'buy'):
		#TODO revers cascade
		investAction = 'sell'
		profitAction = 'buy'
		if profitType == 'buy':
			investAction, profitAction = profitAction, investAction
	
		profitOrders = []
		invested = 0
		accepted = 0
		for order in investOrders:
			accepted += order['amount'] * (100 - self.conditions['fee']) / 100
			invested += order['amount'] * order['price']
			price = invested / accepted * (100 + self.minProfitPercent) / 100
			#if profitType <> 'buy':
			#	accepted += order['amount'] * order['price'] * (100 - self.conditions['fee']) / 100
			#	invested += order['amount']
			#	price = 
			
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
		print('setParams is not implement')
		quit()
		
	## 
	#  @brief only update order status
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] cascadeStruct Parameter_Description
	#  @return cascadeStruct, False or cascadeStruct, errorMessage
	#  
	#  @details Details
	#  
	def checkOrders(self, cascadeStruct):
		print('checkOrders is not implement')
		quit()
	
	## 
	#  @brief True if exist active or executed profit order
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] cascadeStruct Parameter_Description
	#  @return True or False
	#  
	#  @details Details
	#  
	def inWork(self, cascadeStruct):
		print('inWork is not implement')
		quit()

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
		print('needRestart is not implement')
		quit()
	
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
		print('hasProfit is not implement')
		quit()

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
		print('reportProfit is not implement')
		quit()
	
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
		print('hasPartialExecution is not implement')
		quit()
	
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
		print('resizeAfterProfit is not implement')
		quit()
		
	## 
	#  @brief cancel all orders
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] cascadeStruct Parameter_Description
	#  @return cascadeStruct, False or cascadeStruct, errorMessage
	#  
	#  @details Details
	#  	
	def cancelOrders(self, cascadeStruct):
		print('cancelOrders is not implement')
		quit()

	## 
	#  @brief create invest orders to self.activeOrders counts
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] cascadeStruct Parameter_Description
	#  @return cascadeStruct, False or cascadeStruct, errorMessage
	#  
	#  @details Details
	#  		
	def createOrders(self, cascadeStruct):
		print('createOrders is not implement')
		quit()
	
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