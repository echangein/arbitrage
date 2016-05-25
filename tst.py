#!/usr/bin/env python
#-*-coding:utf-8-*-

from kbrd import getch
import time, os, json, sys

from speculator import Speculator

spec = Speculator()
print('enter depth');
depth = raw_input()
print(spec.getSigmaAndAvg('ltc_rur', depth))

quit()

pair = 'ltc_rur'
silent = False

profitPercent = 1.2
startPercent = 0.9
deepPercent = 19
totalInvest = 5000
activeOrdersCount = 5

profitPrecision = 4

import config
from cascade import Cascade
import os.path, json


cascadeFile = 'trades_btc_usd_btc_usd_key'

dirname, filename = os.path.split(os.path.abspath(__file__))
cascadeFileName = dirname + '/../' + cascadeFile
cascadeFileName = dirname + '/../bool'

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

cascade = engine.createCascade(17.99, 666) #43.93, 666
engine.printCascade(cascade)
