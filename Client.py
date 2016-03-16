from ClientCLI import *
from Utils import *
import sys


def main():
    if len(sys.argv) == 3:
        server = sys.argv[1]
        port = sys.argv[2]

        if Utils.is_number(port):
            c = ClientCLI(server, int(port))
            c.start()
        else:
            print 'Port must be an integer.'
    else:
        print "Invalid argument. Usage: python client.py <server> <port>"


if __name__ == "__main__":
    main()