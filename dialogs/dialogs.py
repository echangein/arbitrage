from colorama import init, Fore

class Dialogs:
	
	def getCheckConnectionError(self, message = None):
		ret = Fore.RED + 'Can\'t connect' + Fore.RESET + ' to server.\nError: ' + Fore.RED + str(message) + Fore.RESET
		return ret

	def getCheckConnectionSuccess(self):
		ret = 'Server answered ' + Fore.GREEN + 'correctly' + Fore.RESET + '.'
		return ret

	def	getLoadTradeConditionsError(self, message = None):
		ret = Fore.RED + 'Can\'t load trade conditions' + Fore.RESET + ' from server.\nError: ' + Fore.RED + message + Fore.RESET
		return ret

	def getLoadTradeConditionsSuccess(self):
		ret = 'Trade conditions is ' + Fore.GREEN + 'loading' + Fore.RESET + '.'
		return ret
	
	def getGenerateTradeSequenceError(self, message = None):
		ret = 'Can\'t ' + Fore.RED + 'generate' + Fore.RESET + ' trade sequence.\nError: ' + Fore.RED + message + Fore.RESET
		return ret
	
	def getGenerateTradeSequenceSuccess(self):
		ret = 'Trade sequences ' + Fore.GREEN + 'successfully' + Fore.RESET + ' generated.'
		return ret
		
	def getLoadTradesMessage(self):
		ret = 'Found uncompleted trading sequence.'
		return ret
		
	def getGenerateTradeAmountError(self, message = None):
		ret = 'Can\'t ' + Fore.RED + 'generate' + Fore.RESET + ' trade amounts.\nError: ' + Fore.RED + message + Fore.RESET
		return ret
	
	def getGenerateTradeAmountSuccess(self):
		ret = 'Depth ' + Fore.GREEN + 'successfully' + Fore.RESET + ' imported.'
		return ret
	
	def formatTrade(self, trade):
		if trade['action'] == 'sell':
			prefix = Fore.RED
		else:
			prefix = Fore.GREEN

		return '{0}: {1}{2}\t{3}{4}\t@ {5}\t= {6}'.format(trade['pair'], prefix, trade['action'], Fore.RESET, trade['operationAmount'], trade['price'], trade['resultAmount'])

	def formatTrades(self, trades):
		res = ''
		for trade in trades:
			if trade['action'] == 'buy':
				res += trade['pair'][:3] + '->'
			else:
				res += trade['pair'][4:] + '->'
				
		return res[:-2]

	def formatSequencyTrades(self, variant, startCurrency, trades, resultAmount):
		ret = '{0}{1}{2}: {3}->{4}\tprofit: {5}{6}{2}'.format(Fore.YELLOW, variant, Fore.RESET, startCurrency, self.formatTrades(trades), Fore.GREEN, resultAmount)
		return ret