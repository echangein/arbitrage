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
s = False
if s is None:
	print('s is None')
elif s is False:
	print('s is false')
else:
	print('s is another')

s = None
if s is None:
	print('s is None')
elif s is False:
	print('s is false')
else:
	print('s is another')

s = 0	
if s is None:
	print('s is None')
elif s is False:
	print('s is false')
else:
	print('s is another')
