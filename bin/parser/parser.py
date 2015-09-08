
import re
import sys
import os
import lxml.html
import json
import chardet
from collections import deque
from htmlentitydefs import name2codepoint
from HTMLParser import HTMLParser
from common.urllib import urlopen_with_retry

# helper for appointments parser
def get_match_indeces(pattern, string):
    return [(m.start(0), m.end(0)) for m in re.finditer(pattern, string)]

# Appointments Parser
def parse_appointments(course_dict):
    appointments = []
    if "Appointments" in course_dict:
        profs = json.load( open('../professors/professors_details.json'))
        raw_appointments = course_dict["Appointments"].replace("Appointments Date From To Room Instructors", "")
        date_pattern = "(Mon|Tue|Wed|Th|Fri|Sat|Sun), \d(\d)?\. (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(\.)? \d\d\d\d \d\d:\d\d \d\d:\d\d"
        matches = get_match_indeces(date_pattern, raw_appointments)
        for i in range(len(matches)):
            current_appointment = ""
            if i + 1 < len(matches):
                # from the start of this match to the start of the next match
                current_appointment = raw_appointments[matches[i][0]:matches[i+1][0]-3] #-3 to skip the number before the appointment date
            else:
                # from the start of this match to the end of the string
                current_appointment = raw_appointments[matches[i][0]:]
            match = get_match_indeces(date_pattern, current_appointment)[0]
            
            dates_string = current_appointment[match[0]:match[1]]
            start_time = dates_string[-11:-6]
            end_time = dates_string[-5:]
            
            date_info = dates_string[:-11]
            _, date = date_info.split(", ")
            
            # Start and end times
            start_datetime = date + start_time
            end_datetime = date + end_time

        

            location = current_appointment[match[1]+1:]
            #location = location.decode("utf-8") 
            # clean prof names from location
            if "Instructors" in course_dict:      
                for prof in course_dict['Instructors'].split("; "):
                    #prof = prof.decode("utf-8")
                    location = location.replace(prof,"")
                    location = location.replace(";", "")
                
            for prof in profs:
                name =  profs[prof]["fname"]+ " " + profs[prof]["lname"]
                location = location.replace(name, u"")
            
            # just in case some of these things have remained
            location = location.replace("Prof.", "")
            location = location.replace("Dr.", "")

            appointment = {
                "start": start_datetime,
                "end": end_datetime,
                "location": location,
                "description": course_dict["CourseName"]
            }
            appointments.append(appointment)
    return appointments

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
    # def handle_entityref(self, name):
    #     print name, chr(name2codepoint[name])
    #     if self.insideTable:
    #         if name in name2codepoint:
    #             self.tableData += unichr(name2codepoint[name])
    #         else:
    #             self.tableData += "&" + name
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
linksFile = open('course_links-2015-Fall-01.csv', 'r')
namesFile = open('course_names-2015-Fall-01.csv', 'r')

coursesList = []

# Parse the Links
for link in linksFile:
    # Get link and print progress
    courseName = namesFile.readline()
    print courseName[:-1]
    # Download the page
    connection = urlopen_with_retry(link)
    page = connection.read()
    encoding = chardet.detect(page)['encoding']
    if encoding != 'unicode':
        page = page.decode(encoding)
        page = page.encode('utf-8', 'ignore')
    # Parse the page
    parser = MyHTMLParser()
    parser.feed(page)
    uglyCourseInfo = parser.getCourseInfo()
    test = json.dumps(uglyCourseInfo)

    if not uglyCourseInfo:
        print "Error: Could not parse this course! Probably a module. Check:", link
        continue

    # Delete the extra stuff and make it a dictionary
    courseInfo = dict(map(lambda x: (cleanuper(x[0]),cleanuper(x[1])), uglyCourseInfo.iteritems() ))
    if not 'Course offering details' in courseInfo:
        print "Error: No label 'Course offering details' abort scanning page"
    if not 'Name' in courseInfo:
        print "Error: No label 'Name' abort scanning page"
    # Get main details about the course
    details = courseInfo['Course offering details']
    detailsMap = {}
    if 'Appointments' in courseInfo:
        detailsMap["Appointments"] = courseInfo['Appointments']
    if 'Literature' in courseInfo:
        detailsMap['Literature'] = courseInfo['Literature']
    # For each field found put it in the map
    for field in importantFields:
        length = len(details)
        if (field+':') in details:
            startIdx = details.find(field + ":") + len(field) + 2
            stopIdx = min( [ (details.find(f+":") if details.find(f+":") >= startIdx else length) for f in importantFields] )
            if startIdx <= stopIdx:
                if startIdx < stopIdx:
                    detailsMap[field] = details[startIdx:stopIdx].strip()
            else:
                print "Error: Start after stop"
    # Parse the Catalogue information
    if 'Contained in course catalogues' in courseInfo:
        catalogue = courseInfo['Contained in course catalogues']
        startIdx = catalogue.find('> ')
        detailsMap['Catalogue'] = "Fall > " + catalogue[startIdx+2:].strip()
    else:
        print "Error: No label 'Contained in course catalogues'"
    detailsMap['Name'] = courseName.strip()
    # Parse for the ID and just course name
    courseID = detailsMap['Name'][0:6]
    courseNameOnly = detailsMap['Name'][7:]
    detailsMap['CourseID'] = courseID
    detailsMap['CourseName'] = courseNameOnly
    detailsMap['CampunetLink'] = link

    #### parse Appointments
    appointments = parse_appointments(detailsMap)
    detailsMap["Appointments"] = appointments

    # Add to our list if it can
    coursesList.append(detailsMap)
    text = json.dumps(detailsMap)

linksFile.close()
namesFile.close()

outputFile = open('course_details-2015-Fall-01.json', 'w')
outputFile.write( json.dumps(coursesList) )
outputFile.close()
