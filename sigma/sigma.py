import time, os, json

from btce import Btce
from speculator import Speculator

class Sigma:
	stat = None
	exchange = None
	
	sigma = None
	lastPrice = None
	conditions = None
	
	pair = None
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
		
		self.sigma, error = stat.getSigmaAndAvg(pair)
		if not self.sigma:
			print(error)
			quit()
		
		res, error = exchange.getTicker([pair])
		if not res:
			print(error)
			quit()
		self.lastPrice = res[pair]['last']
		
		res, error = exchange.getConditions()
		if not res:
			print(error)
			quit()

		self.conditions = res['pairs'][pair]
	
	## 
	#  @brief Brief
	#  
	#  @param [in] self Parameter_Description
	#  @return cascade struct
	#  
	#  @details Details
	#  	
	def createCascade(self):
		print('createCascade is not implement')
		quit()
		
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