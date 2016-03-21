from ClientCLI import *
from Utils import *
import sys


def main():
    if len(sys.argv) == 3:
        server = sys.argv[1]
        port = sys.argv[2]

        if Utils.is_number(port):
            client = ClientCLI(server, int(port))
            client.start()
        else:
            print 'Port must be an integer.'
    else:
        print "The command is invalid. Usage: python client.py <server> <port>"


if __name__ == "__main__":
    main()