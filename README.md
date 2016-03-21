# Simple Chatroom

### Brief description
This simple chatroom is developed by Python 2.7 mainly using the socket module. It adopts the server-client structure, where clients can send messages to each other via the server. Some elementary security features are also included in this system. The Github space for this project is: https://github.com/cyrexin/simplechatroom

### Details on development environment
This program is written and complied by Python 2.7.3. The text file user_pass.txt contains all the usernames and encrypted passwords. This file is included in the folder. If it is missing by accident, or you cannot log in, simply run the following command and the text file will be created/updated:
```
$ python PopulateCredential.py
```

### How to run the code
- To run the server, type the following command, where 4119 is the port and it could be any number:
```
$ python Server.py 4119
```
- To run the client, type the following command, where <server_IP_address> can be found on the server side:
```
$ python Client.py <server_IP_address> <server_port_no>
```

### Sample commands
#### who
```
// Display all the online users.
who
```

#### last
The format for this command should be:
```
last <number>
```
Where number is in unit minute and it should be greater than 0 and less or equal 60.
Example:
```
// Display the connected users within the last 15 minutes.
last 15
```

#### broadcast
The format of this command should be:
```
broadcast <message>
```
Example:
```
// Send the message "Hello world!" to all the online users.
broadcast Hello world!
```

#### send
The format of this command should be:
```
// Send a message to a single user.
send <user> <message>

// Send a message to a list of users.
send (<user> <user> ... <user>) <message>
```
Example:
```
// Send a private message "How are you?" to the user "facebook".
send facebook How are you?

// Send a private message "How are you guys?" to the users "facebook", "windows" and "google".
send (facebook windows google) How are you guys?
```
After the user type this command, a feedback for the message status to each user will be displayed (e.g. To facebook: You message has been sent! To google: google is not online. You message has been stored as an offline message.). If the receiving user is not online, the message will be saved as an offline message. When this user comes back online again, the offline messages will be displayed.

#### logout
```
// The current user will be logged out after typing this command.
logout
```

### Additional functionalities
#### Offline messages
As mentioned above, when a user sends a private message to another, if the receiving user is not online, the message will be stored as an offline message. When this user comes back online again, the offline messages will be displayed. These offline messages will be stored in a text file named "offline_message_<username>.txt" where <username> is the username of the receiving user. This text file can ensure that even if the server is restarted, these offline messages will NOT be lost. After the offline messages have been displayed, this text file will be removed from the disk.

To test this functionality is simple. The following is a sample procedure:
- Log out all the users.
- Log in as facebook.
- Use this command to send a message to the user "google":
```
send google Hello Google!
```
- Now a text file "offline_message_google.txt" should be created. Use another client window to log in as google.
- The user google should see the offline message from facebook.

#### Blacklist
A user X can blacklist other users, for example Y and Z, so that Y and Z cannot send messages to X. Of course, user X can remove Y and Z from the black list so that they can send messages to X again. This black list only applies for private messages, but NOT broadcast messages.

The format of the command is very similar to that of "send":
```
// Blacklist a single user.
blacklist <user>
// Remove a single user from the blacklist
whitelist <user>

// Blacklist a list of users.
blacklist (<user> <user> ... <user>)
// Remove a list of users from the blacklist
whitelist (<user> <user> ... <user>)
```

A sample flow to test this is as follows:
- Use a client window to log in as facebook.
- Use a client window to log in as google. Send a message to facebook. The message should be successfully sent.
- Back to the facebook window. Type the following command:
```
blacklist google
```
- Back to the google window and send a message to facebook. Now it should be prompted that the message cannot be sent because the user has been added in the blacklist of facebook.
- Back to the facebook window. Type the following command:
```
whitelist google
```
- Back to the google window and send a message to facebook. Now the message should be sent successfully again.

#### Command "active"
Every time a user types a command, its "last_active" attribute will be updated. With the "active" command, a user can check which users are active within the last specific minutes. The format of this command is very similar to "last":
```
active <number>
```

The test case should be similar to the command "last".

#### Command "check"
This command is mainly used for debugging. It can check all the attributes of an online user, including the querying user. The format is as follows:
```
// Check the information of yourself.
check

// Check the information of others.
check <user>
```

### Some notes:
- If a client is idle for a specific period, it will be logged out by the server automatically. This period is defined by the environment variable TIME_OUT, with the default value as 30*60 seconds.
- If a user attempts to log in with an incorrect password for 3 consecutive times, this IP will be blocked for a certain period for this username. The period is defined by the environment variable BLOCK_TIME, with the default value as 60 seconds.
- You can use "Ctrl+C" to terminate a client or the server. When the client is terminated, it will be properly logged out. When the server is terminated, all the connected clients will be properly logged out.
