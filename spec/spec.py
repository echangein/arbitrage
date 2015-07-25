import urllib2
import json

class Spec:
	lastErrorMessage = None
	lastResult = None
	lastBody = None
	baseUrl = None
	pairs = None
	depth = None
	seqs = []
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
	
	def generateTradeSequence(self, start, seq = None, length = 3):
		if length < 2:
			self.lastErrorMessage = 'tradeLength at config.py too small'
			return False
		
		if len(seq) < length:
			self.lastErrorMessage = 'Not enough values in tradeSequence at config.py'
			return False
			
		#allSeq = [items for items in __getAllCombinations(seq) if len(s) == length and s[0] == start]
		
		self.seqs = []
		for seqItem in [items for items in self.__getAllCombinations(seq) if len(items) == length and items[0] == start]:
			success = True
			seq = []
			for idx, val in enumerate(seqItem):
				if success:
					if idx + 1 == len(seqItem):
						idx = -1
					pair = self.__searchPair(val, seqItem[idx+1])
					if not pair:
						success = False
					seq.append(pair)
			if success:
				self.seqs.append(seq)
		
		if len(self.seqs)>0:
			return True
		
		self.lastErrorMessage = 'Can\'t choose pair for any sequence'
		return False
	
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
	
	def __getAllCombinations(self, seq = None):
		if not(hasattr(seq, '__iter__')):
			return
		
		seq = list(seq)
		if len(seq) == 1:
			return [seq]
		
		ret = []
		for elem in seq:
			ret.append([elem])
			for sub in self.__getAllCombinations(seq[:seq.index(elem)] + seq[seq.index(elem)+1:]):
				if sub != None:
					ret.append([elem] + sub)
		return ret
	
	
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
