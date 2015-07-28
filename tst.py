#-*-coding:utf-8-*-
from spec import Spec


f = open('../secrets.txt', 'r')
key = f.readline().strip()
secret = f.readline().strip()
f.close()

myInt = Spec(key, secret)


print('hello'),
print('- cont')

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
"""