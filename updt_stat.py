#!/usr/bin/env python
#-*-coding:utf-8-*-

import os, json
from stats import Stats

dirName, ownFileName = os.path.split(os.path.abspath(__file__))
configFileName = dirName + '/../conf.cfg'
if os.path.isfile(configFileName):
	file = open(configFileName, 'r+')
	config = json.load(file)
	file.close()
	if 'db' in config:
		db = config['db']
	if 'user' in config:
		user = config['user']
	if 'pswd' in config:
		pswd = config['pswd']

dbStat = Stats(db, user, pswd)
dbStat.updateStats()