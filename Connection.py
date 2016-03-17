from socket import *
import json


class Connection:
    @staticmethod
    def bind(host, port):
        try:
            s = socket(AF_INET, SOCK_STREAM)
            s.bind((host, port))
            s.listen(5)
            # print 'The host is: %s. The port is %s.' % (host, port)
            return s
        except error, msg:
            # print "Failed to bind on port: " + str(port)
            print msg[1]
            raise

    @staticmethod
    def connect(host, port):
        """
        """
        try:
            s = socket(AF_INET, SOCK_STREAM)
            s.connect((host, port))
            return s
        except:
            print "Failed to connect to the server " + host + " on port: " + str(port)
            raise

    @staticmethod
    def send(s, command, data):
        """
        """
        all = [command, data]
        try:
            data_json = json.dumps(all)
            # print 'data_json: ' + data_json
            s.send("%d\n" % len(data_json))
            s.send(data_json)
        except:
            print "Failed to send data:"
            print all
            raise


    @staticmethod
    def receive(s):
        """
        """
        try:
            str_length = ''
            char = s.recv(1)
            # print 'char: %s' % char
            while char != '\n':
                str_length += char
                char = s.recv(1)
            total = int(str_length)

            data = s.recv(total)
            data_json = json.loads(data)

            return data_json
        except:
            print "Failed to receive data."
            raise

    # @staticmethod
    # def clientHandler(conn, addr):
    #     print addr, "is Connected"
    #     while 1:
    #         data = conn.recv(1024)
    #         if not data:
    #             break
    #         print "Received Message", repr(data)