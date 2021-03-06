"""
The Auth file contains functions required to validate, register and generate passwords for users

"""

from models import User, ApiKeys
from django.http import Http404
import random
import hashlib

#get the api key for the provided user, or create one if one doesnt exist yet
#package this into 
def checkLogin(bundle):
	name = bundle.data.get('user')
	passw = bundle.data.get('passw')


	#find user, if does not exist in Users table, is not a valid user
	try:
		userObj = User.objects.get(username__iexact=name)
	except Exception:
		raise Http404('Invalid Username')
	if userObj.pwHash == encryptPass(passw, name):
		#get api key for user, or create new api key if not had one before
		bundle.data = {}
		bundle.data['user'] = userObj.username
		try:
			bundle.data['key'] = ApiKeys.objects.get(user=userObj.pk).key
		except ApiKeys.DoesNotExist:
			bundle.data['key'] = ApiKeys.objects.create(user=userObj, key=genApiKey(name=name)).key
		return bundle
	else:
		raise Http404('Invalid Password')


#salt password and then encrypt with SHA-1.  Needs to be repeatable for validating login requests
def encryptPass(passw, username):
	h = hashlib.sha1()
	h.update('adgi43g3g' + passw + '4352fmv' + username.lower())
	return str(h.hexdigest())

#generate an API key for name, salt with some random bits
def genApiKey(name):
	random.seed()
	bits = str(random.getrandbits(24))
	h = hashlib.sha1()
	h.update('apikey' + name + bits)
	return str(h.hexdigest())

#check provided key matches key stored against user record
def validKey(name, key):
	try:
		userObj = User.objects.get(username__iexact=name)
		storedKey = ApiKeys.objects.get(user=userObj.pk)
		if storedKey.key == key:
			return True
		else:
			return False
	except Exception:
		return False
