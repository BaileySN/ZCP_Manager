#!/usr/bin/python
# -*- coding: utf-8 -*-
###########################################################################################################
# zcp-manager - Zarafa Manager                                                                            #
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

from bin import getmail4_template

gt = getmail4_template.getmail4

vernum = "0.4 "
command = sys.argv[1]
zcpadmin = "zarafa-admin"
getmail_script_path = (sep + "home" + sep + "vmail" + sep + ".getmail" + sep)


def createconf():
    if not os.path.isfile(curdir + sep + "bin" + sep + "config.py"):
        os.system(
            "cp " + curdir + sep + "bin" + sep + "config.py.orig" + " " + curdir + sep + "bin" + sep + "config.py")
        time.sleep(0.5)
        os.system("editor " + curdir + sep + "bin" + sep + "config.py")
        print("config.py erstellt")


def gpl_txt():
    print("""
###########################################################################################
# zcp-manager Copyright (C) 2015  Bailey                                                  #
# This program comes with ABSOLUTELY NO WARRANTY.                                         #
# This is free software, and you are welcome to redistribute it under certain conditions. #
###########################################################################################
        """)


def printhelp():
    helptxt = """
###########################################################################################
#                                                                                         #
#                               ZCP Manager v%s                                         #
#-----------------------------------------------------------------------------------------#
#                                                                                         #
# Dieses Tool vereinfacht das Einrichten von Konten mit DB Plugin und getmail4.           #
#                                                                                         #
#-----------------------------------------------------------------------------------------#
#                                                                                         #
# config            -> Oeffnet mit dem Standart Editor die configurationsdatei            #
# createmailuser    -> Erstellt Benutzer im Zarafa und richtet die Mailabholung mit       #
#                      den jeweiligen angegeben Daten ein.                                #
# list              -> Zeigt die Zarafa Benutzerliste an gleich wie zarafa-admin -l       #
# help              -> Zeigt diese Hilfe an                                               #
#                                                                                         #
#-----------------------------------------------------------------------------------------#
#                                                                                         #
# Falls man als Benutzer Root arbeitet, braucht man sudo nicht angeben                    #
#                                                                                         #
# python python zcp-manager.py config                                                     #
# sudo python zcp-manager.py createmailuser (die Daten werden Interaktiv abgefragt)       #
# sudo python zcp-manager.py list                                                         #
# python zcp-manager.py help                                                              #
#                                                                                         #
###########################################################################################
        """ % vernum
    print(helptxt)


def createmailuser(username, userpassword, fname, email, providerlogin, providerpassword, activeuser="1"):
    from bin import config as conf
    ts = time.sleep
    try:
        print("Benutzer im ZCP System anlegen")
        os.system(
            zcpadmin + " " + "-c " + username + " -p " + userpassword + " -f " + '"' + fname + '"' + " -e " + email + " -n " + activeuser)
        ts(0.5)
        os.system(zcpadmin + " --create-store " + username)
        ts(0.5)
        print("Erstelle Getmail4 script")
        fname = email.replace('@', '.')
        f = open(getmail_script_path + fname, 'w')
        f.write(gt.g_retriever + "\n" +
                "type = " + conf.RETRIEVER_TYPE + "\n" +
                "server = " + conf.RETRIEVER_SERVER + "\n" +
                "username = " + providerlogin + "\n" +
                "password = " + providerpassword + "\n" +
                "\n" +
                gt.g_destination + "\n" +
                "arguments = ('-s', '" + username + "')" + "\n" +
                "\n" +
                gt.g_options + "\n" +
                "\n" +
                gt.g_filter1 + "\n")
        f.close()
        os.system(
            "chmod 660 " + getmail_script_path + fname + " &&chown " + conf.MAILUSER + ":" + conf.MAILGROUP + " " + getmail_script_path + fname)
        ts(0.5)
        print("getmail4 script erstellt")
        print("Automatische Abholung anlegen")
        cronjob = open(sep + "etc" + sep + "crontab", "a")
        cronjob.write(
            conf.TIME_MINUTES + " " + conf.TIME_HOURS + " * * *" + "\t" + " vmail" + "\t" + " /usr/bin/getmail --rcfile ~/.getmail/" + fname + " &>/dev/null")
        ts(0.5)
        os.system("service cron reload")
        print("Cronjob angelegt und neu geladen")
        print("Benutzer angelegt und Automatische Abholung erstellt")
        ts(0.5)
    except IOError:
        print("Fehler bei der Benutzer Erstellung!")

gpl_txt()
createconf()

if command == "createmailuser":
    print("ZCP Einstellungen ")
    userlogin = raw_input("Benutzernamen Angeben : ")
    userpasswd = raw_input("Benutzer Passwort fuer Login : ")
    fullname = raw_input("Vor- und Nachname : ")
    usermail = raw_input("E-Mail Adresse : ")
    active = raw_input("Benutzer Active yes=1 no=0, default=1 : ")
    if int(active) != int("0"):
        active = "1"
    print("Mailabholung")
    provider_login = raw_input("Provier Login : ")
    provider_passwd = raw_input("Provider Passwort : ")
    createmailuser(userlogin, userpasswd, fullname, usermail, provider_login, provider_passwd, active)
elif command == "list":
    os.system(zcpadmin + " -l")
elif command == "config":
    os.system("nano " + curdir + sep + "bin" + sep + "config.py")
else:
    printhelp()
