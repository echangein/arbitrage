import os

if os.name == 'nt':
	import msvcrt
	getch = msvcrt.getch
else:
	import sys, tty, termios
	def getch():
		fd = sys.stdin.fileno()
		oldSettings = termios.tcgetattr(fd)
		tty.setraw(sys.stdin.fileno())
		ch = sys.stdin.read(1)
		termios.tcsetattr(fd, termios.TCSADRAIN, oldSettings)
		return ch
