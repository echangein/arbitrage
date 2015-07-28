from interface import Interface
from colorama import init, Fore
import time

class Spec:
	lastErrorMessage = None
	checkTimeout = 2
	int = None
	pairs = None
	depth = None
	seqs = []
	
	
	def __init__(self, key, secret):
		self.int = Interface(key, secret)
	
	def getLastErrorMessage(self):
		return self.lastErrorMessage

	def checkConnection(self):
		res = self.int.sendGet('info')
		if not res:
			self.lastErrorMessage = self.int.getLastErrorMessage()
			return False
		return True
	
	def loadTradeConditions(self):
		res = self.int.sendGet('info')
		if not res:
			self.lastErrorMessage = self.int.getLastErrorMessage()
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
	
	def executeSequence(self, selectedTrades, startAmount, startCurr):
		print('Checking start amount: {0} {1}'.format(startAmount, startCurr))
		if not self.checkAmount(startAmount, startCurr):
			return False
		else:
			print('Funds: ' + Fore.GREEN + 'ok' + Fore.RESET + '.')
			
		for trade in selectedTrades:
			print('Create order: ' + self.formatTrade(trade))
			res = self.createOrder(trade)
			if res is False:
				print(Fore.RED + 'Fail' + Fore.RESET + '.')
				return False
			elif res is None:
				print('Already ' + Fore.GREEN + 'executed' + Fore.RESET + '.')
				trade['order_id'] = 0
				trade['status_id'] = 1
			else:
				print('Wairing for execute.')
				trade['order_id'] = res
				trade['status_id'] = 0
				res = self.waitingOrder(trade['order_id'])
				if res != 1:
					self.lastErrorMessage = 'Order {0} was be cancelled'.format(trade['order_id'])
					return False
		return True
	
	def checkAmount(self, startAmount = 0.0, startCurr = 'usd'):
		res = self.int.sendPost({'method': 'getInfo'})
		if not res:
			self.lastErrorMessage = self.int.getLastErrorMessage()
			return False
			
		if not startCurr in res['return']['funds']:
			self.lastErrorMessage = 'Not have fund: '+startCurr
			return False
		
		if res['return']['funds'][startCurr] < startAmount:
			self.lastErrorMessage = 'Start amount large than {0}'.format(res['funds'][startCurr])
			return False
			
		return True
	
	def waitingOrder(self, orderId = None):
		status = 0
		while status == 0:
			time.sleep(self.checkTimeout)
			status = self.getOrderStatus(orderId)
		
		return status
	
	def getOrderStatus(self, orderId = None):
		res = self.int.sendPost({'method': 'OrderInfo', 'order_id': orderId})
		if not res:
			self.lastErrorMessage = self.int.getLastErrorMessage()
			return False

		if not str(orderId) in res['return']:
			self.lastErrorMessage = 'Order {0} not found'.format(orderId)
			return False
		
		return res['return'][str(orderId)]['status']

	
	def createOrder(self, trade):
		#TODO check values

		res = self.int.sendPost({'method': 'Trade', 'pair': trade['pair'], 'type': trade['action'], 'rate': trade['price'], 'amount': trade['operationAmount']})
		if not res:
			self.lastErrorMessage = self.int.getLastErrorMessage()
			return False
		
		if res['return']['order_id'] == 0:
			return None
		else:
			return res['return']['order_id']
	
	def formatTrade(self, trade):
		if trade['action'] == 'sell':
			prefix = Fore.RED
		else:
			prefix = Fore.GREEN

		return '{0}: {1}{2}\t{3}{4} @ {5}\t= {6}'.format(trade['pair'], prefix, trade['action'], Fore.RESET, trade['operationAmount'], trade['price'], trade['resultAmount'])

	
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
		