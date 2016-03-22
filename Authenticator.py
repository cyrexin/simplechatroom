from Connection import *
from Encrypt import *
import datetime
import random
import json
import os


class Authenticator:
    """
    This class contains methods for the server authentication.
    """
    users = {}

    @staticmethod
    def load_user_password():
        """
        Load the credentials from the file "user_pass.txt".
        """
        user_pass = open("user_pass.txt", "r")
        for line in user_pass:
            split = line.rstrip("\n").split(' ', 2)
            username = split[0]
            password = split[1]
            Authenticator.users[username] = {
                'password': password,
                'offline_messages': [],
                'ip': '',
                'port': 0,
                'last_active': None,
                'login_attempts': {},
                'last_attempt': {},
                'session': False,  # used for checking if the user is online
                'locked': {},
                'black_list': []
            }

            # load offline messages
            try:
                Authenticator.__load_offline_messages(username)
            except:
                print 'Failed to load the offline messages for user ' + username + '.'

        user_pass.close()

    @staticmethod
    def __load_offline_messages(username):
        message_filename = 'offline_message_' + username + '.txt'
        try:
            message_file = open(message_filename, 'r')
            print 'Loading offline messages for user ' + username + '...'
            for line in message_file:
                Authenticator.users[username]['offline_messages'].append(
                    json.loads(line)
                )
            message_file.close()
            print 'Done loading offline messages for user ' + username + '.'

            # os.remove(message_filename)  # delete the file after it is loaded
        except IOError:
            print 'User ' + username + ' does not have offline messages.'
            pass

    @staticmethod
    def is_online(user):
        """
        Check if a user is online based on the session attribute.
        """
        return user['session']

    @staticmethod
    def get_user_address(user):
        """
        Return the IP and port of a client user.
        """
        if user:
            ip = user.get('ip', None)
            port = user.get('port', None)
            return ip, port

        return None

    @staticmethod
    def authenticate(from_user, data, addr, block_time):
        """
        There are some key points in this server-side authentication method:
        1. For a username, each IP has 3 chances to attempt login. After that, this IP will be blocked for this user for a period of BLOCK_TIME.
        2. For a user, if it is logged in from another client, the previous logged-in client will be disconnected.
        """
        username = from_user
        password = Encrypt.create_signature(data['password'])
        # print 'username = ' + username
        # print 'password plain: ' + data['password']
        # print 'password = ' + password
        # print self.users[username]
        user_ip = addr[0]

        if username in Authenticator.users:
            user = Authenticator.users[username]
            # print user

            # should reset locking status for the IP if the block_time has passed
            Authenticator.__reset_locked_status(user_ip, user, block_time)

            if user_ip not in user['locked'] or not user['locked'][user_ip]:
                if user['password'] == password:
                    if Authenticator.is_online(user):  # if the user has been online, disconnect it from other machine.
                        try:
                            (ip, port) = Authenticator.get_user_address(user)
                            socket_online = Connection.connect(ip, port)
                            command = {'command': 'LOGOUT'}
                            print addr
                            message = username + ' has connected from address: ' + addr[0] + '. You will be disconnected.'
                            Connection.send(socket_online, command, {'message': message})
                            socket_online.close()
                        except:
                            print 'Cannot connect to old socket.'

                    user['ip'] = user_ip
                    user['port'] = random.randint(10000, 50000)  # assign a random port to the client TODO:maybe there is a better way
                    user['last_active'] = datetime.datetime.now()
                    user['session'] = True

                    if user_ip in user['login_attempts']:
                        user['login_attempts'][user_ip] = 0

                    offline_messages = []
                    if len(user['offline_messages']) > 0:  # should send these messages to the user and reset the offline_messages field
                        offline_messages = user['offline_messages']
                        user['offline_messages'] = []
                        message_filename = 'offline_message_' + username + '.txt'
                        os.remove(message_filename)  # delete the file after it is loaded

                    command = 'OK'
                    response = {'ip': user['ip'], 'port': user['port'], 'message': 'You have been connected to the chat server!', 'offline_messages': offline_messages}
                else:  # wrong password
                    # print 'The input password is not correct.'
                    if user_ip not in user['login_attempts']:
                        user['login_attempts'][user_ip] = 1
                    else:
                        user['login_attempts'][user_ip] += 1
                    command = 'WRONG_PASSWORD'
                    message = 'The input password is not correct.'
                    # response = {'message': 'The input password is not correct.'}

                    if user['login_attempts'][user_ip] == 3:  # the user has 3 chances to input a wrong password
                        message += '\nThis account has been locked for ' + str(block_time) + ' seconds due to too many attempts. Please try later.'
                        user['locked'][user_ip] = True  # set the account as locked for the attempted IP
                        user['login_attempts'][user_ip] = 0  # reset the number of login attempt for the IP

                    response = {'message': message}
            else:
                command = 'BLOCK'
                response = {'message': 'This account has been locked for ' + str(block_time) + ' seconds due to too many attempts. Please try later.'}

        else:
            message = 'User "%s" is not found.' % username
            command = 'USER_NOT_FOUND'
            response = {'message': message}

        command = {'command': command}
        return command, response

    @staticmethod
    def __reset_locked_status(user_ip, user, block_time):
        if user_ip in user['last_attempt']:
            since_last = (datetime.datetime.now() - user['last_attempt'][user_ip]).total_seconds()
            if since_last > block_time:
                if user_ip in user['locked']:
                    user['locked'][user_ip] = False

        user['last_attempt'][user_ip] = datetime.datetime.now()