from dispatch.response import Response

class Test(object):
	def handler(self, req, path, ajax=False):
		if ajax:
			return Response('Booh from an ajax-request!')
		return Response('Boeh! :)')
