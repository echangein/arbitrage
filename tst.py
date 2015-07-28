#-*-coding:utf-8-*-
from spec import Spec


f = open('../secrets.txt', 'r')
key = f.readline().strip()
secret = f.readline().strip()
f.close()

myInt = Spec(key, secret)

#res = myInt.sendPost({'method': 'getInfo'})
#print res

trade = {'pair': 'btc_usd', 'action': 'buy', 'price': 10.0, 'operationAmount': 0.33}
orderId = myInt.createOrder(trade)
if not orderId:
	print(myInt.getLastErrorMessage())
else:
	print('orderId: {0}'.format(orderId))

orderStatus = myInt.getOrderStatus(orderId)
if orderStatus is False:
	print(myInt.getLastErrorMessage())
else:
	print('orderStatus: {0}'.format(orderStatus))

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