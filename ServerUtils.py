from threading import Thread
from Authenticator import *
from Connection import *
import datetime
import time


class ServerUtils:
    CHECK_FREQUENCY = 10

    def __init__(self, port, block_time, time_out):
        self.port = port
        self.users = Authenticator.users
        self.block_time = block_time
        self.time_out = time_out
        # load the users and passwords
        Authenticator.load_user_password()

    def start(self):
        """
        Start the server and wait for connections.
        """
        # ip = socket.gethostbyname(socket.gethostname())
        ip = 'localhost'
        s = Connection.bind(ip, self.port)
        print 'Server (' + ip + ':' + str(self.port) + ') has started....'
        Thread(target=self.check_client, args=()).start()
        while True:
            try:
                conn, addr = s.accept()
                Thread(target=self.listen_client, args=(conn, addr)).start()
            except (KeyboardInterrupt, SystemExit):
                s.close()
                print 'Thank you for using this chat room. See you next time!'
                return

    def listen_client(self, s, addr):
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
            Authenticator.users[cmd_from]['last_seen'] = datetime.datetime.now()  # should update user's last_seen if the user has done something
        elif cmd == 'SEND':
            self.send_message(s, cmd_from, data)
            Authenticator.users[cmd_from]['last_seen'] = datetime.datetime.now()
        elif cmd == 'LOGOUT':
            self.logout(cmd_from)
        elif cmd == 'WHO':
            self.who(s, cmd_from)
            Authenticator.users[cmd_from]['last_seen'] = datetime.datetime.now()
        elif cmd == 'LAST':
            self.last(s, cmd_from, data)
            Authenticator.users[cmd_from]['last_seen'] = datetime.datetime.now()
        elif cmd == 'CHECK':
            self.check(s, cmd_from, data)
            Authenticator.users[cmd_from]['last_seen'] = datetime.datetime.now()

        s.close()

    def check_client(self):
        while True:
            print 'Checking idle users...'
            for username in self.users:
                user = self.users[username]
                if Authenticator.is_online(user):  # only check the online users
                    last_seen = user['last_seen']
                    if last_seen:
                        idle = (datetime.datetime.now() - last_seen).total_seconds()
                        if idle > self.time_out:  # automatically log the user out
                            (ip, port) = Authenticator.user_address(user)
                            command = {'command': 'LOGOUT'}
                            message = {'from': 'SERVER', 'message': 'You have been disconnected by the server due to being inactive.'}
                            socket_to = Connection.connect(ip, port)
                            Connection.send(socket_to, command, message)
                            socket_to.close()

                            # clear the login information
                            self.logout(username, True)
                            print username + ' has been disconnected.'

            print 'Done checking.'
            time.sleep(self.CHECK_FREQUENCY)


    def authenticate(self, s, cmd_from, data, addr):
        (command, response) = Authenticator.authenticate(cmd_from, data, addr, self.block_time)
        Connection.send(s, command, response)

    def broadcast(self, s, cmd_from, data):
        """
        """
        sender_username = cmd_from
        message = data['message']

        command = {'command': 'OK'}
        response = 'You message has been broadcast!'
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
            else:  # store as an offline message
                offline_message = {'sender': sender_username, 'message': message}
                user['offline_messages'].append(offline_message)

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
        response = 'You message has been sent!'
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
                else:  # store as an offline message
                    offline_message = {'sender': sender_username, 'message': message}
                    user['offline_messages'].append(offline_message)

        Connection.send(s, command, {'message': response})

    def logout(self, username, is_forced=False):
        """
        :param s:
        :param username:
        :param is_forced:
        :return:
        """
        user = self.users[username]
        # (ip, port) = self.user_address(user)
        # command = {'command': 'LOGOUT'}
        # message = {'from': sender_username, 'message': 'You have logged out.'}
        # socket_to = Connection.connect(ip, port)
        # Connection.send(socket_to, command, message)
        # socket_to.close()

        # clear the login information
        user['ip'] = ''
        user['port'] = 0
        if not is_forced:
            user['last_seen'] = datetime.datetime.now()
        user['session'] = False
        user['login_attempts'] = 0

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
        :param data:
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

    def check(self, s, cmd_from, data):
        """
        :param s:
        :param cmd_from:
        :param data:
        :return:
        """
        target = data['target']
        command = {'command': 'ok'}
        sender_username = cmd_from
        if target in self.users:
            user = self.users[target]
            if Authenticator.is_online(user):
                message = {'from': sender_username, 'message': str(user)}
            else:
                message = {'from': sender_username, 'message': 'User ' + target + ' is not online.'}
        else:
            message = {'from': sender_username, 'message': 'User ' + target + ' is not found.'}
        Connection.send(s, command, message)