#-*-coding:utf-8-*-
from interface import Interface

"""
f = open('../secrets.txt', 'r')
key = f.readline().strip()
secret = f.readline().strip()
f.close()

myInt = Interface('https://btc-e.com/api/3', 'https://btc-e.com/tapi', key, secret)

res = myInt.sendPost({'method': 'getInfo'})

print res
"""

import os, sys, tty, termios
if os.name == 'nt':
	from msvcrt import getch
else:
	import sys, tty, termios
	def getch():
		fd = sys.stdin.fileno()
		oldSettings = termios.tcgetattr(fd)
		tty.setraw(sys.stdin.fileno())
		ch = sys.stdin.read(1)
		termios.tcsetattr(fd, termios.TCSADRAIN, oldSettings)
		return ch

while True:
	key = ord(getch())
	print(key)
	
	if key == 27:
		break

print('finish')
