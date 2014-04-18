import sys
import os

from twill import commands

_UNIVERSITY_LOGINS = [
    {
        "name": "Jacobs University Bremen",
        "url": 'https://campusnet.jacobs-university.de/scripts/mgrqispi.dll?APPNAME=CampusNet&PRGNAME=ACTION&ARGUMENTS=-A9PnS7.Eby4LCWWmmtOcbYKUQ-so-sF48wtHtVNWX9aIeYmoSh5mej--SCbT.jubdlAouHy3dHzwyr-O.ufj3NVAYCNiJr0CFcBNwA3xADclRCTyqC0Oip8drT0F=',
        "domain": 'jacobs-university.de'
    }
]


def get_university(username, password):
    # Get rid of ugly console logging
    out = sys.stdout
    bin = open(os.devnull, 'w')
    sys.stdout = bin

    for university in _UNIVERSITY_LOGINS:
        commands.go(university["url"])
        commands.fv('1', 'usrname', username)
        commands.fv('1', 'pass', password)
        commands.submit('3')
        login_result = commands.show()

        if login_result.find('Wrong username or password') == -1:
            sys.stdout = out
            university_context = {
                "name": university["name"],
                "domain": university["domain"]
            }
            return university_context

    sys.stdout = out
    return None
