from interface import Interface
from dialogs import Dialogs
from colorama import init, Fore
import time, os, json



class Spec:
	dialogs = None
	lastErrorMessage = None
	checkTimeout = 2
	silent = False
	int = None
	pairs = None
	tickers = None
	depth = None
	seqs = []
	
	
	def __init__(self, key = None, secret = None, silent = False):
		self.int = Interface(key, secret)
		self.dialogs = Dialogs()
		self.formatTrade = self.dialogs.formatTrade
		self.silent = silent
	
	def getLastErrorMessage(self):
		return self.lastErrorMessage

	def checkConnection(self):
		res = self.int.sendGet('info')
		if not res:
			self.lastErrorMessage = self.int.getLastErrorMessage()
			if not self.silent:
				print self.dialogs.getCheckConnectionError(self.lastErrorMessage)
			return False
		
		if not self.silent:
			print self.dialogs.getCheckConnectionSuccess()
		return True
	
	def loadTradeConditions(self):
		res = self.int.sendGet('info')
		if not res:
			self.lastErrorMessage = self.int.getLastErrorMessage()
			if not self.silent:
				print self.dialogs.getLoadTradeConditionsError(self.lastErrorMessage)
			return False
			
		self.pairs = res['pairs']
		if not self.silent:
			print self.dialogs.getLoadTradeConditionsSuccess()
		return True
	
	def loadTickers(self, pairs = ['btc_rur']):
		res = self.int.sendGet('ticker', pairs)
		if not res:
			self.lastErrorMessage = self.int.getLastErrorMessage()
			if not self.silent:
				print self.dialogs.getLoadTickersError(self.lastErrorMessage)
			return False
			
		self.tickers = res
		if not self.silent:
			print self.dialogs.getLoadTickersSuccess()
		return True
	
	def generateTradeSequence(self, start, seq = None, length = 3):
		if length < 2:
			self.lastErrorMessage = 'tradeLength at config.py too small'
			if not self.silent:
				print self.dialogs.getGenerateTradeSequenceError(self.lastErrorMessage)
			return False
		
		if len(seq) < length:
			self.lastErrorMessage = 'Not enough values in tradeSequence at config.py'
			if not self.silent:
				print self.dialogs.getGenerateTradeSequenceError(self.lastErrorMessage)
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
			if not self.silent:
				print self.dialogs.getGenerateTradeSequenceSuccess()
			return True
		
		self.lastErrorMessage = 'Can\'t choose pair for any sequence'
		if not self.silent:
			print self.dialogs.getGenerateTradeSequenceError(self.lastErrorMessage)
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
						#self.lastErrorMessage = seq['options']['error']
						contFlag = False
					else:
						tradeItem.update(actionItem)
						actionAmount = actionItem['resultAmount']
			if contFlag:
				seq['options']['resultAmount'] = actionItem['resultAmount']
			
		return True
	
	def executeSequence(self, selectedTrades, startAmount = None, startCurr = None, cont = False):
		if not cont:
			print('Checking start amount: {0} {1}'.format(startAmount, startCurr)),
			if not self.checkAmount(startAmount, startCurr):
				print('')
				return False
			else:
				print('- ' + Fore.GREEN + 'ok' + Fore.RESET + '.')
			
		for trade in selectedTrades:
			if not 'order_id' in trade:
				print('Create order: ' + self.formatTrade(trade))
				orderId = self.createOrder(trade)
			else:
				print('Exist order: ' + self.formatTrade(trade))
				orderId = trade['order_id']
			
			if orderId is False:
				print(Fore.RED + 'Fail' + Fore.RESET + '.')
				return False
			elif orderId is None:
				print('Already ' + Fore.GREEN + 'executed' + Fore.RESET + '.')
				trade['order_id'] = 0
				trade['status_id'] = 1
			else:
				print('Waiting for execute'),
				trade['order_id'] = orderId
				trade['status_id'] = 0
				self.saveTrades(selectedTrades)
				res = self.waitingOrder(trade['order_id'])
				if res != 1:
					self.lastErrorMessage = 'Order {0} was be cancelled'.format(trade['order_id'])
					print('')
					return False
				trade['status_id'] = res
				print('- ' + Fore.GREEN + 'ok' + Fore.RESET + '.')
			self.saveTrades(selectedTrades)
		return True
	
	def saveTrades(self, trades):
		file = open('selected_trades', 'w+')
		file.write(json.dumps(trades))
		file.close()
	
	def loadTrades(self):
		file = open('selected_trades', 'r+')
		trades = json.load(file)
		file.close()
		
		if not self.silent:
			print self.dialogs.getLoadTradesMessage()
			for action in selectedTrades:
				print(self.dialogs.formatTrade(action))
		
		return trades
		
	def unlinkTrades(self):
		if os.path.isfile('selected_trades'):
			os.remove('selected_trades')
	
	def hasSavedTrades(self):
		return os.path.isfile('selected_trades')
	
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
		res = self.int.sendPost({'method': 'Trade', 'pair': trade['pair'], 'type': trade['action'], 'rate': trade['price'], 'amount': trade['operationAmount']})
		if not res:
			self.lastErrorMessage = self.int.getLastErrorMessage()
			return False
		
		if res['return']['order_id'] == 0:
			return None
		else:
			return res['return']['order_id']
	
	
	def cancelOrder(self, orderId = None):
		res = self.int.sendPost({'method': 'CancelOrder', 'order_id': orderId})
		if not res:
			self.lastErrorMessage = self.int.getLastErrorMessage()
			return False

		if not 'order_id' in res['return']:
			self.lastErrorMessage = 'Order {0} not found'.format(orderId)
			return False
		
		return True
	
	def waitingDepths(self, startAmount, startCurrency, minProfit = 0.00):
		print('Waiting for profitable depths.')
		execute = True
		while execute:
			if not self.generateTradeAmount(startAmount):
				if not self.silent:
					print(self.dialogs.getGenerateTradeAmountError(self.lastErrorMessage))
				return False
			
			if not self.silent:
				print self.dialogs.getGenerateTradeAmountSuccess()
			
			variant = 0
			for trades in self.seqs:
				if not 'error' in trades['options'] and trades['options']['resultAmount'] > startAmount + minProfit:
					variant += 1
					print(self.dialogs.formatSequencyTrades(variant, startCurrency, trades['trades'], trades['options']['resultAmount']))
			
			if variant:
				execute = False
			else:
				time.sleep(self.checkTimeout)
		
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
		#price = round((depth['bids'][0][0]+depth['asks'][0][0])/2, condition['decimal_places'])
		price = round(depth['asks'][0][0]-10**(-condition['decimal_places']), 8)
		operationAmount = amount
		if operationAmount < condition['min_amount']:
			return False
		resultAmount = round(amount * price * (100-condition['fee']) / 100, 8);
		return {'operationAmount': operationAmount, 'price': price, 'resultAmount': resultAmount, 'action': 'sell'}
	
	def __buy(self, amount = None, depth = None, condition = None):
		#price = round((depth['bids'][0][0]+depth['asks'][0][0])/2, condition['decimal_places'])
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
		
