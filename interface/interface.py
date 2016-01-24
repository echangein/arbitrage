import urllib2
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
	baseUrl = 'https://btc-e.nz/api/3/'
	hostName = 'btc-e.nz'
	apiLink = '/api/3/'
	tradeUrl = 'https://btc-e.nz/tapi'
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
	
	def getLastErrorMessage(self):
		return self.lastErrorMessage

	def getLastBody(self):
		return self.lastBody
		
	def getLastResult(self):
		return self.lastResult
	
	def sendGet(self, method = None, params = None, tail = None):
		url = self.apiLink + method + '/'
		if hasattr(params, '__contains__'):
			url = url + '-'.join(params) + '/'
		
		if hasattr(tail, '__contains__'):
			url = url + '?'
			for key in tail.keys():
				url = url + key + '=' + str(tail[key]) + '&'
			url = url[:-1]
		
		headers = {'Content-type': 'application/x-www-form-urlencoded'}
		conn = httplib.HTTPSConnection(self.hostName)
		conn.request('GET', url, {}, headers)
		response = conn.getresponse()
		
		self.lastResult = response.status
		self.lastErrorMessage = 'HTTP Error #{0}: {1}'.format(response.status, response.reason)
		
		res = False
		
		if self.lastResult == 200:
			res = json.load(response)
			if res.has_key('error'):
				self.lastErrorMessage = res['error']
				res = False
		
		return res
		
		# ========= will remove =========
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
		
		conn = httplib.HTTPSConnection(self.hostName)
		conn.request('POST', self.tradeLink, params, headers)
		response = conn.getresponse()

		self.lastResult = response.status
		self.lastErrorMessage = 'HTTP Error #{0}: {1}'.format(response.status, response.reason)
		
		res = False
		
		if self.lastResult == 200:
			res = json.load(response)
			if res.has_key('error'):
				self.lastErrorMessage = res['error']
				res = False
		
		return res
		
		# ========= will remove =========
		response = None
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
		
		if response:
			response.close()
		
		return res
