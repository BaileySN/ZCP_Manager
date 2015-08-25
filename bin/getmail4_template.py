#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hier kann man das getmail Template anpassen.
# Danach wird dies bei neu einem neue User verwendet.


# noinspection PyPep8Naming,PyClassHasNoInit
class getmail4:
    g_retriever = "[retriever]"
    g_destination = """
[destination]
type = MDA_external
path = /usr/bin/zarafa-dagent
    """
    g_options = """
[options]
verbose = 1
#read_all = true
delete = true
message_log = ~/.getmail/log
    """
    g_filter1 = """
[filter]
type = Filter_external
path = /usr/bin/spamc
arguments = ('-s', '250000' )
    """
