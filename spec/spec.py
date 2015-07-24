import urllib2
import json

class Spec:
	lastErrorMessage = None
	lastResult = None
	lastBody = None
	baseUrl = None
	pairs = None
	depth = None
	seq = []
	actions = []
	
	def __init__(self, baseUrl):
		self.baseUrl = baseUrl
		if baseUrl[-1:] <> '/':
			self.baseUrl = baseUrl + '/'
			return
			
		self.baseUrl = baseUrl
	
	def getLastErrorMessage(self):
		return self.lastErrorMessage

	def getLastBody(self):
		return self.lastBody
		
	def getLastResult(self):
		return self.lastResult
	
	def checkConnection(self):
		res = self.__sendGet('info')
		if not res:
			return False
		return True
	
	def loadTradeConditions(self):
		res = self.__sendGet('info')
		if not res:
			return False
			
		self.pairs = res['pairs']
		return True
	
	def generateTradeSequence(self, seq = None):
		if len(seq) < 2:
			self.lastErrorMessage = 'Not enough values in tradeSequence at config.py'
			return False
		
		self.seq = []
		for idx, val in enumerate(seq):
			if idx + 1 == len(seq):
				idx = -1
			seqItem = self.__searchPair(val, seq[idx+1])
			if not seqItem:
				self.lastErrorMessage = 'Not found pair for ' + val + ' and ' + seq[idx+1]
				return False
			self.seq.append(seqItem)
		
		return True
	
	def generateTradeAmount(self, startAmount = 0.0):
		keys = []
		for seqItem in self.seq:
			keys.append(seqItem['pair'])
			
		if not self.__getDepth(keys):
			return False
		
		self.actions = []
		actionAmount = startAmount
		for seqItem in self.seq:
			if (seqItem['action']=='sell'):
				actionItem = self.__sell(actionAmount, self.depth[seqItem['pair']], self.pairs[seqItem['pair']])
			else:
				actionItem = self.__buy(actionAmount, self.depth[seqItem['pair']], self.pairs[seqItem['pair']])
			
			if not actionItem:
				self.lastErrorMessage = 'Can\'t ' + seqItem['action'] + ' ' + str(actionAmount) + ' in ' + seqItem['pair']
				return False
			
			actionItem['pair'] = seqItem['pair']
			self.actions.append(actionItem)
			actionAmount = actionItem['resultAmount']
		
		return True
	
	def __sell(self, amount = None, depth = None, condition = None):
		price = round(depth['asks'][0][0]-10**(-condition['decimal_places']), 8)
		operationAmount = amount
		if operationAmount < condition['min_amount']:
			return False
		resultAmount = round(amount * price * (100-condition['fee']) / 100, 8);
		return {'operationAmount': operationAmount, 'price': price, 'resultAmount': resultAmount, 'action': 'sell'}
	
	def __buy(self, amount = None, depth = None, condition = None):
		price = round(depth['bids'][0][0]+10**(-condition['decimal_places']), 8)
		operationAmount = round(amount / price, 8)
		if operationAmount < condition['min_amount']:
			return False
		resultAmount = round(amount / price * (100-condition['fee']) / 100, 8);
		return {'operationAmount': operationAmount, 'price': price, 'resultAmount': resultAmount, 'action': 'buy'}
		
	def __searchPair(self, cur1, cur2):
		for pair in self.pairs.keys():
			if ((pair[:3] == cur1) and (pair[-3:] == cur2)) or ((pair[:3] == cur2) and (pair[-3:] == cur1)):
				action = 'sell'
				if pair[:3] == cur2:
					action = 'buy'
				return {'pair': pair, 'action': action}
		return False
	
	def __getDepth(self, pairs = None, tail = {'limit': 10}):
		res = self.__sendGet('depth', pairs, tail)
		if not res:
			return False
			
		self.depth = res
		return True
		
	
	def __sendGet(self, method = None, params = None, tail = None):
		url = self.baseUrl + method + '/'
		if hasattr(params, '__contains__'):
			url = url + '-'.join(params) + '/'
		
		if hasattr(tail, '__contains__'):
			url = url + '?'
			for key in tail.keys():
				url = url + key + '=' + str(tail[key]) + '&'
			url = url[:-1]

		response = urllib2.urlopen(url)
		self.lastResult = response.getcode()
		res = json.loads(response.read())
		if res.has_key('error'):
			self.lastErrorMessage = res['error']
			return False
		
		return res
