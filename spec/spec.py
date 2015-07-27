from int import Int
import json

class Spec:
	lastErrorMessage = None
	int = None
	pairs = None
	depth = None
	seqs = []
	
	def __init__(self, baseUrl):
		self.int = Int(baseUrl)
	
	def getLastErrorMessage(self):
		return self.lastErrorMessage

	def checkConnection(self):
		res = self.int.sendGet('info')
		if not res:
			return False
		return True
	
	def loadTradeConditions(self):
		res = self.int.sendGet('info')
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
				self.seqs.append({'trades': seq})
		
		if len(self.seqs)>0:
			return True
		
		self.lastErrorMessage = 'Can\'t choose pair for any sequence'
		return False
	
	def generateTradeAmount(self, startAmount = 0.0):
		pairs = set()
		for row in self.seqs:
			for trade in row['trades']:
				pairs.update([trade['pair']])
				
		if not self.__getDepth(pairs):
			return False
		
		for seq in self.seqs:
			seq['options'] = {'startAmount': startAmount}
			actionAmount = startAmount
			contFlag = True
			for tradeIdx, tradeItem in enumerate(seq['trades']):
				if contFlag:
					if (tradeItem['action']=='sell'):
						actionItem = self.__sell(actionAmount, self.depth[tradeItem['pair']], self.pairs[tradeItem['pair']])
					else:
						actionItem = self.__buy(actionAmount, self.depth[tradeItem['pair']], self.pairs[tradeItem['pair']])
					if not actionItem:
						seq['options']['error'] = 'Can\'t ' + tradeItem['action'] + ' ' + str(actionAmount) + ' in ' + tradeItem['pair']
						contFlag = False
					else:
						tradeItem.update(actionItem)
						actionAmount = actionItem['resultAmount']
			if contFlag:
				seq['options']['resultAmount'] = actionItem['resultAmount']
			
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
		res = self.int.sendGet('depth', pairs, tail)
		if not res:
			return False
			
		self.depth = res
		return True
		