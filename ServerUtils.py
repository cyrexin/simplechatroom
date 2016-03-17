from threading import Thread
from Authenticator import *
from Connection import *
import datetime
import time
import os


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
        try:
            s = Connection.bind(ip, self.port)
            print 'Server (' + ip + ':' + str(self.port) + ') has started....'
            Thread(target=self.check_client, args=()).start()
            while True:
                try:
                    conn, addr = s.accept()
                    Thread(target=self.listen_client, args=(conn, addr)).start()
                except (KeyboardInterrupt, SystemExit):
                    for username in self.users:  # log all users out
                        user = self.users[username]
                        if Authenticator.is_online(user):
                            (ip, port) = Authenticator.user_address(user)
                            command = {'command': 'LOGOUT'}
                            message = {'from': 'SERVER', 'message': 'You have been disconnected by the server because the server is shutting down.'}
                            socket_to = Connection.connect(ip, port)
                            Connection.send(socket_to, command, message)
                            socket_to.close()
                            self.logout(username, True)

                    s.close()
                    print '\nThank you for using this chat room. All connected users have been disconnected. See you next time!'
                    sys.exit(0)
        except:
            os._exit(1)

    def listen_client(self, s, addr):
        """
        """
        print addr, "is trying to connect."
        (command, data) = Connection.receive(s)
        print 'command: %s' % command
        print 'data: %s' % data

        cmd = command['command']
        from_user = command['from']

        if cmd == 'AUTH':
            self.authenticate(s, from_user, data, addr)
        elif cmd == 'BROADCAST':
            self.broadcast(s, from_user, data)
            Authenticator.users[from_user]['last_seen'] = datetime.datetime.now()  # should update user's last_seen if the user has done something
        elif cmd == 'SEND':
            self.send_message(s, from_user, data)
            Authenticator.users[from_user]['last_seen'] = datetime.datetime.now()
        elif cmd == 'LOGOUT':
            self.logout(from_user)
        elif cmd == 'WHO':
            self.who(s, from_user)
            Authenticator.users[from_user]['last_seen'] = datetime.datetime.now()
        elif cmd == 'LAST':
            self.last(s, from_user, data)
            Authenticator.users[from_user]['last_seen'] = datetime.datetime.now()
        elif cmd == 'CHECK':
            self.check(s, from_user, data)
            Authenticator.users[from_user]['last_seen'] = datetime.datetime.now()

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


    def authenticate(self, s, from_user, data, addr):
        (command, response) = Authenticator.authenticate(from_user, data, addr, self.block_time)
        Connection.send(s, command, response)

    def broadcast(self, s, from_user, data):
        """
        """
        sender_username = from_user
        message = data['message']

        command = {'command': 'OK'}
        response = 'You message has been broadcast!'
        sender = self.users[sender_username]
        for username in self.users:
            user = self.users[username]
            if Authenticator.is_online(user):
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
            # else:  # store as an offline message
            #     offline_message = {'sender': sender_username, 'message': message}
            #     user['offline_messages'].append(offline_message)

        Connection.send(s, command, {'message': response})

    def send_message(self, s, from_user, data):
        """
        :param s:
        :param from_user:
        :param data:
        :return:
        """
        sender_username = from_user
        message = data['message']
        message_to = data['message_to']  # tuple of receiving users

        status = 'OK'  #{'command': 'OK'}
        response = ''  #'You message has been sent!'
        sender = self.users[sender_username]
        for username in message_to:
            print username
            print username in self.users
            if username in self.users:  # only send message to those valid users
                user = self.users[username]
                if Authenticator.is_online(user):
                    if username != sender_username:  # should not self message to yourself
                        (ip, port) = Authenticator.user_address(user)
                        try:
                            socket_to = Connection.connect(ip, port)
                            resp_cmd = {'command': 'MESSAGE'}
                            json_message = {'from': sender_username, 'message': message}
                            Connection.send(socket_to, resp_cmd, json_message)
                            socket_to.close()

                            # status = 'OK'
                            response += 'To ' + username + ': ' + 'You message has been sent!\n'
                        except:
                            print 'Could not deliver to: ' + ip + ' port: ' + str(port)
                            # status = 'ERROR'
                            response += 'To ' + username + ': ' + 'You message has failed to be sent!\n'

                        # Connection.send(s, {'command': status}, {'message': response})
                    else:
                        # status = 'WARNING'
                        response += 'To ' + username + ': ' + 'You cannot send message to yourself.\n'
                        # Connection.send(s, {'command': status}, {'message': response})
                else:  # store as an offline message
                    self.__store_offline_message(user, username, sender_username, message)
                    # status = 'OK'
                    response += 'To ' + username + ': ' + username + ' is not online. You message has been stored as an offline message.\n'
                    # Connection.send(s, {'command': status}, {'message': response})
            else:
                # status = 'ERROR'
                response += 'To ' + username + ': ' + 'User ' + username + ' is not found.\n'
                # Connection.send(s, {'command': status}, {'message': response})

        Connection.send(s, {'command': status}, {'message': response})

    def __store_offline_message(self, user, username, sender_username, message):
        offline_message = {'sender': sender_username, 'message': message}
        user['offline_messages'].append(offline_message)

        filename = 'offline_message_' + username + '.txt'
        with open(filename, 'a') as myfile:
            json.dump(offline_message, myfile)
            myfile.write('\n')

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

    def who(self, s, from_user):
        """
        :param from_user:
        :return:
        """
        online_users = []
        sender_username = from_user
        for username in self.users:
            if username != sender_username:
                user = self.users[username]
                if Authenticator.is_online(user):
                    online_users.append(username)

        command = {'command': 'ok'}
        message = {'from': sender_username, 'message': online_users}
        Connection.send(s, command, message)

    def last(self, s, from_user, data):
        """
        :param s:
        :param from_user:
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

        sender_username = from_user
        command = {'command': 'ok'}
        message = {'from': sender_username, 'message': users}
        Connection.send(s, command, message)

    def check(self, s, from_user, data):
        """
        :param s:
        :param from_user:
        :param data:
        :return:
        """
        target = data['target']
        command = {'command': 'ok'}
        sender_username = from_user
        if target in self.users:
            user = self.users[target]
            if Authenticator.is_online(user):
                message = {'from': sender_username, 'message': str(user)}
            else:
                message = {'from': sender_username, 'message': 'User ' + target + ' is not online.'}
        else:
            message = {'from': sender_username, 'message': 'User ' + target + ' is not found.'}
        Connection.send(s, command, message)