from ServerUtils import *
from Utils import *
import sys


BLOCK_TIME = 60
TIME_OUT = 30 * 60


def main():
    if len(sys.argv) == 2:
        port = sys.argv[1]
        if Utils.is_number(port):
            s = ServerUtils(int(port), BLOCK_TIME, TIME_OUT)
            s.start()
        else:
            print 'Port must be an integer.'
    else:
        print "Invalid argument. Usage: python server.py <port>"

if __name__ == "__main__":
    main()