from threading import Thread
from Authenticator import *
from Connection import *
import datetime


class ServerUtils:
    def __init__(self, port, block_time, time_out):
        self.port = port
        self.users = Authenticator.users
        self.block_time = block_time
        self.time_out = time_out
        # loading the users and passwords
        Authenticator.load_user_password()

    def start(self):
        """
        Start the server and wait for connections.
        """
        # ip = socket.gethostbyname(socket.gethostname())
        ip = 'localhost'
        s = Connection.bind(ip, self.port)
        while True:
            try:
                conn, addr = s.accept()
                Thread(target=self.client_thread, args=(conn, addr)).start()
            except (KeyboardInterrupt, SystemExit):
                s.close()
                print 'Thank you for using this chat room. See you next time!'
                return

    def client_thread(self, s, addr):
        """
        """
        print addr, "is trying to connect."
        (command, data) = Connection.receive(s)
        print 'command: %s' % command
        print 'data: %s' % data

        cmd = command['command']
        cmd_from = command['from']

        if cmd == 'AUTH':
            self.authenticate(s, cmd_from, data, addr)
        elif cmd == 'BROADCAST':
            self.broadcast(s, cmd_from, data)
        elif cmd == 'SEND':
            self.send_message(s, cmd_from, data)
        elif cmd == 'LOGOUT':
            self.logout(s, cmd_from)
        elif cmd == 'WHO':
            self.who(s, cmd_from)
        elif cmd == 'LAST':
            self.last(s, cmd_from, data)

        s.close()

    def authenticate(self, s, cmd_from, data, addr):
        (command, response) = Authenticator.authenticate(cmd_from, data, addr, self.block_time)
        Connection.send(s, command, response)

    def broadcast(self, s, cmd_from, data):
        """
        """
        sender_username = cmd_from
        message = data['message']

        command = {'command': 'OK'}
        response = ''
        sender = self.users[sender_username]
        for username in self.users:
            user = self.users[username]
            if Authenticator.is_online(user):
                if username not in sender['blocked']:
                    if username != sender_username:
                        (ip, port) = Authenticator.user_address(user)
                        try:
                            socket_to = Connection.connect(ip, port)
                            resp_cmd = {'command': 'MESSAGE'}
                            json_message = {'from': sender_username, 'message': message}
                            Connection.send(socket_to, resp_cmd, json_message)
                            socket_to.close()
                        except:
                            print 'Could not deliver to: ' + ip + ' port: ' + str(port)
                else:
                    command = {'command':'WARNING'}
                    response = 'Your message could not be delivered to some recipients'

        Connection.send(s, command, {'message': response})

    def send_message(self, s, cmd_from, data):
        """
        :param s:
        :param cmd_from:
        :param data:
        :return:
        """
        sender_username = cmd_from
        message = data['message']
        message_to = data['message_to']  # tuple of receiving users

        command = {'command': 'OK'}
        response = ''
        sender = self.users[sender_username]
        for username in message_to:
            print username
            print username in self.users
            if username in self.users:  # only send message to those valid users
                user = self.users[username]
                if Authenticator.is_online(user):
                    if username not in sender['blocked']:
                        if username != sender_username:
                            (ip, port) = Authenticator.user_address(user)
                            try:
                                socket_to = Connection.connect(ip, port)
                                resp_cmd = {'command': 'MESSAGE'}
                                json_message = {'from': sender_username, 'message': message}
                                Connection.send(socket_to, resp_cmd, json_message)
                                socket_to.close()
                            except:
                                print 'Could not deliver to: ' + ip + ' port: ' + str(port)
                    else:
                        command = {'command':'WARNING'}
                        response = 'Your message could not be delivered to some recipients'

        Connection.send(s, command, {'message': response})

    def logout(self, s, cmd_from):
        """
        :param s:
        :param cmd_from:
        :return:
        """
        sender_username = cmd_from
        user = self.users[sender_username]
        # (ip, port) = self.user_address(user)
        # command = {'command': 'LOGOUT'}
        # message = {'from': sender_username, 'message': 'You have logged out.'}
        # socket_to = Connection.connect(ip, port)
        # Connection.send(socket_to, command, message)
        # socket_to.close()

        # clear the login information
        user['ip'] = ''
        user['port'] = 0
        user['last_seen'] = datetime.datetime.now()
        user['session'] = False

    def who(self, s, cmd_from):
        """
        :param cmd_from:
        :return:
        """
        online_users = []
        sender_username = cmd_from
        for username in self.users:
            if username != sender_username:
                user = self.users[username]
                if Authenticator.is_online(user):
                    online_users.append(username)

        command = {'command': 'ok'}
        message = {'from': sender_username, 'message': online_users}
        Connection.send(s, command, message)

    def last(self, s, cmd_from, data):
        """
        :param s:
        :param cmd_from:
        :param number:
        :return:
        """
        users = []
        for username in self.users:
            user = self.users[username]
            last_seen = user['last_seen']
            if last_seen is not None:
                if (datetime.datetime.now() - last_seen).total_seconds() <= data['number'] * 60:
                    users.append(username)

        sender_username = cmd_from
        command = {'command': 'ok'}
        message = {'from': sender_username, 'message': users}
        Connection.send(s, command, message)