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
		if len(rows) == 0:
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
			  COUNT(*) cou, 
			  MIN(price) price_min, 
			  MAX(price) price_max,
			  CAST(SUBSTR(MIN(CONCAT(event_ts, '_', price)), 12) AS DECIMAL(16, 8)) price_open,
			  CAST(SUBSTR(MAX(CONCAT(event_ts, '_', price)), 12) AS DECIMAL(16, 8)) price_close,
			  SUM(amount) amount_sum,
			  SUM(amount*amount) amount_2_sum,
			  SUM(price) price_sum,
			  SUM(price*price) price_2_sum,
			  SUM(price*amount) volume_sum,
			  SUM(price*price*amount*amount) volume_2_sum,
			  MIN(event_ts) start_ts,
			  MAX(event_ts) end_ts,
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
		if lastTS is None:
			return False
	
		query = u"""
			SELECT
				COUNT(*)
			FROM
				s_trade_stats
			WHERE
				trade_stat_id = {0}
				AND start_ts = {1}
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
	#  @brief Brief
	#  
	#  @param [in] self Parameter_Description
	#  @param [in] cursor Parameter_Description
	#  @param [in] statId Parameter_Description
	#  @param [in] vals Parameter_Description
	#  @return Return_Description
	#  
	#  @details Details
	#  
	def updateStatDB(self, cursor, statId, vals):
		query = u"""
			UPDATE
				s_trade_stats
			SET 
				end_ts = {1[12]},
				cou = {1[0]},
				price_open = {1[3]},
				price_min = {1[1]},
				price_max = {1[2]},
				price_close = {1[4]},
				amount_sum = {1[5]},
				amount_2_sum = {1[6]},
				price_sum = {1[7]},
				price_2_sum = {1[8]},
				volume_sum = {1[9]},
				volume_2_sum = {1[10]}
			WHERE
				trade_stat_id = {0} AND start_ts = {1[11]}
		""".format(statId, vals)
		cursor.execute(query)

	def insertStatDB(self, cursor, statId, vals):
		query = u"""
			INSERT INTO
				s_trade_stats
				(trade_stat_id, start_ts, end_ts, cou, price_open, price_min, price_max, price_close, amount_sum, amount_2_sum, price_sum, price_2_sum, volume_sum, volume_2_sum)
			VALUES (
				{0}, {1[11]}, {1[12]}, {1[0]}, {1[3]}, {1[1]}, {1[2]}, {1[4]}, {1[5]}, {1[6]}, {1[7]}, {1[8]}, {1[9]}, {1[10]})
		""".format(statId, vals)
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
		for vals in self.calcStats(cursor, pairId, typeId, lastTS):
			if self.isExistsStat(cursor, statId, lastTS):
				self.updateStatDB(cursor, statId, vals)
			else:
				self.insertStatDB(cursor, statId, vals)
			lastVals = vals
		
		if not lastVals is None:
			self.updateStatKey(cursor, statId, lastVals)
	
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
	
	def getPriceSigma(self, cursor, statIds, startTS, endTS):
		query = u"""
			SELECT
				SUM(cou) cou, SUM(price_sum) price, SUM(price_2_sum) price_2
			FROM
				s_trade_stats
			WHERE
				trade_stat_id IN ({0}) AND start_ts >= {1} AND end_ts <= {2}
		""".format(', '.join(str(id) for id in statIds), startTS, endTS)
		
		cursor.execute(query)
		rows = cursor.fetchall()
		if len(rows) <> 1:
			return False, 'getPriceSigma: rows conut is not 1'
		
		return abs((rows[0][2] - rows[0][1] * rows[0][1] / float(rows[0][0])) / float(rows[0][0])) ** 0.5, True
		
		#return (rows[0][2] / float(rows[0][0]) - (rows[0][1] / float(rows[0][0])) ** 2) ** 0.5, True
		
	
	def getSigma(self, pair = None, depth = None):
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
		
		rows = self.getStatKeysByPairId(cursor, pairId)
		if rows is False:
			return False, 'StatKeyIds not found'
		statIds = []
		for row in rows:
			statIds.append(row[0])
		
		if depth is None or not depth.isdigit():
			depth = self.depth
		
		dt = int(time.time())
		
		sigma, message = self.getPriceSigma(cursor, statIds, dt - depth, dt)
		
		connect.close()
		
		return sigma, message
