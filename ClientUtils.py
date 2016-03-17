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
        self.started = False

    def start(self):
        """
        """
        if self.authorized:
            Thread(target=self.listen_server).start()
            self.started = True
        else:
            raise Exception('The client is not authorized. Should run authenticate() first.')

    def listen_server(self):
        """
        """
        ip = gethostbyname(gethostname())
        # ip = ''
        try:
            s = Connection.bind(ip, self.port)
            while True:
               conn, addr = s.accept()
               Thread(target=self.listen_thread, args=(conn, addr)).start()
        except:
            os._exit(1)

    def listen_thread(self, s, addr):
        """
        """
        (cmd, data) = Connection.receive(s)

        command = cmd['command']
        # print 'command: ' + command

        if command == 'MESSAGE':
            from_user = data['from']
            message = data['message']
            print '\n' + from_user + ' said: ' + message
        elif command == 'LOGOUT':
            message = data['message']
            s.close()
            print '\n' + message
            # sys.exit(0)
            os._exit(0)

        # print('s: ' + s)
        # print('addr: ' + addr)

    def authenticate(self, username, password):
        try:
            s = Connection.connect(self.server['host'], self.server['port'])
            command = {'command': 'AUTH', 'from': username}
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

    def create_command(self, command):
        """
        """

        return {'command': command, 'from': self.username}

    def broadcast(self, message):
        """
        """
        data = {'message': message}
        s = Connection.connect(self.server['host'], self.server['port'])
        Connection.send(s, self.create_command('BROADCAST'), data)

        (cmd, data) = Connection.receive(s)
        print cmd['command'] + ' - ' + data['message']

        s.close()

    def send_message(self, message_to, message):
        """
        :param message_to:
        :param message:
        :return:
        """
        data = {'message': message, "message_to": message_to}
        s = Connection.connect(self.server['host'], self.server['port'])
        Connection.send(s, self.create_command('SEND'), data)

        (cmd, data) = Connection.receive(s)
        print data['message']

        s.close()

    def logout(self):
        s = Connection.connect(self.server['host'], self.server['port'])
        Connection.send(s, self.create_command("LOGOUT"), {})
        s.close()

    def who(self):
        s = Connection.connect(self.server['host'], self.server['port'])
        Connection.send(s, self.create_command("WHO"), {})

        (cmd, data) = Connection.receive(s)
        message = data['message']
        if cmd['command'] != 'OK':
            output = ''
            for username in message:
                output += username + ' '
            print output

        s.close()

    def last(self, number):
        s = Connection.connect(self.server['host'], self.server['port'])
        Connection.send(s, self.create_command("LAST"), {'number': number})

        (cmd, data) = Connection.receive(s)
        message = data['message']
        if cmd['command'] != 'OK':
            output = ''
            for username in message:
                output += username + ' '
            print output

        s.close()

    def check(self, target):
        if target == '':  # if the target if not specified, then check yourself
            target = self.username
        s = Connection.connect(self.server['host'], self.server['port'])
        Connection.send(s, self.create_command("CHECK"), {'target': target})

        (cmd, data) = Connection.receive(s)
        message = data['message']
        if cmd['command'] != 'OK':
            print message

        s.close()
