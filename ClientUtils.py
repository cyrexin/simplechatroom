from Connection import *
from threading import Thread
import os


class ClientUtils:
    def __init__(self, host, port):
        self.server = {
            'host': host,
            'port': port
        }
        self.addr = ''
        self.username = ''
        self.port = 0
        self.authorized = False

    def invoke(self):
        """
        """
        if self.authorized:
            Thread(target=self.__server_listener).start()
        else:
            raise Exception('The client is not authorized. Should run authenticate() first.')

    def __server_listener(self):
        """
        """
        ip = gethostbyname(gethostname())
        # ip = ''
        try:
            s = Connection.bind(ip, self.port)
            while True:
                conn, addr = s.accept()
                Thread(target=self.__listener_thread, args=(conn, addr)).start()
        except:
            os._exit(1)

    def __listener_thread(self, s, addr):
        """
        This is the thread that client listens to the message from the server.
        """
        data_json = Connection.receive(s)

        instruction = data_json['command']
        # print 'command: ' + command

        if instruction == 'MESSAGE':
            from_user = data_json['from']
            message = data_json['message']
            print '\n' + from_user + ' said: ' + message
        elif instruction == 'LOGOUT':
            message = data_json['message']
            s.close()
            print '\n' + message
            # sys.exit(0)
            os._exit(0)
        elif instruction == 'NOTIFICATION':
            message = data_json['message']
            print '\n' + message

        # print('s: ' + s)
        # print('addr: ' + addr)

    def __create_instruction_json(self, instruction, data):
        """
        All the commands from the client should eventually transform in this json format.
        """
        return {'from': self.username, 'instruction': instruction, 'data': data}

    def login(self, username, password):
        try:
            s = Connection.connect(self.server['host'], self.server['port'])
            data_json = {'instruction': 'LOGIN', 'from': username, 'data': {'password': password}}
            Connection.send(s, data_json)

            data_json = Connection.receive(s)
            data = data_json['response']
            s.close()
            if data_json['command'] == 'OK':
                self.authorized = True
                self.username = username
                self.addr = data['ip']
                self.port = data['port']
                print data['message']

                # if the user has offline messages, print them out
                if len(data['offline_messages']) > 0:
                    print 'You have got some offline messages:'
                    for offline_message in data['offline_messages']:
                        print offline_message['sender'] + ' said: ' + offline_message['message']

                return True
            else:
                print data_json['command'] + ' - ' + data['message']
                return False
        except:
            # print "Failed to connect to the server " + self.server['host'] + " on port: " + str(self.server['port'])
            os._exit(1)

    def broadcast(self, message):
        """
        """
        data = {'message': message}
        s = Connection.connect(self.server['host'], self.server['port'])
        Connection.send(s, self.__create_instruction_json('BROADCAST', data))

        data_json = Connection.receive(s)
        print data_json['command'] + ' - ' + data_json['message']

        s.close()

    def send_message(self, message_to, message):
        """
        :param message_to: a list of usernames that the message is supposed to sent to
        :param message:
        :return:
        """
        data = {'message': message, "message_to": message_to}
        s = Connection.connect(self.server['host'], self.server['port'])
        Connection.send(s, self.__create_instruction_json('SEND', data))

        data_json = Connection.receive(s)
        print data_json['message']

        s.close()

    def logout(self):
        s = Connection.connect(self.server['host'], self.server['port'])
        Connection.send(s, self.__create_instruction_json('LOGOUT', {}))
        s.close()

    def who(self):
        s = Connection.connect(self.server['host'], self.server['port'])
        Connection.send(s, self.__create_instruction_json('WHO', {}))

        data_json = Connection.receive(s)
        message = data_json['message']
        if data_json['command'] == 'OK':
            output = ''
            for username in message:
                output += username + ' '
            print output

        s.close()

    def last(self, number):
        """
        :param number: the unit should be in minute
        :return:
        """
        data = {'number': number}
        s = Connection.connect(self.server['host'], self.server['port'])
        Connection.send(s, self.__create_instruction_json('LAST', data))

        data_json = Connection.receive(s)
        message = data_json['message']
        if data_json['command'] == 'OK':
            output = ''
            for username in message:
                output += username + ' '
            print output

        s.close()

    def check(self, target):
        """
        A simple debug command to print out a specific user's information.
        """
        if target == '':  # if the target if not specified, then check yourself
            target = self.username
        data = {'target': target}
        s = Connection.connect(self.server['host'], self.server['port'])
        Connection.send(s, self.__create_instruction_json('CHECK', data))

        data_json = Connection.receive(s)
        message = data_json['message']
        if data_json['command'] == 'OK':
            print message

        s.close()

    def update_blacklist(self, targets, command):
        data = {'targets': targets}
        s = Connection.connect(self.server['host'], self.server['port'])
        Connection.send(s, self.__create_instruction_json(command.upper(), data))

        data_json = Connection.receive(s)
        print data_json['message']

        s.close()

    def active(self, number):
        """
        :param number: the unit should be in minute
        :return:
        """
        data = {'number': number}
        s = Connection.connect(self.server['host'], self.server['port'])
        Connection.send(s, self.__create_instruction_json('ACTIVE', data))

        data_json = Connection.receive(s)
        message = data_json['message']
        if data_json['command'] == 'OK':
            output = ''
            for username in message:
                output += username + ' '
            print output

        s.close()
