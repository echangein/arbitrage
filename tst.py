#-*-coding:utf-8-*-
#!/usr/bin/env python
import os, json, sys, time

dirname, filename = os.path.split(os.path.abspath(__file__))
stateFileName = 'state';
stateFile = dirname + '/../' + stateFileName;

key = None

if len(sys.argv) > 1:
	key = sys.argv[1]

print(key)
print(int(time.time()))
print('__file__: {0}'.format(__file__))
print('repr(__file__): {0}'.format(repr(__file__)))
print('os.getcwd(): {0}'.format(os.getcwd()))

dirname, filename = os.path.split(os.path.abspath(__file__))
print "\nrunning from", dirname
print "file is", filename

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