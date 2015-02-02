from icalendar import *
#the function is used for formatting the string
#@param date_string A string of the form YYYY-mm-ddTHH:MM:SS.uuuuuu+(HHMM | HH:MM)
#@return formatted_string The string with milliseconds (as opposed to microseconds)
def format_date(date_string):
	before = date_string[:23]
	after = date_string[26:]
	return before+after


def pretty_print(calendar):
	return calendar.to_ical().replace('\r\n', '<br>').strip()

# Truncates a string of the form "YYYYmmddTHMSuuuuuu" to
# "YYYYmmddTHMSuu" which is RFC2445 compliant.
def to_ical_date(date_string,aware=False):
	if not aware:
		return date_string[:-6]
	else:
		return date_string[:-6]+"Z"


# The function check whether 'calendar' represents a 
# valid Calendar object. Note that the function distinguishes
# between import and export. 
#
# On 'export' mode: 
# 	Only the correct formatting of the dates 
# 	(since the structure is fixed, and dates are annoying little shits)
# 	is checked. Returns True/False
# 
# On 'import' mode:  
# 	A parse is attempted, if successful a valid calendar object is returned,
# 	else NONE is returned.
def validate_ical(calendar, purpose='export'):

	if purpose=='import':
		cal = None
		try:
			cal = Calendar.from_ical(calendar)
		except Exception:
			pass
		return cal

	if purpose=='export':
		return True
		
	return False