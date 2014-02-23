#!/usr/bin/env python

import urllib
import re
import sys
import os
import lxml.html
from collections import deque
import HTMLParser
_htmlparser = HTMLParser.HTMLParser()
unescape = _htmlparser.unescape

BASE_URL = "https://campusnet.jacobs-university.de"
START_URL = "https://campusnet.jacobs-university.de/scripts/mgrqispi.dll?APPNAME=CampusNet&PRGNAME=ACTION&ARGUMENTS=-A9PnS7.Eby4LCWWmmtOcbYKUQ-so-sF48wtHtVNWX9aIeYmoSh5mej--SCbT.jubdlAouHy3dHzwyr-O.ufj3NVAYCNiJr0CFcBNwA3xADclRCTyqC0Oip8drT0F="

def cleanLink(link):
    return unescape(link)

def getLinks(input_string):
    links = re.findall(r"<a.*?\s*href=\"(.*?)\".*?>(.*?)</a>", input_string)
    return [cleanLink(BASE_URL+link[0]) for link in links]

def getCourseNames(input_string):
    links = re.findall(r"<a.*?\s*href=\"(.*?)\".*?>(.*?)</a>", input_string)
    return [link[1] for link in links]

courses = []
courseNames = []
queue = deque([START_URL])

while queue:
    link = queue.popleft()
    print link

    page = urllib.urlopen(link)
    page = page.read()

    indexStart = page.find('class="auditRegistrationList"')
    indexStop = page.find('</ul>', indexStart)

    if indexStart < 0:
        indexStart = page.find('class="nb eventTable"')
        indexStop = page.find('</table>', indexStart)
        table = page[indexStart:indexStop]
        newLinks = getLinks(table)
        newCourseNames = getCourseNames(table)

        courses.extend(newLinks)
        courseNames.extend(newCourseNames)
        continue
    ulList = page[indexStart:indexStop]
    newLinks = getLinks(ulList)
    queue.extend(newLinks)


fileHandle = open('crawler/courses', 'w')
for course in courses:
    sys.stdout = fileHandle
    print ('%s' % (course))
sys.stdout = sys.__stdout__
fileHandle.close()

fileHandle = open('crawler/courseNames', 'w')
for course in courseNames:
    sys.stdout = fileHandle
    # Hacked way to avoid some bad characters
    course = course.replace('\xe9', 'e').replace('\xa0', ' ').strip()

    print ('%s' % (course))
sys.stdout = sys.__stdout__
fileHandle.close()