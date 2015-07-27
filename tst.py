#-*-coding:utf-8-*-
from interface import Interface

f = open('../secrets.txt', 'r')
key = f.readline().strip()
secret = f.readline().strip()
f.close()

myInt = Interface('https://btc-e.com/api/3', 'https://btc-e.com/tapi', key, secret)

res = myInt.sendPost({'method': 'getInfo'})

print res
