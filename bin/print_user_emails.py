from app.models import *

for u in jUser.objects.all():
	print u.email

