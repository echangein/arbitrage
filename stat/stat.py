import time, os, json, MySQLdb

class Stat:
	depth = 604800
	host = 'localhost'

	## 
	#  @brief Brief
	#  
	#  @param [in] self Parameter_Description
	#  @return Return_Description
	#  
	#  @details Details
	#  
	def __init__(self, db, user, pswd):
		self.db = db
		self.user = user
		self.pswd = pswd

	## 
	#  @brief Brief
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] pair Parameter_Description
	#  @param [in] depth Parameter_Description
	#  @return sigma, avg or False, errorMessage
	#  
	#  @details Details
	#  		
	def getSigmaAndAvg(self, pair = None, depth = None):
		connect = MySQLdb.connect(
			host = self.host,
			user = self.user,
			passwd = self.pswd,
			db = self.db,
			charset = 'utf8',
			use_unicode = True)

		cursor = connect.cursor()
		
		query = u"""
			SELECT
			  goods_id, group_id, goods_name
			FROM
			  all_goods
			WHERE
			  LOWER(goods_name) LIKE LOWER('%{0}%')
		""".format(signature)
		
		cursor.execute(query)
		rows = cursor.fetchall()
			
		connect.close()
	
		req = {'pair': pair}
		if not depth is None and depth.isdigit():
			req['depth'] = depth
		
		res = self.int.sendGet('stat', None, req, False)
		if not res:
			return False, self.int.getLastErrorMessage()
			
		return res['res']['sigma'], res['res']['avg']