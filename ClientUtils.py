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

    def start(self):
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
        (command, data) = Connection.receive(s)

        instruction = command['command']
        # print 'command: ' + command

        if instruction == 'MESSAGE':
            from_user = data['from']
            message = data['message']
            print '\n' + from_user + ' said: ' + message
        elif instruction == 'LOGOUT':
            message = data['message']
            s.close()
            print '\n' + message
            # sys.exit(0)
            os._exit(0)

        # print('s: ' + s)
        # print('addr: ' + addr)

    def login(self, username, password):
        try:
            s = Connection.connect(self.server['host'], self.server['port'])
            command = {'instruction': 'LOGIN', 'from': username}
            data = {'password': password}
            Connection.send(s, command, data)

            (cmd, data) = Connection.receive(s)
            s.close()
            if cmd['command'] == 'OK':
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
                print data['message']
                return False
        except:
            # print "Failed to connect to the server " + self.server['host'] + " on port: " + str(self.server['port'])
            os._exit(1)

    def __create_instruction_json(self, instruction):
        """
        All the commands from the client should eventually transform in this json format.
        """
        return {'from': self.username, 'instruction': instruction}

    def broadcast(self, message):
        """
        """
        data = {'message': message}
        s = Connection.connect(self.server['host'], self.server['port'])
        Connection.send(s, self.__create_instruction_json('BROADCAST'), data)

        (cmd, data) = Connection.receive(s)
        print cmd['command'] + ' - ' + data['message']

        s.close()

    def send_message(self, message_to, message):
        """
        :param message_to: a list of usernames that the message is supposed to sent to
        :param message:
        :return:
        """
        data = {'message': message, "message_to": message_to}
        s = Connection.connect(self.server['host'], self.server['port'])
        Connection.send(s, self.__create_instruction_json('SEND'), data)

        (cmd, data) = Connection.receive(s)
        print data['message']

        s.close()

    def logout(self):
        s = Connection.connect(self.server['host'], self.server['port'])
        Connection.send(s, self.__create_instruction_json("LOGOUT"), {})
        s.close()

    def who(self):
        s = Connection.connect(self.server['host'], self.server['port'])
        Connection.send(s, self.__create_instruction_json("WHO"), {})

        (cmd, data) = Connection.receive(s)
        message = data['message']
        if cmd['command'] != 'OK':
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
        s = Connection.connect(self.server['host'], self.server['port'])
        Connection.send(s, self.__create_instruction_json("LAST"), {'number': number})

        (cmd, data) = Connection.receive(s)
        message = data['message']
        if cmd['command'] != 'OK':
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
        s = Connection.connect(self.server['host'], self.server['port'])
        Connection.send(s, self.__create_instruction_json("CHECK"), {'target': target})

        (cmd, data) = Connection.receive(s)
        message = data['message']
        if cmd['command'] != 'OK':
            print message

        s.close()

    def update_blacklist(self, targets, command):
        data = {'targets': targets}
        s = Connection.connect(self.server['host'], self.server['port'])
        Connection.send(s, self.__create_instruction_json(command.upper()), data)

        (cmd, data) = Connection.receive(s)
        print data['message']

        s.close()
