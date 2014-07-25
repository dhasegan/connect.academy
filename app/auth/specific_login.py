import sys
import os

from twill.commands import go, showforms, formclear, fv, submit

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
        go(university["url"])
        fv('1', 'usrname', username)
        fv('1', 'pass', password)
        submit('3')
        login_result = showforms()

        if login_result.find('Wrong username or password') == -1 and login_result.find('Access denied') == -1:
            sys.stdout = out
            university_context = {
                "name": university["name"],
                "domain": university["domain"]
            }
            return university_context

    sys.stdout = out
    return None
