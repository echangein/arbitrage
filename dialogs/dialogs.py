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