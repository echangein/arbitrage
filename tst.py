#-*-coding:utf-8-*-
#!/usr/bin/env python
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

setPrevStat('low')
#print(getPrevStat())