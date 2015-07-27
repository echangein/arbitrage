import urllib2
import json

class Int:
	lastErrorMessage = None
	lastResult = None
	lastBody = None
	baseUrl = None
	
	def __init__(self, baseUrl):
		self.baseUrl = baseUrl
		if baseUrl[-1:] <> '/':
			self.baseUrl = baseUrl + '/'
			return
			
		self.baseUrl = baseUrl
	
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

		response = urllib2.urlopen(url)
		self.lastResult = response.getcode()
		res = json.loads(response.read())
		if res.has_key('error'):
			self.lastErrorMessage = res['error']
			return False
		
		return res
