from interface import Interface
import time, os, json


class Btce:
	int = None

	## 
	#  @brief Brief
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] key Parameter_Description
	#  @param [in] secret Parameter_Description
	#  @return Return_Description
	#  
	#  @details Details
	#  
	def __init__(self, key = None, secret = None):
		self.int = Interface(key, secret)
	## 
	#  @brief get exchange trade conditions
	#  
	#  @param [in] self Parameter_Description
	#  @return result, 'ok' or False, 'error message'
	#  
	#  @details Details
	#  
	def getConditions(self):
		res = self.int.sendGet('info')
		if not res:
			return False, self.int.getLastErrorMessage()
			
		return res, 'ok'
		
	## 
	#  @brief Brief
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] pairs array of pair alias
	#  @return Return_Description
	#  
	#  @details Details
	#  	
	def getTicker(self, pairs = None):
		if not hasattr(pairs, '__contains__'):
			return False, 'pairs must be array'
			
		res = self.int.sendGet('ticker', pairs)
		if not res:
			return False, self.int.getLastErrorMessage()
			
		return res, 'ok'
		
	## 
	#  @brief Brief
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] pair Parameter_Description
	#  @param [in] type Parameter_Description
	#  @param [in] rate Parameter_Description
	#  @param [in] amount Parameter_Description
	#  @return Return_Description
	#  
	#  @details Details
	#  		
	def createOrder(self, pair = None, type = None, rate = None, amount = None):
		res = self.int.sendPost({'method': 'Trade', 'pair': pair, 'type': type, 'rate': rate, 'amount': amount})
		if not res:
			return False, self.int.getLastErrorMessage()
		return res['return'], 'ok'
	
	## 
	#  @brief Brief
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] pair only one pair
	#  @return Return_Description
	#  
	#  @details Details
	#  		
	def getActiveOrders(self, pair = None):
		params = {'method': 'ActiveOrders'}
		if isinstance(pair, str) or isinstance(pair, unicode):
			params['pair'] = pair
		
		res = self.int.sendPost(params)
		if not res:
			return False, self.int.getLastErrorMessage()
			
		return res['return'], 'ok'
	
	## 
	#  @brief Brief
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] orderId Parameter_Description
	#  @return Return_Description
	#  
	#  @details 0 - active, 1 - excuted, 2 - canceled, 3 - canceled but partial executed
	#  		
	def getOrderInfo(self, orderId = None):
		res = self.int.sendPost({'method': 'OrderInfo', 'order_id': orderId})
		if not res:
			return False, self.int.getLastErrorMessage()
		return res['return'], 'ok'
	
	## 
	#  @brief Brief
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] orderId Parameter_Description
	#  @return Return_Description
	#  
	#  @details Details
	#  	
	def cancelOrder(self, orderId = None):
		res = self.int.sendPost({'method': 'CancelOrder', 'order_id': orderId})
		if not res:
			return False, self.int.getLastErrorMessage()
			
		return res['return'], 'ok'
