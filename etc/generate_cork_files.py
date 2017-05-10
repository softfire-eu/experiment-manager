#!/usr/bin/env python
#
#
# Regenerate files in example_conf
import argparse
import getpass
from datetime import datetime

from cork import Cork


def get_username_and_password():
    user = input("Username [%s]: " % getpass.getuser())
    if not user:
        user = getpass.getuser()

    pprompt = lambda: (getpass.getpass(), getpass.getpass('Retype password: '))

    p1, p2 = pprompt()
    while p1 != p2:
        print('Passwords do not match. Try again')
        p1, p2 = pprompt()

    get_role = lambda: input("chose the role between admin or experimenter [a/e]")
    role = get_role()
    while not role or (role != 'a' and role != 'e'):
        role = get_role()

    if role == 'a':
        role = 'admin'
    else:
        role = 'experimenter'
    return user, p1, role


def populate_conf_directory(out_dir):
    cork = Cork(out_dir, initialize=True)

    cork._store.roles['admin'] = 100
    cork._store.roles['experimenter'] = 60
    cork._store.save_roles()

    tstamp = str(datetime.utcnow())
    stop = False
    while not stop:
        choice = input('do you want to add one user? [Y/n]')
        if choice.lower() == 'y' or choice.lower() == 'yes' or not choice:

            username, password, role = get_username_and_password()
            user_cork = {
                'role': role,
                'hash': cork._hash(username, password),
                'email_addr': username + '@localhost.local',
                'desc': username + ' test user',
                'creation_date': tstamp
            }
            cork._store.users[username] = user_cork
            print("Cork user is: %s, password is %s" % (username,password))
        else:
            stop = True

    cork._store.save_users()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create username and password for experimenter manager.')
    parser.add_argument('outdir', help='output dir of the cork files')

    args = parser.parse_args()
    populate_conf_directory(args.outdir)
