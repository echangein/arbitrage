#-*-coding:utf-8-*-
from colorama import init, Fore, Back, Style
init()

import config
from spec import Spec

curSite = Spec(config.baseUrl)

if not curSite.checkConnection():
	print(Fore.RED + 'Can\'t connect' + Fore.RESET + ' to ' + curSite.baseUrl)
	print('Error: ' + Fore.RED + curSite.getLastErrorMessage() + Fore.RESET)
	quit()

print('Server answered ' + Fore.GREEN + 'correctly' + Fore.RESET + '.')

if not curSite.loadTradeConditions():
	print(Fore.RED + 'Can\'t load trade conditions' + Fore.RESET + ' from ' + curSite.baseUrl)
	print('Error: ' + Fore.RED + curSite.getLastErrorMessage() + Fore.RESET)
	quit()

print('Trade conditions is ' + Fore.GREEN + 'loading' + Fore.RESET + '.')
	
if not curSite.generateTradeSequence(config.startCurrency, config.tradeSequence, config.tradeLength):
	print('Can\'t ' + Fore.RED + 'generate' + Fore.RESET + ' trade sequence.')
	print('Error: ' + Fore.RED + curSite.getLastErrorMessage() + Fore.RESET)
	quit()

print('Trade sequences ' + Fore.GREEN + 'successfully' + Fore.RESET + ' generated.')

for item in curSite.seqs:
	print(item)

"""	
if not curSite.generateTradeAmount(config.startAmount):
	print('Can\'t ' + Fore.RED + 'generate' + Fore.RESET + ' trade amounts.')
	print('Error: ' + Fore.RED + curSite.getLastErrorMessage() + Fore.RESET)
	quit()

print('')

for action in curSite.actions:
	if action['action'] == 'sell':
		prefix = Fore.RED
	else:
		prefix = Fore.GREEN
	print('{0}: {1}{2}\t{3}{4} @ {5}\t= {6}'.format(action['pair'], prefix, action['action'], Fore.RESET, action['operationAmount'], action['price'], action['resultAmount']))
"""
	
#print u'Press ENTER to exit'
#raw_input()
