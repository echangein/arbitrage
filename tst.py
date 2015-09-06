#!/usr/bin/env python
#-*-coding:utf-8-*-

import os, json, sys, time

dirname, filename = os.path.split(os.path.abspath(__file__))
stateFileName = 'state';
stateFile = dirname + '/../' + stateFileName;

statusFile = '/../status1'
statusFileName = dirname + statusFile

def getPrevStat():
	ret = 'waiting'
	if os.path.isfile(statusFileName):
		f = open(statusFileName, 'r')
		ret = f.readline().strip()
		f.close()
	return ret

def setPrevStat(val):
	f = open(statusFileName, 'w+')
	f.write(val)
	f.close()

#setPrevStat('low')
#print(getPrevStat())

print('Hello')
#for 
print(sys.argv[1:])



for key, val in [s.split('=') for s in sys.argv[1:]]:
	print(key, val)

print(json.dumps({'hi': True}))
	
	
#print(dict(sys.argv[1:]))
