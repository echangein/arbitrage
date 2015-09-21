import urllib2
import urllib
import hmac
import hashlib
import json
import time

class Interface:
	lastErrorMessage = None
	lastResult = None
	lastBody = None
	baseUrl = 'https://btc-e.com/api/3/'
	tradeUrl = 'https://btc-e.com/tapi'
	
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
	
	def getLastErrorMessage(self):
		return self.lastErrorMessage

	def getLastBody(self):
		return self.lastBody
		
	def getLastResult(self):
		return self.lastResult
	
	def sendGet(self, method = None, params = None, tail = None):
		url = self.baseUrl + method + '/'
		if hasattr(params, '__contains__'):
			url = url + '-'.join(params) + '/'
		
		if hasattr(tail, '__contains__'):
			url = url + '?'
			for key in tail.keys():
				url = url + key + '=' + str(tail[key]) + '&'
			url = url[:-1]
		
		try:
			response = urllib2.urlopen(url)
		except urllib2.HTTPError, err:
			self.lastResult = err.code
			self.lastErrorMessage = 'HTTP Error #{0}'.format(err.code)
			res = False
		except urllib2.URLError, err:
			self.lastErrorMessage = err.reason
			res = False
		else:
			self.lastResult = response.getcode()
			res = json.loads(response.read())
			if res.has_key('error'):
				self.lastErrorMessage = res['error']
				res = False
		
		#response.close()
		
		return res

	def sendPost(self, params = None):
		params['nonce'] = self.__getNonce()
		
		params = urllib.urlencode(params)
		H = hmac.new(self.apiSecret, digestmod=hashlib.sha512)
		H.update(params)
		sign = H.hexdigest()
 		headers = {"Content-type": "application/x-www-form-urlencoded", 'Key': self.apiKey, 'Sign': sign}
		
		try:		
			req = urllib2.Request(self.tradeUrl, params, headers)
			response = urllib2.urlopen(req)
		except urllib2.HTTPError, err:
			self.lastResult = err.code
			self.lastErrorMessage = 'HTTP Error #{0}'.format(err.code)
			res = False
		except urllib2.URLError, err:
			#self.lastResult = -1 #err.code
			self.lastErrorMessage = err.reason
			res = False
		else:
			self.lastResult = response.getcode()
			res = json.loads(response.read())
			if res.has_key('error'):
				self.lastErrorMessage = res['error']
				res = False
		
		response.close()
		
		return res
