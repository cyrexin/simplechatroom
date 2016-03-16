from Encrypt import *

user_password = {
    'columbia': '116bway',
    'seas': 'winterisover',
    'csee4119': 'lotsofassignments',
    'foobar': 'passpass',
    'windows': 'withglass',
    'google': 'partofalphabet',
    'facebook': 'wastetime',
    'wikipedia': 'donation',
    'network': 'seemsez'
}

f = open('user_pass.txt','w')
for username in user_password:
    print 'username: %s' % username
    print 'password: %s' % user_password[username]
    f.write(username + ' ' + Encrypt.create_signature(user_password[username].strip()) + '\n')
f.close()
