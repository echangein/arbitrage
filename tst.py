#-*-coding:utf-8-*-
#!/usr/bin/env python
import os, json, sys, time

stateFile = '/home/m/morro/dev/state';

#print(len(sys.argv))
#print(sys.argv)
#print(int(time.time()))

key = None

if len(sys.argv) > 1:
	key = sys.argv[1]

print(key)
print(int(time.time()))
print(__file__)

file = open(stateFile, 'w+')
file.write(json.dumps({'key': key, 'time': int(time.time())}))
file.close()
	
	
"""
if os.path.isfile(stateFile):
	print('File exists')
	file = open('selected_trades', 'r+')
	qq = json.load(file)
	file.close()
	print(qq)
else:
	print('File NOT exists')
	
ss = [{'a': 'trolol'}, {'z': 'hell', 's': 34}]
	

os.remove(stateFile)
"""