from Connection import *
from Encrypt import *
import datetime
import random


class Authenticator:
    """
    This class is used for the server authentication
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
                'queue': [],
                'ip': '',
                'port': 0,
                'last_seen': None,
                'blocked': [],
                'login_attempts': 0,
                'last_attempt': None,
                'session': False,  # used for checking if the user is online
                'locked': False
            }

        user_pass.close()

    @staticmethod
    def is_online(user):
        """
        """
        # last_seen = user.get('last_seen', None)
        #
        # if last_seen != None:
        #     idle = (datetime.datetime.now() - last_seen).total_seconds()
        #     if idle < TIMEOUT:
        #         return True
        #
        # return False
        return user['session']

    @staticmethod
    def user_address(user):
        """
        """
        if user:
            ip = user.get('ip', None)
            port = user.get('port', None)
            return (ip, port)

        return None

    @staticmethod
    def authenticate(cmd_from, data, addr, block_time):
        """
        """
        username = cmd_from
        password = Encrypt.create_signature(data['password'])
        # print 'username = ' + username
        # print 'password plain: ' + data['password']
        # print 'password = ' + password
        # print self.users[username]

        if username in Authenticator.users:
            user = Authenticator.users[username]
            # print user

            # should reset locking status if the block_time has passed
            if user['last_attempt']:
                since_last = (datetime.datetime.now() - user['last_attempt']).total_seconds()
                if since_last > block_time:
                    if user['locked']:
                        user['locked'] = False

            user['last_attempt'] = datetime.datetime.now()

            if user['login_attempts'] < 2 and not user['locked']:  # the user has 3 chances to input a wrong password
                if user['password'] == password:
                    if Authenticator.is_online(user):  # if the user has been online, disconnect it from other machine.
                        try:
                            (ip, port) = Authenticator.user_address(user)
                            socket_old = Connection.connect(ip, port)
                            command = {'command': 'LOGOUT'}
                            print addr
                            message = username + 'has connected from address: ' + addr[0] + '. You will be disconnected.'
                            Connection.send(socket_old, command, {'message': message})
                            socket_old.close()
                        except:
                            print 'Can not connect to old socket.'

                    user['ip'] = addr[0]
                    user['port'] = random.randint(10000, 50000)  # assign a random port to the client
                    user['last_seen'] = datetime.datetime.now()
                    user['session'] = True
                    command = 'OK'
                    response = {'ip': user['ip'], 'port': user['port'], 'message': 'You have been connected to the chat server!'}
                else:  # wrong password
                    # print 'The input password is not correct.'
                    user['login_attempts'] += 1
                    command = 'WRONG_PASSWORD'
                    response = {'message': 'The input password is not correct.'}
            else:
                command = 'BLOCK'
                response = {'message': 'This account has been locked for ' + str(block_time) + ' seconds due to too many attempts. Please try later.'}
                user['locked'] = True
                user['login_attempts'] = 0

        else:
            print 'User "%s" is not found.' % username
            command = 'USER_NOT_FOUND'
            response = {'message': 'User not found.'}

        command = {'command': command}
        return command, response
