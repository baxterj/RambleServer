from django.test import TestCase
import auth
import hashlib

class TestAuth(TestCase):
	def test_pass_encryption(self):
		passw= 'hello123'
		username='CAts'
		h = hashlib.sha1()
		h.update('adgi43g3g' + passw + '4352fmv' + username.lower())
		self.assertEqual(auth.encryptPass(passw, username), h.hexdigest())