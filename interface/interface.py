import urllib
import hmac
import hashlib
import json
import time

import httplib

class Interface:
	lastErrorMessage = None
	lastResult = None
	lastBody = None
	hostName = 'btc-e.nz'
	apiLink = '/api/3/'
	tradeLink = '/tapi'
	
	apiKey = None
	apiSecret = None
	nonce = None
	
	def __init__(self, apiKey = None, apiSecret = None):
		self.apiKey = apiKey
		self.apiSecret = apiSecret
		self.nonce = int(time.time())
	
	def __getNonce(self):
		self.nonce += 1
		return self.nonce
	
	## 
	#  @brief will be using in speculator class
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] hostName Parameter_Description
	#  @return Return_Description
	#  
	#  @details Details
	#  	
	def setHost(self, hostName = None):
		self.hostName = hostName
	
	## 
	#  @brief will be using in speculator class
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] apiLink Parameter_Description
	#  @return Return_Description
	#  
	#  @details Details
	#  	
	def setApiLink(self, apiLink = None):
		self.apiLink = apiLink
	
	def getLastErrorMessage(self):
		return self.lastErrorMessage

	def getLastBody(self):
		return self.lastBody
		
	def getLastResult(self):
		return self.lastResult
	
	def sendGet(self, method = None, params = None, tail = None, ssh = True):
		url = self.apiLink + method + '/'
		if hasattr(params, '__contains__'):
			url = url + '-'.join(params) + '/'
		
		if hasattr(tail, '__contains__'):
			url = url + '?'
			for key in tail.keys():
				url = url + key + '=' + str(tail[key]) + '&'
			url = url[:-1]
		
		headers = {'Content-type': 'application/x-www-form-urlencoded'}
		if ssh:
			conn = httplib.HTTPSConnection(self.hostName)
		else:
			conn = httplib.HTTPConnection(self.hostName)
			
		try:
			if ssh:
				conn.request('GET', url, {}, headers)
			else:
				conn.request('GET', url)
		except:
			self.lastResult = 0
			self.lastErrorMessage = 'connection to {0} error'.format(self.hostName+url)
			return False
			
		response = conn.getresponse()
		
		self.lastResult = response.status
		self.lastErrorMessage = 'HTTP Error #{0}: {1}'.format(response.status, response.reason)
		
		res = False
		
		if self.lastResult == 200:
			try:
				res = json.load(response)
			except:
				self.lastResult = 0
				self.lastErrorMessage = 'recognize error'
				return False
				
			if res.has_key('error'):
				self.lastErrorMessage = res['error']
				res = False
		
		return res

	def sendPost(self, params = None):
		params['nonce'] = self.__getNonce()
		params = urllib.urlencode(params)
		
		try:
			H = hmac.new(self.apiSecret, digestmod=hashlib.sha512)
		except:
			self.lastResult = 0
			self.lastErrorMessage = 'sendPost: undefined secret key'
			return False
			
		H.update(params)
		sign = H.hexdigest()
 		headers = {"Content-type": "application/x-www-form-urlencoded", 'Key': self.apiKey, 'Sign': sign}
		
		conn = httplib.HTTPSConnection(self.hostName)
		try:
			conn.request('POST', self.tradeLink, params, headers)
		except:
			self.lastResult = 0
			self.lastErrorMessage = 'send POST to {0} error'.format(self.hostName+self.tradeLink)
			return False
			
		response = conn.getresponse()

		self.lastResult = response.status
		self.lastErrorMessage = 'HTTP Error #{0}: {1}'.format(response.status, response.reason)
		
		res = False
		
		if self.lastResult == 200:
			try:
				res = json.load(response)
			except:
				self.lastResult = 0
				self.lastErrorMessage = 'recognize error'
				return False
		
			if res.has_key('error'):
				self.lastErrorMessage = res['error']
				res = False
		
		return res
