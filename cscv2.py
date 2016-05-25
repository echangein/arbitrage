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

if needRestartCascadeStruct(cascadeStruct):
	cascadeStruct = createCascadeStruct()
	cascadeStruct, error = checkOrdersStatus(cascadeStruct)#can be errors
	if error:
		reportCheckOrdersStatusError()
		saveCascadeFile(cascadeFileName, cascadeStruct)
		quit()
	
if hasProfit(cascadeStruct): #sell order complete
	reportProfit(cascadeStruct)
	removeCascadeFile(cascadeFileName) # need check executed next buy order
	quit()
	
if not waitingProfit(cascadeStruct): #sell order is partial executed
	cascadeStruct, error = createOrder(cascadeStruct)
	if error:
		reportCreateOrdersError()
	cascadeStruct = shiftOrders(cascadeStruct)

saveCascadeFile(cascadeFileName, cascadeStruct)