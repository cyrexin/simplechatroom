from Connection import *
from threading import Thread


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
            Thread(target=self.listen).start()
            self.started = True
        else:
            raise Exception('The client is not authorized. Should run authenticate() first.')

    def listen(self):
        """
        Thread that listen on port self.port for messages from the server.
        When server connects, start thread self._listen_thread for communication.
        """
        # ip = socket.gethostbyname(socket.gethostname())
        ip = ''
        s = Connection.bind(ip, self.port)
        while True:
           conn, addr = s.accept()
           Thread(target=self.listen_thread, args=(conn, addr)).start()

    def listen_thread(self, s, addr):
        """
        """
        (cmd, data) = Connection.receive(s)

        command = cmd['command']
        print 'command: ' + command

        if command == 'MESSAGE':
            cmd_from = data['from']
            message = data['message']
            print cmd_from + ' said: ' + message
        elif command == 'LOGOUT':
            message = data['message']
            s.close()
            print message
            # sys.exit(0)
            os._exit(0)

        # print('s: ' + s)
        # print('addr: ' + addr)

    def authenticate(self, username, password):
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
            return True
        else:
            print data['message']
            return False

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
        if cmd['command'] != 'OK':
            print data['message']

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
        if cmd['command'] != 'OK':
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