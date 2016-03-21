# Simple Chatroom

### Brief description
This simple chatroom is developed by Python 2.7 mainly using the socket module. It adpots the server-client structure, where clients can send messages to each other via the server. Some elementary security features are also included in this system. The github space for this project is: https://github.com/cyrexin/simplechatroom

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
```
// Display the connected users within the last 15 minutes.
last 15
```

#### broadcast
```
// Send the message "Hello world!" to all the online users.
broadcast Hello world!
```

#### send
```
// Send a private messaeg "How are you?" to the user "facebook".
send facebook How are you?

// Send a private message "How are you guys?" to the users "facebook", "windows" and "google".
send (facebook windows google) How are you guys?
```

#### logout
```
// The current user will be logged out after typing this command.
logout
```
