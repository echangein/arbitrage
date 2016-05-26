cascadeFileName = 'usd_rur.csc'

if isExistsCascadeFile(cascadeFileName):
	cascadeStruct = loadCascadeFile(cascadeFileName)
else
	cascadeStruct = createCascadeStruct()
	
cascadeStruct, error = checkOrdersStatus(cascadeStruct)#can be errors
if error:
	reportCheckOrdersStatusError()
	saveCascadeFile(cascadeFileName, cascadeStruct)
	quit()

# ================== restart cascade ================== #
if not inWork(cascadeStruct) and needRestart(cascadeStruct):
	cascadeStruct, error = cancelOrders(cascadeStruct)
	if error:
		reportCancelOrdersError()
		saveCascadeFile(cascadeFileName, cascadeStruct)
		quit()
		
	cascadeStruct = createCascadeStruct()
	cascadeStruct, error = checkOrdersStatus(cascadeStruct)#can be errors
	if error:
		reportCheckOrdersStatusError()
		saveCascadeFile(cascadeFileName, cascadeStruct)
		quit()
# ================== restart cascade ================== #

# ================== cascade get profit ================== #
if hasProfit(cascadeStruct): #sell order complete
	reportProfit(cascadeStruct)
	if hasPartialExecution(cascadeStruct): # need check executed next buy order
		cascadeStruct = resizeAfterProfit(cascadeStruct)
	else:
		cascadeStruct, error = cancelOrders(cascadeStruct)
		if error:
			reportCancelOrdersError()
			saveCascadeFile(cascadeFileName, cascadeStruct)
			quit()
		if hasParnet(cascadeStruct): # for reverse
			restoreParent(cascadeStruct)
			quit()
		else:
			removeCascadeFile(cascadeFileName)
			quit()
# ================== cascade get profit ================== #

# ================== create revers cascade ================== #
# ================== create revers cascade ================== #

# ================== create order sequence ================== #
cascadeStruct, error = createOrders(cascadeStruct)
if error:
	reportCreateOrdersError()
cascadeStruct = shiftOrders(cascadeStruct)

cascadeStruct, error = moveProfitOrder(cascadeStruct)
if error:
	reportMoveProfitOrderError()
# ================== create order sequence ================== #

saveCascadeFile(cascadeFileName, cascadeStruct)