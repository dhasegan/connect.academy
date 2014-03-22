from app.models import *
from django.core.mail import send_mail
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


