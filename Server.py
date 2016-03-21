from ServerUtils import *
from Utils import *
import sys
import os


BLOCK_TIME = os.getenv('BLOCK_TIME', 60)
TIME_OUT = os.getenv('TIME_OUT', 30 * 60)


def main():
    # print BLOCK_TIME
    # print TIME_OUT
    if len(sys.argv) == 2:
        port = sys.argv[1]
        if Utils.is_number(port):
            server = ServerUtils(int(port), BLOCK_TIME, TIME_OUT)
            server.start()
        else:
            print 'Port must be an integer.'
    else:
        print "The command is invalid. Usage: python server.py <port>"

if __name__ == "__main__":
    main()