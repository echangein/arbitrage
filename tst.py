#-*-coding:utf-8-*-
import os, json

if os.path.isfile('selected_trades'):
	print('File exists')
	file = open('selected_trades', 'r+')
	qq = json.load(file)
	file.close()
	print(qq)
else:
	print('File NOT exists')
	
ss = [{'a': 'trolol'}, {'z': 'hell', 's': 34}]
	
file = open('selected_trades', 'w+')
file.write(json.dumps(ss))
file.close()

os.remove('selected_trades')