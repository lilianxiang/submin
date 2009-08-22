import os

from dispatch.view import View
from dispatch.response import Response, Redirect
from views.error import ErrorResponse
from template import evaluate
from config.authz.htpasswd import NoMD5PasswordError
from models.user import User

class Login(View):
	def handler(self, request, path):
		config = Config()
		if not request.post:
			return self.evaluate_form(config)
		username = request.post.get('username', '')
		password = request.post.get('password', '')

		try:
			if not config.htpasswd.check(username, password):
				return self.evaluate_form(config, 'Not a valid username and password combination')
		except NoMD5PasswordError, e:
			return self.evaluate_form(config, str(e))

		url = '/'
		if 'redirected_from' in request.session:
			url = request.session['redirected_from']

		user = User(username)
		user.is_authenticated = True
		request.session['user'] = user
		request.session.save()
		return Redirect(url)


	def evaluate_form(self, config, msg=''):
		localvalues = {}
		localvalues['msg'] = msg
		localvalues['base_url'] = config.base_url
		return Response(evaluate('login.html', localvalues))


class Logout(View):
	def handler(self, request, path):
		if 'user' in request.session:
			request.session['user'].is_authenticated = False
			del request.session['user']
		url = '/'
		if 'redirected_from' in request.session:
			url = request.session['redirected_from']
		return Redirect(url)

