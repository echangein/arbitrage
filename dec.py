#-*-coding:utf-8-*-
firstRusLetter = u'а'[0]

def printAbc(abc, shift = 10):
	idx = 0
	for letter in abc:
		print(letter), 
		print(abc[(idx + shift) % len(abc)])
		idx += 1

abcRus = []
for x in xrange(0, 32):
	abcRus.append(unichr(ord(firstRusLetter) + x))

abcRus = abcRus[:6] + [u'ё'] + abcRus[6:]

printAbc(abcRus)


print('\nfinish')