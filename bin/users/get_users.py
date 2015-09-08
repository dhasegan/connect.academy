 #!/usr/bin/env python

# Used jpeople.py. To recrawl run: python get_users <college_name>
# It will make a file named <college_name>.json with all people from that college

# CONFIG

# There should be no need to change this.

# Where is jPeople?
jpeople_server_name = "jpeople.user.jacobs-university.de"
jpeople_server_path = "/ajax.php"
jpeople_server_image_prefix = "/utils/images/"
jpeople_server_image_suffix = ".jpg";

# Additional headers
jpeople_search_headers = {
	"Accept-Charset":"ISO-8859-1,utf-8;q=0.7,*;q=0.3",
	"Referer": "http://jpeople.user.jacobs-university.de/"
}

# Map for property names
# Anything not in here will be removed
jpeople_attr_map = {
	"id": "id",
	"eid": "eid",
	"fname": "fname",
	"lname": "lname",
	"birthday": "birthday",
	"country": "country",
	"college": "college",
	"majorlong": "majorlong",
	"majorinfo": "majorinfo",
	"major": "major",
	"status": "status",
	"year": "year",
	"room": "room",
	"phone": "phone",
	"email": "email",
	"description": "description",
	"title": "title",
	"deptinfo": "deptinfo",
	"block": "block",
	"floor": "floor",
	"photo": "photo",
	"account": "account",
}

# end CONFIG


# IMPORTS

# Common imports
import sys
import json


if sys.version_info >= (3, 0):
	# Python3
	import http.client as httplib
	from urllib.parse import quote as urllib_quote

	unicode = str # Unicode fix

else:
	# Python2
	import httplib
	from urllib import quote as urllib_quote


# CORE FUNCTIONS

def search(query):
	"""Return an array of jpeople results for the given search. """
	try:
		query = urllib_quote(query) # We have to quote it.
		# Make a connection
		conn = httplib.HTTPConnection(jpeople_server_name)
		conn.request("GET", jpeople_server_path+"?action=fullAutoComplete&str="+query, "", jpeople_search_headers)
		
		# Get the response
		conn_respone = conn.getresponse()
		if conn_respone.status == 200:
			# Get the result into a tree
			people_tree = json.loads(unicode(conn_respone.read(), errors="ignore"))["records"]

			# Set an empty result stack
			people_list = []

			# Lets make it a hash-style-object
			for person in people_tree:

				# A Directory for the person
				person_dict = {}


				for tag in person:
					# We want to rename some properties
					if tag in jpeople_attr_map.keys():
						tag = jpeople_attr_map[tag]
						if person[tag]==None:
							person_dict[tag] = ""
						else:
							person_dict[tag] = person[tag].replace("\n", "")

				person_dict["photo"] = "http://"+jpeople_server_name+jpeople_server_image_prefix+person_dict["eid"]+jpeople_server_image_suffix
				people_list.append(person_dict)

			# Return the list of all the lovely people
			return people_list

		else:
			return False
	except Exception:
		return False

# MAIN Function
# if run stand alone

def main(args):
	"""Makes a search for people in jPeople"""

	# Get the search string (Just joining of the arguments)
	search_str = " ".join(args[1:])

	if search_str == "":
		# It is empty, we should print some help.
		print("jPeople API Client (Python)")
		print("(c) Tom Wiesing 2013")
		print("Usage: "+args[0]+" $SEARCH")
		sys.exit(0)

	# Get the search result and check for errors
	try:
		people = search(search_str)
		if not people:
			raise Exception
	except Exception:
		print("Search failed. ")
		print("Please make sure you are in the Jacobs University Network / VPN. ")
		sys.exit(1)

	# Function for nice output
	def out(obj, item, pre="", post=""):
		if item in obj.keys():
			data = obj[item]
			if data=='':
				return
			print(pre+obj[item]+post)

	# Print the results
	result = json.dumps(people)
	json_file = open(search_str+".json", "w")
	json_file.write(result)

	if False:
		for person in people:		
			out(person, 'lname', post=", "+person['fname'])
			out(person, 'attributes', post=", "+person['description'])
			out(person, 'college', pre='College: ')
			out(person, 'office', pre='Office: ')
			out(person, 'room')
			out(person, 'email')
			out(person, 'phone', pre="(0421) 200 ")
			out(person, 'country', pre="Country: ")
			out(person, 'majorinfo', pre="Major: ")
			out(person, 'id', pre="ID: ")
			print("--")

	sys.exit(0)

# Check if we are stand alone
if __name__ == "__main__":
	main(sys.argv)

