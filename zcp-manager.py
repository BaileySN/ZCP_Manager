#!/usr/bin/python3
# -*- coding: utf-8 -*-
###########################################################################################################
# kopano-manager - Kopano Manager                                                                         #
# Copyright (C) [2015]  [Bailey]                                                                          #
#                                                                                                         #
# This program is free software;                                                                          #
# you can redistribute it and/or modify it under the terms of the GNU General Public License              #
# as published by the Free Software Foundation;                                                           #
# either version 3 of the License, or (at your option) any later version.                                 #
#                                                                                                         #
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;               #
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.               #
# See the GNU General Public License for more details.                                                    #
#                                                                                                         #
# You should have received a copy of the GNU General Public License along with this program;              #
# if not, see <http://www.gnu.org/licenses/>.                                                             #
###########################################################################################################
import os
import sys
import time
from os import sep, curdir
from argparse import ArgumentParser
from bin import __version__, gpl_header
from subprocess import Popen, PIPE


def createconf():
    if not os.path.isfile(curdir + sep + "bin" + sep + "config.py"):
        os.system(
            "cp " + curdir + sep + "bin" + sep + "config.py.orig" + " " + curdir + sep + "bin" + sep + "config.py")
        time.sleep(0.5)
        os.system("editor " + curdir + sep + "bin" + sep + "config.py")
        print("config.py erstellt")


class KopanoBase(object):
    def __init__(self):
        from bin import config as conf
        self.conf = conf
        self.external_provider = conf.EXTERNAL_PROVIDER
        self.kpadmin = conf.KOPANO_ADMIN_PATH
        self.sleep = time.sleep
        self.getmail_dir = conf.GETMAIL_PATH

    def recreate_userstore(self, username, lang='de_DE.UTF-8'):
        try:
            print("recreate store for {}".format(username))
            oscmd = [self.kpadmin, "--unhook-store", username]
            oscmd2 = [self.kpadmin, "--create-store", username, "--lang", lang]
            p = Popen(oscmd, stdout=PIPE)
            result, error = p.communicate()
            if error:
                print(error)
                exit(1)
            self.sleep(1.0)
            p = Popen(oscmd2, stdout=PIPE, stderr=PIPE)
            result, error = p.communicate()
            if error:
                print(error)
                exit(2)
            return True
        except ValueError:
            pass
        return False

    def kopano_create_user(self, login, password, fullname, email, active):
        print("create User in Kopano")
        try:
            oscmd = [self.kpadmin, "-c", login, "-p", password, "-f", fullname, "-e", email, "-n", active]
            p1 = Popen(oscmd, stdout=PIPE)
            result, error = p1.communicate()
            if error:
                print(error)
                raise ValueError()
            self.recreate_userstore(username=login)
            return result.decode()
        except ValueError:
            return None

    def create_file(self, path_filename, content='', user='vmail', group='vmail', rights='0660'):
        with open(path_filename, 'w') as f:
            f.write(content)
        self.sleep(1.0)
        chright = '{}:{}'.format(user, group)
        cmd = ["chown", chright, path_filename]
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        result, error = p.communicate()
        cmd = ["chmod", rights, path_filename]
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        result, error = p.communicate()
        self.sleep(1.0)
        return True

    def list_user(self):
        try:
            oscmd = [self.kpadmin, "-l"]
            p = Popen(oscmd, stdout=PIPE, stderr=PIPE)
            result, error = p.communicate()
            if error:
                print(error.decode())
                exit(11)
            print(result.decode())
        except ValueError:
            exit(12)


class GetmailTask(KopanoBase):
    def write_cronjob(self, path_filename):
        cnf = self.conf
        fname = path_filename.split(sep)[-1]
        content = '{m} {h} * * * {user} /usr/bin/getmail --rcfile ~/.getmail/{script} &> /dev/null \n'\
            .format(m=cnf.TIME_MINUTES, h=cnf.TIME_HOURS, user=cnf.MAILUSER, script=fname)

        with open(sep+'etc'+sep+'crontab', 'a') as cron:
            cron.write(content)
        return True

    def getmail_rc_file(self, login, password, email, kopano_user):
        try:
            print("Create getmail script for {}".format(login))
            fname = email.replace('@', '.')
            content = """
[retriever]
type = {type}
server = {server}
username = {login}
password = {password}

[destination]
type = MDA_external
path = /usr/sbin/kopano-dagent
arguments = ('-s', '{kopano_user}')

[options]
verbose = 1
#read_all = true
delete = true
message_log = ~/.getmail/log

[filter]
type = Filter_external
path = /usr/bin/spamc
arguments = ('-s', '250000' )

        """.format(type=self.conf.RETRIEVER_TYPE, server=self.conf.RETRIEVER_SERVER, login=login, password=password,
                   kopano_user=kopano_user)

            absolute_fpath = self.conf.GETMAIL_PATH+sep+fname
            self.create_file(path_filename=absolute_fpath, content=content, user=self.conf.MAILUSER,
                             group=self.conf.MAILGROUP)
            print("getmail {} created".format(fname))
            self.write_cronjob(path_filename=absolute_fpath)
            print("reload cron service")
            p = Popen(self.conf.CRON_RELOAD, stdout=PIPE)
            result = p.communicate()[0]
            return True
        except ValueError:
            return False


