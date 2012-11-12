from models import User, ApiKeys
from django.http import Http404


def getKey(name):
	#find user, if does not exist in Users table, is not a valid user
	try:
		userObj = User.objects.get(username__iexact=name)
	except ApiKeys.DoesNotExist:
		raise Http404
	#get api key for user, or create new api key if not had one before
	try:
		keyObj = ApiKeys.objects.get(user=userObj.pk)
	except ApiKeys.DoesNotExist:
		keyObj = ApiKeys.objects.create(user=userObj, key=genApiKey(name=name))

	return keyObj.key






def genApiKey(name):
	return 'this is the key for ' + name
