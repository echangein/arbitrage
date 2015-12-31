#!/usr/bin/env python
#-*-coding:utf-8-*-

from kbrd import getch
import time, os, json, sys
#from spec import Spec


pair = 'ltc_rur'
silent = False

profitPercent = 1.1
startPercent = 0.9
deepPercent = 20
totalInvest = 5000
activeOrdersCount = 5

profitPrecision = 2

import config
#from spec import Spec
from cascade import Cascade
import os.path

key = None
secret = None

engine = Cascade(key, secret, silent)
engine.setPair(pair)

engine.setProfitPercent(profitPercent)
engine.setStartPercent(startPercent)
engine.setDeepPercent(deepPercent)
engine.setTotalInvest(totalInvest)
engine.setActiveOrdersCount(activeOrdersCount)

engine.setProfitPrecision(profitPrecision)

cascade = engine.createCascade(17.99258339, 666) #

#print(cascade)
#print(cascade[0]['sellOrder']['operationAmount'])
engine.printCascade(cascade)

if len(cascade) > 0 and 'options' in cascade[0]:
	print('cascade is revers')