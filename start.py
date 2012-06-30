import sys, os, time

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print "Usage: ./start.py <server/client>"
		sys.exit()
	else:
		if sys.argv[1] == 'server':
			from server import server
			server.start()
		elif sys.argv[1] == "client":
			from client import main