class CreateMailUser(GetmailTask):
    def interactive(self):
        userlogin = input("Kopano Benutzernamen : ")
        userpasswd = input("Kopano Benutzer Passwort : ")
        fullname = input("Benutzer Vor- und Nachname : ")
        usermail = input("E-Mail : ")
        active = input("Benutzer Active yes=0 no=1, default=0 : ")
        if not active:
            active = '0'
        else:
            active = str(active)

        if self.external_provider:
            print("Angaben Mailabholung")
            provider_login = input("Provier Login : ")
            provider_passwd = input("Provider Passwort : ")
        else:
            provider_login = None
            provider_passwd = None

        kp_result = self.kopano_create_user(login=userlogin, password=userpasswd, fullname=fullname, email=usermail,
                                            active=active)
        if not kp_result:
            print("error create kopano user")
            exit(1)
        if self.external_provider:
            self.getmail_rc_file(login=provider_login, password=provider_passwd, email=usermail, kopano_user=userlogin)
        return True

    def non_interactive(self, login, password, fullname, email, provider_login=None, provider_password=None,
                        active='0'):
        kp_result = self.kopano_create_user(login=login, password=password, fullname=fullname, email=email,
                                            active=active)
        if not kp_result:
            print("error create kopano user")
            exit(1)

        if self.external_provider:
            if provider_login and provider_password:
                self.getmail_rc_file(login=provider_login, password=provider_password, email=email, kopano_user=login)
            else:
                print("External Provider Login or Password is empty")
                exit(3)
        return True


class App():
    def __init__(self):
        from bin import config as conf
        usage = "usage: Kopano Manager v{} options".format(__version__)
        parser = ArgumentParser(usage=usage)
        parser.add_argument("--config", action="store_true", help="open editor and edit Configuration")
        parser.add_argument("--create", action="store_true", dest="createmailuser",
                            help="create E-Mail User and getmail config")
        parser.add_argument("--interactive", action="store_true", dest="interactive", help="Interactive Mode")
        parser.add_argument("--login", action="store", dest="kopano_user", help="Kopano Username")
        parser.add_argument("--password", action="store", dest="kopano_password", help="Kopano Password")
        parser.add_argument("--fullname", action="store", dest="kopano_fname", help="Account Fullname")
        parser.add_argument("--email", action="store", dest="kopano_email", help="E-Mail Adress")
        parser.add_argument("--active", action="store_true", default=False, dest="kopano_activeuser",
                            help="User login disabled")
        parser.add_argument("--provider-login", action="store", dest="provider_login", help="Getmail Provider Login")
        parser.add_argument("--provider-password", action="store", dest="provider_password",
                            help="Getmail Provider Password")
        parser.add_argument("--listuser", action="store_true", dest="kopano_list", help="List Kopano Users")
        parser.add_argument("--kopano-create-user", action="store_true", default=False, dest="kp_create_user",
                            help="create only kopano user")
        parser.add_argument("--create-getmail", action="store_true", default=False, dest="create_getmail",
                            help="create getmail script and cronjob")
        options = parser.parse_args()

        try:
            options_list = [(options.kopano_user, 'Kopano Username'), (options.kopano_password, 'Kopano User Password'),
                            (options.kopano_fname, 'User Fullname'), (options.kopano_email, 'E-Mail Adress')]

            if conf.EXTERNAL_PROVIDER:
                options_list += [(options.provider_login, 'External Provider Login'),
                                 (options.provider_password, 'External Provider Password')]

            if options.createmailuser and options.interactive:
                CreateMailUser().interactive()
            elif not options.interactive and options.createmailuser:
                # detect empty data
                for opt in options_list:
                    if not opt[0]:
                        raise ValueError('No {}'.format(opt[1]))

                if options.kopano_activeuser:
                    active = '1'
                else:
                    active = '0'

                CreateMailUser().non_interactive(login=options.kopano_user, password=options.kopano_password,
                                                 fullname=options.kopano_fname, email=options.kopano_email,
                                                 provider_login=options.provider_login,
                                                 provider_password=options.provider_password, active=active)
                print("user {} created".format(options.kopano_user))
            elif options.kp_create_user:
                # detect empty data
                for opt in options_list:
                    if not opt[0]:
                        raise ValueError('No {}'.format(opt[1]))

                if options.kopano_activeuser:
                    active = '1'
                else:
                    active = '0'

                result = KopanoBase().kopano_create_user(login=options.kopano_user, password=options.kopano_password,
                                                         fullname=options.kopano_fname, email=options.kopano_email,
                                                         active=active)
                print(result)
                exit(0)
            elif options.create_getmail:
                # detect empty data
                for opt in [(options.kopano_user, 'Kopano Username'), (options.kopano_email, 'E-Mail Adress'),
                            (options.provider_login, 'External Provider Login'),
                            (options.provider_password, 'External Provider Password')]:
                    if not opt[0]:
                        raise ValueError('No {}'.format(opt[1]))

                result = GetmailTask().getmail_rc_file(login=options.provider_login, password=options.provider_password,
                                                       email=options.kopano_email, kopano_user=options.kopano_user)
                print("getmail create success {}".format(result))
            elif options.kopano_list:
                KopanoBase().list_user()
            elif options.config:
                os.system("nano "+curdir+sep+"bin"+sep+"config.py")
            else:
                raise IndexError()
        except IndexError:
            parser.print_help()
            exit(0)
        except ValueError as exp:
            print(exp)
            exit(10)


if __name__ == "__main__":
    gpl_header()
    createconf()
    app = App()
