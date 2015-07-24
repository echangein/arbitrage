#-*-coding:utf-8-*-

def getAllCombinations(seq = None):
	if not(hasattr(seq, '__iter__')):
		return
	
	seq = list(seq)
	if len(seq) == 1:
		return [seq]
	
	ret = []
	for elem in seq:
		ret.append([elem])
		for sub in getAllCombinations(seq[:seq.index(elem)] + seq[seq.index(elem)+1:]):
			if sub != None:
				ret.append([elem] + sub)
	return ret


seq = 'usd', 'btc', 'ltc', 'nmc', 'nvc'

for s in [s for s in getAllCombinations(seq) if len(s) == 3 and s[0] == 'ltc']:
	print(s)
