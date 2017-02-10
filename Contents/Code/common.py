#!/usr/bin/env python

"""9anime common code"""

# general constants
TITLE = '9anime'
PREFIX = '/video/' + TITLE
BASE_URL = 'https://{}.to'.format(TITLE)
LIST_VIEW_CLIENTS = ['Android', 'iOS']

####################################################################################################
def ParseVersion(version):
    try:
        return tuple(map(int, (version.split('.'))))
    except:
        return version
