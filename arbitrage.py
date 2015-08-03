#-*-coding:utf-8-*-
from colorama import init, Fore
init()

from kbrd import getch

def formatTrades(trades):
	res = ''
	for trade in trades:
		if trade['action'] == 'buy':
			res += trade['pair'][:3] + '->'
		else:
			res += trade['pair'][4:] + '->'
			
	return res[:-2]

def reloadDepths(spec, startAmount, startCurrency):
	if not spec.generateTradeAmount(startAmount):
		print('Can\'t ' + Fore.RED + 'generate' + Fore.RESET + ' trade amounts.')
		print('Error: ' + Fore.RED + spec.getLastErrorMessage() + Fore.RESET)
		quit()

	print('Depth ' + Fore.GREEN + 'successfully' + Fore.RESET + ' imported.\n')

	variant = 0
	for trades in spec.seqs:
		if not 'error' in trades['options'] and trades['options']['resultAmount'] > startAmount:
			variant += 1
			print('{0}{1}{2}: {3}->{4}\tprofit: {5}{6}{2}'.format(Fore.YELLOW, variant, Fore.RESET, startCurrency, formatTrades(trades['trades']), Fore.GREEN, trades['options']['resultAmount']))
	
	print('\nPress ' + Fore.YELLOW + 'R' + Fore.RESET + ' to reload trade depth.')
	if variant:
		print('Press ' + Fore.YELLOW + 'number' + Fore.RESET + ' to select trading sequence.')
	else:
		print('Profitable trading sequence ' + Fore.RED + 'not found' + Fore.RESET + '. Try later please.')

	print('Press ' + Fore.YELLOW + 'ESC' + Fore.RESET + ' to exit.')
	
	return

	
import config
from spec import Spec
import os.path

key = None
secret = None

if os.path.isfile('../secrets.txt'):
	f = open('../secrets.txt', 'r')
	key = f.readline().strip()
	secret = f.readline().strip()
	f.close()

curSite = Spec(key, secret)

if not curSite.checkConnection():
	quit()

if not curSite.loadTradeConditions():
	quit()
	
if not curSite.generateTradeSequence(config.startCurrency, config.tradeSequence, config.tradeLength):
	quit()

if curSite.hasSavedTrades():
	selectedTrades = curSite.loadTrades()
	
	key = 0
	cont = True
else:
	if not curSite.waitingDepths(config.startAmount, config.startCurrency):
		quit()
	key = ord(getch())
	cont = False
	
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
				print(curSite.formatTrade(action))
			
			print('\nPress ' + Fore.YELLOW + 'number' + Fore.RESET + ' to select trading sequence.')
			print('Press ' + Fore.YELLOW + 'E' + Fore.RESET + ' to execute trading sequence.')
			print('Press ' + Fore.YELLOW + 'R' + Fore.RESET + ' to reload trade depth.')
			print('Press ' + Fore.YELLOW + 'ESC' + Fore.RESET + ' to exit.')
	
	if (key == ord('r')) or (key == ord('R')):
		selectedTrades = None
		print('')
		reloadDepths(curSite, config.startAmount, config.startCurrency)
	
	if (key == ord('e')) or (key == ord('E') or cont):
		print('')
		if not selectedTrades is None:
			if curSite.executeSequence(selectedTrades, config.startAmount, config.startCurrency, cont):
				print('Trading sequence complete ' + Fore.GREEN + 'successfully' + Fore.RESET + '.')
				curSite.unlinkTrades()
				quit()
			else:
				print('Trading sequence  ' + Fore.RED + 'failed' + Fore.RESET + '.')
				print('Error: ' + Fore.RED + curSite.getLastErrorMessage() + Fore.RESET)
		else:
			print(Fore.RED + 'Select trading sequence' + Fore.RESET + ' please!')
	
	cont = False
	key = ord(getch())
