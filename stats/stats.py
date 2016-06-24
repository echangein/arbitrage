import time, os, json, MySQLdb

class Stats:
	exchangeId = 1 #btc-e exchange
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
	#  @brief return pairId by alias
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] cursor Parameter_Description
	#  @param [in] pair Parameter_Description
	#  @return pairId or False
	#  
	#  @details Details
	#  
	def getPairId(self, cursor, pair):
		query = u"""
			SELECT 
				p.pair_id, p.pair_name, CONCAT(mc.alias, '_', sc.alias) pair_alias
			FROM 
				s_pairs p
				JOIN s_currencys mc ON mc.cur_id = p.main_cur_id
				JOIN s_currencys sc ON sc.cur_id = p.sec_cur_id
			WHERE
				p.exch_id = {0}
			HAVING
				pair_alias = '{1}'
		""".format(self.exchangeId, pair)
		
		cursor.execute(query)
		rows = cursor.fetchall()
		
		if len(rows) <> 1:
			return False
		
		return rows[0][0]

	def getStat(self, cursor, pairId, startTS, endTS):
		query = u"""
			SELECT
				STD(price) sigma, AVG(price) avg
			FROM
				s_trades
			WHERE
				pair_id = {0} AND event_ts >= {1} AND event_ts <= {2}
		""".format(pairId, startTS, endTS)
		
		cursor.execute(query)
		rows = cursor.fetchall()
		if len(rows) <> 1:
			return False, 'rows conut is not 1'
		
		return rows[0][0], rows[0][1]
		
		
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
		
		if not isinstance(pair, basestring):
			return False, 'pair param is not string'
			
		pairId = self.getPairId(cursor, pair)
		
		if pairId is False:
			return False, 'uncknown pair: {0}'.format(pair)
		
		if depth is None or not depth.isdigit():
			depth = self.depth
		
		dt = int(time.time())
		
		sigma, avg = self.getStat(cursor, pairId, dt - depth, dt)
		
		connect.close()
		
		return sigma, avg
		