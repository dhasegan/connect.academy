from app.models import *
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User, check_password
from django.db.models import Q

def send_email_confirmation(user,confirmation_link):
	fname = user.first_name
	lname = user.last_name
	email = user.email
	message = "Dear " + fname + ",\r\n"
	message +="Thank you for registering with Link.Academy!\r\n"
	message += "Please confirm your account by entering the following URL in the address bar:\r\n\r\n"
	message += confirmation_link + "\r\n\r\n"
	message += "Greetings,\r\n"
	message += "The Link.academy Team.\r\n"

	
	send_mail("Link.academy Account Confirmation", message,"Link.Academy <noreply@link-academy.com>",[email],fail_silently=False)

class jUserBackend(object):
	def authenticate(self, username=None, password=None):
		try:
			user = jUser.objects.get(Q(email = username)|Q(username=username))
			if user.check_password(password):
				return user
		except jUser.DoesNotExist:
			return None 

	def get_user(self, user_id):
		try:
			return jUser.objects.get(pk=user_id)
		except jUser.DoesNotExist:
			return None