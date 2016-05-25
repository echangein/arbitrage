from interface import Interface
import time, os, json

class Speculator:
	host = 'speculator.in'
	apiLink = '/ax/'

	## 
	#  @brief Brief
	#  
	#  @param [in] self Parameter_Description
	#  @return Return_Description
	#  
	#  @details Details
	#  
	def __init__(self):
		self.int = Interface()
		self.int.setHost(self.host)
		self.int.setApiLink(self.apiLink)

	## 
	#  @brief Brief
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] pair Parameter_Description
	#  @param [in] depth Parameter_Description
	#  @return Return_Description
	#  
	#  @details Details
	#  		
	def getSigmaAndAvg(self, pair = None, depth = None):
		return 0, 0