import time, os, json, MySQLdb

class Stats:
	exchangeId = 1 #btc-e exchange
	depth = 604800
	statLen = 300 # 5 min
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
	
	## 
	#  @brief get std and avg from s_trades table
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] cursor Parameter_Description
	#  @param [in] pairId Parameter_Description
	#  @param [in] startTS Parameter_Description
	#  @param [in] endTS Parameter_Description
	#  @return Return_Description
	#  
	#  @details Details
	#  
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
	#  @brief return 
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] cursor Parameter_Description
	#  @return list of keys and last event TS, or False
	#  
	#  @details using for update stat table
	#  		
	def getStatKeysByPairId(self, cursor, pairId):
		query = u"""
			SELECT
				trade_stat_id, pair_id, type_id last_ts
			FROM
				s_trade_stat_keys
			WHERE
				pair_id = {0}
		""".format(pairId)
		
		cursor.execute(query)
		rows = cursor.fetchall()
		if len(rows) <> 1:
			return False
		
		return rows
	
	## 
	#  @brief Brief
	#  
	#  @param [in] cursor Parameter_Description
	#  @return all stat keys and params
	#  
	#  @details Details
	#  	
	def getStatPairs(self, cursor):
		query = u"""
			SELECT
				trade_stat_id, pair_id, type_id, last_ts
			FROM
				s_trade_stat_keys;
		"""
		
		cursor.execute(query)
		return list(map(tuple, cursor.fetchall()))
	
	def calcStats(self, cursor, pairId, typeId, lastTS = None):
		query = u"""
			SELECT
0			  COUNT(*) cou, 
1			  MIN(price) price_min, 
2			  MAX(price) price_max,
3			  CAST(SUBSTR(MIN(CONCAT(event_ts, '_', price)), 12) AS DECIMAL(16, 8)) price_open,
4			  CAST(SUBSTR(MAX(CONCAT(event_ts, '_', price)), 12) AS DECIMAL(16, 8)) price_close,
5			  SUM(amount) amount_sum,
6			  SUM(amount*amount) amount_2_sum,
7			  SUM(price) price_sum,
8			  SUM(price*price) price_2_sum,
9			  SUM(price*amount) volume_sum,
10			  SUM(price*price*amount*amount) volume_2_sum,
11			  MIN(event_ts) stars_ts,
12			  MAX(event_ts) end_ts,
			  FLOOR(event_ts / {2}) mark,
			  FROM_UNIXTIME(FLOOR(event_ts / {2}) * {2})
			FROM
			  s_trades
			WHERE
			  pair_id = {0} AND type_id = {1}
		""".format(pairId, typeId, self.statLen)
		
		queryTail = u"""
			GROUP BY 
				mark;
		"""
		
		if not lastTS is None:
			queryTail = u"""
					AND event_ts >= {0}
				GROUP BY 
					mark;
			""".format(lastTS)
		
		query += queryTail
		cursor.execute(query)
		return cursor.fetchall()
	
	## 
	#  @brief Brief
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] cursor Parameter_Description
	#  @param [in] statId Parameter_Description
	#  @param [in] lastTS Parameter_Description
	#  @return Return_Description
	#  
	#  @details Details
	#  	
	def isExistsStat(self, cursor, statId, lastTS):
		query = u"""
			SELECT
				COUNT(*)
			FROM
				s_trade_stats
			WHERE
				trade_stat_id = {0}
				AND stars_ts = {1}
		""".format(statId, lastTS)
		cursor.execute(query)
		rows = cursor.fetchall()
		
		if rows[0][0] == 1:
			return True
		
		return False
	
	## 
	#  @brief update last timestamp
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] cursor Parameter_Description
	#  @param [in] statId Parameter_Description
	#  @param [in] lastVals Parameter_Description
	#  @return Return_Description
	#  
	#  @details Details
	#  	
	def updateStatKey(self, cursor, statId, lastVals):
		query = u"""
			UPDATE
				s_trade_stat_keys
			SET 
				last_ts = {0}
			WHERE
				trade_stat_id = {1}
		""".format(lastVals[11], statId)
		cursor.execute(query)
	
	## 
	#  @brief update statistic for specified pair and type
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] cursor Parameter_Description
	#  @param [in] statId Parameter_Description
	#  @param [in] pairId Parameter_Description
	#  @param [in] typeId Parameter_Description
	#  @param [in] lastTS Parameter_Description
	#  @return Return_Description
	#  
	#  @details Details
	#  	
	def updateStat(self, cursor, statId, pairId, typeId, lastTS):
		
		lastVals = None
		for vals in calcStats(cursor, pairId, typeId, lastTS):
			if isExistsStat(cursor, statId, lastTS):
				updateStatDB(cursor, statId, vals)
			else:
				insertStatDB(cursor, statId, vals)
			lastVals = vals
		
		if not lastVals is None:
			updateStatKey(cursor, statId, lastVals)
	
	## 
	#  @brief update stats for all pairs
	#  
	#  @param [in] self Parameter_Description
	#  @return Return_Description
	#  
	#  @details Details
	#  	
	def updateStats(self):
		connect = MySQLdb.connect(
			host = self.host,
			user = self.user,
			passwd = self.pswd,
			db = self.db,
			charset = 'utf8',
			use_unicode = True)

		cursor = connect.cursor()
	
		for statId, pairId, typeId, lastTS in self.getStatPairs(cursor):
			self.updateStat(cursor, statId, pairId, typeId, lastTS)
		
		connect.commit()
		connect.close()
			
	
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
	