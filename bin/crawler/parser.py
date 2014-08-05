
import urllib
import re
import sys
import os
import lxml.html
from collections import deque
from htmlentitydefs import name2codepoint
from HTMLParser import HTMLParser

# create a subclass and override the handler methods
class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.insideForm = 0
        self.insideTable = 0
        self.insideCaption = 0
        self.caption = ""
        self.tableData = ""
        self.gotName = 0
        self.courseInfo = {}
    def handle_starttag(self, tag, attrs):
        if tag == "form":
            m = dict(attrs)
            if m['name'] == 'courseform' or self.insideForm > 0:
                self.insideForm += 1
        if self.insideForm and self.gotName == 0 and tag == "h1":
            self.gotName = 1
        if self.insideForm and tag == 'table':
            self.insideTable = 1
        if self.insideTable and tag == 'caption':
            self.insideCaption = 1
        if self.insideTable and tag == 'br':
            self.tableData += '<br>'
        # if self.insideTable:
        #     self.tableData += "{ "
    def handle_endtag(self, tag):
        # if self.insideTable:
        #     self.tableData += "} "
        if tag == "form" and self.insideForm > 0:
            self.insideForm -= 1
        if tag == 'table' and self.insideTable:
            self.insideTable = 0
            if self.caption != "" and self.tableData != "":
                self.courseInfo[self.caption] = self.tableData
                self.caption = ""
                self.tableData = ""
            else:
                print "Error: No caption or table contents!", self.caption
        if tag == 'caption' and self.insideCaption:
            self.insideCaption = 0
    def handle_data(self, data):
        if self.gotName == 1:
            self.courseInfo['Name'] = data
            self.gotName = 2
        if self.insideCaption:
            self.caption = data
        if self.insideTable:
            self.tableData += data
    def handle_charref(self, name):
        if name.startswith('x'):
            c = chr(int(name[1:], 16))
        else:
            c = chr(int(name))
        if self.insideTable:
            self.tableData += c
    def handle_entityref(self, name):
        if self.insideTable:
            if name in name2codepoint:
                self.tableData += chr(name2codepoint[name])
            else:
                self.tableData += "&" + name
    def getCourseInfo(self):
        return self.courseInfo

# Clean the extra things
def cleanuper(content):
    no_newlines = content.replace("\n", " ")
    no_unix_newlines = no_newlines.replace("\r", " ")
    no_tabs = no_unix_newlines.replace("\t", " ")
    no_extra_spaces = re.sub(r'  +', ' ', no_tabs)
    formatted = no_extra_spaces.replace('<br>', '\n')
    return formatted

importantFields = [ 'Instructors', 'Type', 'Org-unit', 'Course Name Abbreviation', 'Hours per week',
                    'Credits', 'Min. | Max. participants', 'Partial Grades', 'Official Course Description',
                    'Additional Information', 'This course is divided into the following sections',
                    'Further Grading Information']
linksFile = open('crawler/courses', 'r')
namesFile = open('crawler/courseNames', 'r')

coursesList = []

# Parse the Links
for link in linksFile:
    # Get link and print progress
    courseName = namesFile.readline()
    print courseName[:-1]
    # Download the page
    page = urllib.urlopen(link)
    page = page.read()
    # Parse the page
    parser = MyHTMLParser()
    parser.feed(page)
    uglyCourseInfo = parser.getCourseInfo()
    # Delete the extra stuff and make it a dictionary
    courseInfo = dict(map(lambda x: (cleanuper(x[0]),cleanuper(x[1])), uglyCourseInfo.iteritems() ))
    if not 'Course offering details' in courseInfo:
        print "Error: No label 'Course offering details' abort scanning page"
    if not 'Name' in courseInfo:
        print "Error: No label 'Name' abort scanning page"
    # Get main details about the course
    details = courseInfo['Course offering details']
    detailsMap = {}
    # For each field found put it in the map
    for field in importantFields:
        length = len(details)
        if (field+':') in details:
            startIdx = details.find(field + ":") + len(field) + 2
            stopIdx = min( [ (details.find(f+":") if details.find(f+":") >= startIdx else length) for f in importantFields] )
            if startIdx <= stopIdx:
                if startIdx < stopIdx:
                    detailsMap[field] = unicode(details[startIdx:stopIdx], errors='ignore').strip()
            else:
                print "Error: Start after stop"
    # Parse the Catalogue information
    if 'Contained in course catalogues' in courseInfo:
        catalogue = courseInfo['Contained in course catalogues']
        startIdx = catalogue.find('> ')
        detailsMap['Catalogue'] = catalogue[startIdx+2:].strip()
    else:
        print "Error: No label 'Contained in course catalogues'"
    detailsMap['Name'] = courseName.strip()
    # Parse for the ID and just course name
    courseID = detailsMap['Name'][0:6]
    courseNameOnly = detailsMap['Name'][7:]
    detailsMap['CourseID'] = courseID
    detailsMap['CourseName'] = courseNameOnly
    # Add to our list
    coursesList.append(detailsMap)

linksFile.close()
namesFile.close()

import json
outputFile = open('crawler/courseDetails', 'w')
outputFile.write( json.dumps(coursesList) )
outputFile.close()
