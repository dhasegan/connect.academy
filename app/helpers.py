from app.models import *
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User, check_password
from django.core.urlresolvers import reverse
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Q

def send_email_confirmation(user,host):
	fname = user.first_name
	email = user.email
	confirmation_hash = default_token_generator.make_token(user)
	confirmation_link = ("http://%s%s" %  (host, reverse('confirmation', args=(user.username, confirmation_hash))))
	delete_link = ("http://%s%s" %  (host, reverse('delete', args=(user.username, confirmation_hash))))
	if len(fname) == 0:
		fname = user.username
	message = "Dear " + fname + ",\r\n"
	message +="Thank you for registering with Connect.Academy!\r\n"
	message +="An account has been created with this e-mail address. \r\n"
	message += "Please confirm your account by entering the following URL in the address bar:\r\n\r\n"
	message += confirmation_link + "\r\n\r\n"
	message += "If you did not register with Link.Academy, you can ignore this message, in which case "
	message += "we will delete the account in 3 days. If you wish to delete the account now, you can enter "
	message += "the following URL in the address bar:\r\n\r\n"
	message += delete_link + "\r\n\r\n"
	message += "Greetings,\r\n"
	message += "The Connect.academy Team.\r\n"

	
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