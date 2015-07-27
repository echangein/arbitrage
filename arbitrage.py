#-*-coding:utf-8-*-
from colorama import init, Fore #, Back, Style
from msvcrt import getch
init()

def formatTrades(trades):
	res = ''
	for trade in trades:
		if trade['action'] == 'buy':
			res += trade['pair'][:3] + '->'
		else:
			res += trade['pair'][4:] + '->'
			
	return res[:-2]

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

if not curSite.generateTradeAmount(config.startAmount):
	print('Can\'t ' + Fore.RED + 'generate' + Fore.RESET + ' trade amounts.')
	print('Error: ' + Fore.RED + curSite.getLastErrorMessage() + Fore.RESET)
	quit()

print('Depth ' + Fore.GREEN + 'successfully' + Fore.RESET + ' imported.\n')

variant = 0
for trades in curSite.seqs:
	if not 'error' in trades['options'] and trades['options']['resultAmount'] > config.startAmount:
		variant += 1
		print('{0}{1}{2}: {3}->{4}\tprofit: {5}{6}{2}'.format(Fore.YELLOW, variant, Fore.RESET, config.startCurrency, formatTrades(trades['trades']), Fore.GREEN, trades['options']['resultAmount']))
		
if not(variant):
	print('Profitable trading sequence ' + Fore.RED + 'not found' + Fore.RESET + '. Try later please.')
	quit()

print('\nPress ' + Fore.YELLOW + 'number' + Fore.RESET + ' to select trading sequence to show detail or press ' + Fore.YELLOW + 'ESC' + Fore.RESET + ' to exit.')

key = ord(getch())
while key != 27:
	if (key >= ord('1')) and (key <= ord('9')):
		variant = 0
		selectedTrades = None
		for trades in curSite.seqs:
			if trades['options']['resultAmount'] > config.startAmount:
				variant += 1
				if variant == (key - ord('0')):
					selectedTrades = trades['trades']
		if selectedTrades <> None:
			print('\nStart amount: {0} {1}'.format(config.startAmount, config.startCurrency))
			for action in selectedTrades:
				if action['action'] == 'sell':
					prefix = Fore.RED
				else:
					prefix = Fore.GREEN

				print('{0}: {1}{2}\t{3}{4} @ {5}\t= {6}'.format(action['pair'], prefix, action['action'], Fore.RESET, action['operationAmount'], action['price'], action['resultAmount']))
			
			print('\nPress ' + Fore.YELLOW + 'number' + Fore.RESET + ' to select trading sequence to show detail or press ' + Fore.YELLOW + 'ESC' + Fore.RESET + ' to exit.')

	key = ord(getch())