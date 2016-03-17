from ClientUtils import *
from Utils import *
import os


class ClientCLI:
    """
    This class is the command line interface for the client.
    """

    def __init__(self, host, port):
        self.client = ClientUtils(host, port)

    def start(self):
        """
        """

        # try:
        self.authenticate()
        self.client.start()
        self.cli()
        # except (KeyboardInterrupt, SystemExit):
        #     if self.client.started:
        #         self.client.logout()
        #
        #     print 'Goodbye!'
        #     exit(0)

    def authenticate(self):
        """
        """
        while True:
            username = raw_input("username: ")
            password = raw_input("Password: ")
            if username == '' or password == '':
                continue

            if self.client.authenticate(username, password):
                return True

    def cli(self):
        """
        """
        while True:
            line = raw_input('Please enter your command: ')
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
                    if '(' not in parameters:  # that there is only one user
                        args = parameters.split(' ', 1)
                        message_to.append(args[0])
                        message = args[1]
                    else:
                        args = re.match( r'\((.+)\)\s(.+)', parameters, re.M|re.I)
                        # print 'args.group(1): ' + args.group(1)
                        # print 'args.group(2): ' + args.group(2)
                        user_list = args.group(1)
                        message = args.group(2)
                        user_list = user_list.split(' ')
                        for user in user_list:
                            message_to.append(user)

                    # print message_to

                    self.client.send_message(message_to, message)
                else:
                    print 'Wrong parameters. Usage: send <user> <message> or send (<user>...<user>) <message>'

            elif command == 'logout':
                self.client.logout()
                print 'Goodbye!'  #TODO: better message
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
