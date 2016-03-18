from ClientUtils import *
from Utils import *
import os
import sys


class ClientCLI:
    """
    This class is the command line interface for the client.
    """

    def __init__(self, host, port):
        self.client = ClientUtils(host, port)

    def start(self):
        """
        1. Trigger the login command line interface.
        2. If the user has been authorized, then start the client (which will bind a port and listen to the server).
        3. Start the client CLI.
        """

        try:
            self.__login()
            self.client.start()
            self.__interface()
        except KeyboardInterrupt, msg:
            if self.client.authorized:
                self.client.logout()

            print '\nThanks for using the chat room. See you next time!'
            os._exit(0)

    def __login(self):
        """
        This is the CLI for the client to log in.
        """
        while True:
            username = raw_input("Username: ")
            password = raw_input("Password: ")
            if username == '' or password == '':
                print 'Username and password cannot be empty!'
                continue

            if self.client.login(username, password):
                return True

    def __interface(self):
        """
        1. The user can input command here.
        2. This CLI will also display the messages from the server.
        """
        while True:
            encoding = 'utf-8' if sys.stdin.encoding in (None, 'ascii') else sys.stdin.encoding  # This is necessary to support UTF-8 characters.
            line = raw_input('Please enter your command: ').decode(encoding)
            # print('line: ' + line)
            if len(line) == 0:
                continue

            data = line.split(" ", 1)
            command = ''
            parameters = ''
            if len(data) > 0:
                command = data[0]
                if len(data) > 1:
                    parameters = data[1]

            if command == 'broadcast':
                if len(parameters) > 0:
                    message = parameters
                    self.client.broadcast(message)
                else:
                    print 'Wrong parameters. Usage: broadcast <message>'

            elif command == 'send':  # TODO: support utf-8 message
                if len(parameters) > 0:
                    message_to = []
                    message = ''
                    regex_one_user = re.match( r'^([\d\w]+)\s(.+)$', parameters, re.M|re.I)
                    regex_multi_users = re.match( r'^\((.+)\)\s(.+)$', parameters, re.M|re.I)
                    if regex_one_user:  # that there is only one user
                        args = parameters.split(' ', 1)
                        message_to.append(args[0])
                        message = args[1]

                        # message = message.decode('utf-8').encode('utf-8')

                        self.client.send_message(message_to, message)
                    elif regex_multi_users:
                        args = re.match( r'\((.+)\)\s(.+)', parameters, re.M|re.I)
                        # print 'args.group(1): ' + args.group(1)
                        # print 'args.group(2): ' + args.group(2)
                        user_list = args.group(1)
                        message = args.group(2)
                        user_list = user_list.split(' ')
                        for user in user_list:
                            message_to.append(user)

                        # message = message.deconde('utf-8').encode('utf-8')

                        self.client.send_message(message_to, message)
                    else:
                        print 'Wrong parameters. Usage: send <user> <message> or send (<user>...<user>) <message>'

                    # print message_to

                    # self.client.send_message(message_to, message)
                else:
                    print 'Wrong parameters. Usage: send <user> <message> or send (<user>...<user>) <message>'

            elif command == 'logout':
                self.client.logout()
                print 'Thanks for using the chat room. See you next time!'
                # sys.exit(0)
                os._exit(0)

            elif command == 'who':
                self.client.who()

            elif command == 'last':
                # print self.__is_number(parameters)
                if len(parameters) > 0 and Utils.is_number(parameters) and int(parameters) > 0 and int(parameters) <= 60:
                    number = int(parameters)
                    self.client.last(number)
                else:
                    print 'Wrong parameters. Usage: last <number>, where 0 < number <= 60'

            elif command == 'check':  # check user's status. mainly for debugging use
                target = ''
                if len(parameters) > 0:
                    target = parameters
                self.client.check(target)

            else:
                print command + ' - is an invalid command.'
