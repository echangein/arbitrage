#!/usr/bin/env python
#-*-coding:utf-8-*-

from kbrd import getch
import time, os, json, sys
from spec import Spec

totalPrecision = 8
profitPrecision = 5
pair = 'ltc_btc'
silent = False

profitPercent = 1
startPercent = 0.5
deepPercent = 18
totalInvest = 0.3725
activeOrdersCount = 5

import config
from spec import Spec
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
engine.setProfitPrecision(profitPrecision)

engine.setActiveOrdersCount(activeOrdersCount)

cascade = engine.createCascade()

engine.printCascade(cascade)
