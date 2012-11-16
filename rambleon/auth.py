from models import User, ApiKeys
from django.http import Http404
from django.utils import simplejson

#get for api key for the provided user, or create one if (for some reason) one doesnt exist
def checkLogin(getRequest):#getRequest is request.GET object
	name = getRequest.get('user')
	passw = getRequest.get('passw')
	print name
	print passw
	#find user, if does not exist in Users table, is not a valid user
	try:
		userObj = User.objects.get(username__iexact=name)
	except Exception:
		return 'invalid'
	if userObj.pwHash == passw:
		#get api key for user, or create new api key if not had one before
		try:
			keyObj = ApiKeys.objects.get(user=userObj.pk)
		except ApiKeys.DoesNotExist:
			keyObj = ApiKeys.objects.create(user=userObj, key=genApiKey(name=name))
		return keyObj.key
	else:
		return 'invalid'



def genApiKey(name):
	return 'thisisthekeyfor' + name


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