#the function is used for formatting the string
#@param date_string A string of the form YYYY-dd-mmTHH:MM:SS.uuuuuu+(HHMM | HH:MM)
#@return formatted_string The string with milliseconds (as opposed to microseconds)
def format_date(date_string):
	before = date_string[:23]
	after = date_string[26:]
	return before+after
