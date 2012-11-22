from django.http import Http404
from datetime import datetime as dt
from models import *

#Methods here should take a tastypie bundle
#they should return the modified bundle or 
#raise a Http404('error description')

def handleRegister(bundle):
	
	username = bundle.data.get('user')
	email = bundle.data.get('email')
	pwHash = bundle.data.get('passw')
	if User.objects.filter(username__iexact=username).count() != 0:
		raise Http404('Username aleady in use')
	if User.objects.filter(email__iexact=email).count() != 0:
		raise Http404('Email aleady in use')
	try:
		newUser = User.objects.create(username=username, email=email, pwHash=pwHash, lastLogin=dt.now())
		bundle.obj = newUser
	except Exception:
		raise Http404('An error occurred when creating the account')

	return bundle