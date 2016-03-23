from threading import Thread
from Authenticator import *
from Connection import *
import datetime
import time
import os


class ServerUtils:
    CHECK_FREQUENCY = 10  # this is frequency that the server checks if a client should be disconnected

    def __init__(self, port, block_time, time_out):
        self.port = port
        self.users = Authenticator.users
        self.block_time = block_time
        self.time_out = time_out
        # load the users and passwords
        Authenticator.load_user_password()

    def start(self):
        """
        1. Bind the server to the specified port.
        2. Open a thread to listen from the clients.
        3. Open another thread to constantly check if a client has been idle for a specific time.
        """
        ip = gethostbyname(gethostname())
        # ip = 'localhost'
        try:
            s = Connection.bind(ip, self.port)
            print 'Server (' + ip + ':' + str(self.port) + ') has started....'
            Thread(target=self.__client_idle_checker, args=()).start()

            while True:
                try:
                    conn, addr = s.accept()
                    Thread(target=self.__client_listener, args=(conn, addr)).start()
                except KeyboardInterrupt, msg:
                    for username in self.users:  # log all users out
                        user = self.users[username]
                        if Authenticator.is_online(user):
                            (ip, port) = Authenticator.get_user_address(user)
                            data_json = {'command': 'LOGOUT', 'from': 'SERVER', 'message': 'You have been disconnected by the server because the server is shutting down.'}
                            socket_to = Connection.connect(ip, port)
                            Connection.send(socket_to, data_json)
                            socket_to.close()
                            self.logout(username, True)

                    s.close()
                    print '\nThank you for using this chat room. All connected users have been disconnected. See you next time!'
                    os._exit(0)

        except:
            os._exit(1)

    def __client_listener(self, s, addr):
        """
        This method listens the command from a client.
        """
        print addr, "is trying to connect."
        data_json = Connection.receive(s)
        data = data_json['data']
        print 'data_json: %s' % data_json
        print 'data: %s' % data

        from_user = data_json['from']
        instruction = data_json['instruction']

        if instruction == 'LOGIN':
            self.authenticate(s, from_user, data, addr)
        elif instruction == 'BROADCAST':
            self.broadcast(s, from_user, data)
            Authenticator.users[from_user]['last_active'] = datetime.datetime.now()  # should update user's last_active if the user has done something
        elif instruction == 'SEND':
            self.send_message(s, from_user, data)
            Authenticator.users[from_user]['last_active'] = datetime.datetime.now()
        elif instruction == 'LOGOUT':
            self.logout(from_user)
        elif instruction == 'WHO':
            self.who(s, from_user)
            Authenticator.users[from_user]['last_active'] = datetime.datetime.now()
        elif instruction == 'LAST':
            self.last(s, from_user, data)
            Authenticator.users[from_user]['last_active'] = datetime.datetime.now()
        elif instruction == 'CHECK':
            self.check(s, from_user, data)
            Authenticator.users[from_user]['last_active'] = datetime.datetime.now()
        elif instruction == 'BLACKLIST':
            self.blacklist(s, from_user, data)
            Authenticator.users[from_user]['last_active'] = datetime.datetime.now()
        elif instruction == 'WHITELIST':
            self.whitelist(s, from_user, data)
            Authenticator.users[from_user]['last_active'] = datetime.datetime.now()
        elif instruction == 'ACTIVE':
            self.active(s, from_user, data)
            Authenticator.users[from_user]['last_active'] = datetime.datetime.now()

        s.close()

    def __client_idle_checker(self):
        """
        This listener constantly (defined by the CHECK_FREQUENCY) checks if a client has been idle for a specific period.
        If yes, this client should be disconnected by the server.
        """
        while True:
            print 'Checking idle users...'
            for username in self.users:
                user = self.users[username]
                if Authenticator.is_online(user):  # only check the online users
                    last_active = user['last_active']
                    if last_active:
                        idle = (datetime.datetime.now() - last_active).total_seconds()
                        if idle > self.time_out:  # automatically log the user out
                            (ip, port) = Authenticator.get_user_address(user)
                            data_json = {'command': 'LOGOUT', 'from': 'SERVER', 'message': 'You have been disconnected by the server due to being inactive.'}
                            socket_to = Connection.connect(ip, port)
                            Connection.send(socket_to, data_json)
                            socket_to.close()

                            # clear the login information
                            self.logout(username, True)
                            print username + ' has been disconnected.'

            print 'Done checking.'
            time.sleep(self.CHECK_FREQUENCY)

    def authenticate(self, s, from_user, data, addr):
        data_json = Authenticator.authenticate(from_user, data, addr, self.block_time)
        Connection.send(s, data_json)

        status = data_json['command']
        if status == 'OK':
            notification_message = from_user + ' has logged in.'
            self.__notification(from_user, notification_message)

    def broadcast(self, s, from_user, data):
        """
        The message from the client will be sent to all other online clients.
        """
        sender_username = from_user
        message = data['message']

        sender = self.users[sender_username]
        for username in self.users:
            user = self.users[username]
            if Authenticator.is_online(user):
                if username != sender_username:
                    (ip, port) = Authenticator.get_user_address(user)
                    try:
                        socket_to = Connection.connect(ip, port)
                        data_json = {'command': 'MESSAGE', 'from': sender_username, 'message': message}
                        Connection.send(socket_to, data_json)
                        socket_to.close()
                    except:
                        print 'Could not deliver to: ' + ip + ' port: ' + str(port)
            # else:  # store as an offline message
            #     offline_message = {'sender': sender_username, 'message': message}
            #     user['offline_messages'].append(offline_message)

        response = 'You message has been broadcast!'
        data_json = {'command': 'OK', 'message': response}
        Connection.send(s, data_json)

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
        sender_user = self.users[sender_username]
        for username in message_to:
            # print username
            # print username in self.users
            if username in self.users:  # only send message to those valid users
                user = self.users[username]
                if sender_username not in user['black_list']:
                    if Authenticator.is_online(user):
                        if username != sender_username:  # should not self message to yourself
                            (ip, port) = Authenticator.get_user_address(user)
                            try:
                                socket_to = Connection.connect(ip, port)
                                data_json = {'command': 'MESSAGE', 'from': sender_username, 'message': message}
                                Connection.send(socket_to,data_json)
                                socket_to.close()

                                response += 'To ' + username + ': ' + 'You message has been sent!\n'
                            except:
                                print 'Could not deliver to: ' + ip + ' port: ' + str(port)
                                response += 'To ' + username + ': ' + 'You message has failed to be sent!\n'
                        else:
                            response += 'To ' + username + ': ' + 'You cannot send message to yourself.\n'
                    else:  # store as an offline message
                        self.__store_offline_message(user, username, sender_username, message)
                        response += 'To ' + username + ': ' + username + ' is not online. You message has been stored as an offline message.\n'
                else:  # the sender is in the receiver's blacklist so the message cannot be sent
                    response += 'To ' + username + ': Sorry! You are in user ' + username + '\'s blacklist. You message cannot be sent.\n'
            else:
                response += 'To ' + username + ': ' + 'User ' + username + ' is not found.\n'

        Connection.send(s, {'command': status, 'message': response})

    def __store_offline_message(self, user, username, sender_username, message):
        """
        The offline messages will be stored in a text file,
        so that when the server is restarted, these messages will not be lost.
        """
        offline_message = {'sender': sender_username, 'message': message}
        user['offline_messages'].append(offline_message)

        filename = 'offline_message_' + username + '.txt'
        with open(filename, 'a') as myfile:
            json.dump(offline_message, myfile)
            myfile.write('\n')

    def logout(self, username, is_forced=False):
        """
        This method resets some of the user information.
        """
        user = self.users[username]
        # (ip, port) = self.get_user_address(user)
        # command = {'command': 'LOGOUT'}
        # message = {'from': sender_username, 'message': 'You have logged out.'}
        # socket_to = Connection.connect(ip, port)
        # Connection.send(socket_to, command, message)
        # socket_to.close()

        # clear the login information
        user['ip'] = ''
        user['port'] = 0
        if not is_forced:  # if the user is logged out by the server, then the last_active attribute should not be updated.
            user['last_active'] = datetime.datetime.now()
        user['session'] = False
        # user['login_attempts'] = 0

        if not is_forced:
            notification_message = username + ' has logged out.'
            self.__notification(username, notification_message)

    def who(self, s, from_user):
        """
        """
        online_users = []
        sender_username = from_user
        for username in self.users:
            # if username != sender_username:  #UPDATED: should include the querying user
            user = self.users[username]
            if Authenticator.is_online(user):
                online_users.append(username)

        data_json = {'command': 'OK', 'from': sender_username, 'message': online_users}
        Connection.send(s, data_json)

    def last(self, s, from_user, data):
        """
        1. Include those users that are online.
        2. If a user is not online, compare its last_active attribute with the number provided,
           since the last_active attribute is updated after the user logs out.
        """
        users = []
        for username in self.users:
            user = self.users[username]
            if Authenticator.is_online(user):  # if the user is currently online, simply add it to the list
                users.append(username)
            else:  # if the user if offline, compare the number with its last_active attribute
                last_active = user['last_active']
                if last_active is not None:
                    if (datetime.datetime.now() - last_active).total_seconds() <= data['number'] * 60:
                        users.append(username)

        sender_username = from_user
        data_json = {'command': 'OK', 'from': sender_username, 'message': users}
        Connection.send(s, data_json)

    def check(self, s, from_user, data):
        """
        This methods is mainly used for debugging.
        """
        target = data['target']
        sender_username = from_user
        data_json = {}
        if target in self.users:
            user = self.users[target]
            #if Authenticator.is_online(user):  # for better debugging, this line may not be necessary
            data_json = {'command': 'OK', 'from': sender_username, 'message': str(user)}
            #else:
            #    message = {'from': sender_username, 'message': 'User ' + target + ' is not online.'}
        else:
            data_json = {'command': 'OK', 'from': sender_username, 'message': 'User ' + target + ' is not found.'}
        Connection.send(s, data_json)

    def blacklist(self, s, from_user, data):
        """
        This methods is used to add users in the blacklist.
        """
        targets = data['targets']
        message = ''
        sender_user = self.users[from_user]
        for target in targets:
            if target != from_user:  # you cannot blacklist yourself
                if target in self.users:
                    if target not in sender_user['black_list']:
                        sender_user['black_list'].append(target)
                        message += 'User ' + target + ' has been added in your blacklist.\n'
                    else:
                        message += 'User ' + target + ' is already in your blacklist.\n'
                else:
                    message += 'User ' + target + ' is not found.\n'
            else:
                message += 'For user ' + target + ': You cannot blacklist yourself.\n'

        data_json = {'command': 'OK', 'message': message}
        Connection.send(s, data_json)

    def whitelist(self, s, from_user, data):
        """
        This methods is used to remove users from the blacklist.
        """
        targets = data['targets']
        message = ''
        sender_user = self.users[from_user]
        for target in targets:
            if target != from_user:  # you cannot whitelist yourself
                if target in self.users:
                    if target in sender_user['black_list']:
                        sender_user['black_list'].remove(target)
                        message += 'User ' + target + ' has been removed from your blacklist.\n'
                    else:
                        message += 'User ' + target + ' is not in your blacklist.\n'
                else:
                    message += 'User ' + target + ' is not found.\n'
            else:
                message += 'For user ' + target + ': You have no reason to remove yourself from the blacklist :)\n'

        data_json = {'command': 'OK', 'message': message}
        Connection.send(s, data_json)

    def active(self, s, from_user, data):
        """
        This method mainly checks the last_active attribute of a user
        """
        users = []
        for username in self.users:
            user = self.users[username]
            last_active = user['last_active']
            if last_active is not None:
                if (datetime.datetime.now() - last_active).total_seconds() <= data['number'] * 60:
                    users.append(username)

        sender_username = from_user
        data_json = {'command': 'OK', 'from': sender_username, 'message': users}
        Connection.send(s, data_json)

    def __notification(self, from_user, data):
        sender_username = from_user
        for username in self.users:
            user = self.users[username]
            if Authenticator.is_online(user):
                if username != sender_username:  # no need to notify yourself
                    (ip, port) = Authenticator.get_user_address(user)
                    try:
                        socket_to = Connection.connect(ip, port)
                        data_json = {'command': 'NOTIFICATION', 'from': sender_username, 'message': data}
                        Connection.send(socket_to, data_json)
                        socket_to.close()
                    except:
                        print 'Could not deliver to: ' + ip + ' port: ' + str(port)