import sys
import os

from twill import commands

def login_success(login_user, login_pass):
    commands.go('https://campusnet.jacobs-university.de/scripts/mgrqispi.dll?APPNAME=CampusNet&PRGNAME=ACTION&ARGUMENTS=-A9PnS7.Eby4LCWWmmtOcbYKUQ-so-sF48wtHtVNWX9aIeYmoSh5mej--SCbT.jubdlAouHy3dHzwyr-O.ufj3NVAYCNiJr0CFcBNwA3xADclRCTyqC0Oip8drT0F=')
    commands.fv('1', 'usrname', login_user)
    commands.fv('1', 'pass', login_pass)
    commands.submit('3')

    out = sys.stdout
    bin = open(os.devnull, 'w')
    sys.stdout = bin
    login_result = commands.show()
    sys.stdout = out

    return (login_result.find('Wrong username or password') == -1)