__version__ = "0.7"


def gpl_header():
    header = """
###########################################################################################
# zcp-manager Copyright (C) 2015  Bailey                                                  #
# This program comes with ABSOLUTELY NO WARRANTY.                                         #
# This is free software, and you are welcome to redistribute it under certain conditions. #
###########################################################################################
        """
    return header


def help_message():
    message = """
###########################################################################################
#                                                                                         #
#                               ZCP Manager v{}                                        #
#-----------------------------------------------------------------------------------------#
#                                                                                         #
# Dieses Tool vereinfacht das Einrichten von Konten mit DB Plugin und getmail.            #
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
        """.format(__version__)
    return message
