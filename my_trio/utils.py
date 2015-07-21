import logging
import hashlib
import urllib
from decimal import Decimal

from flask.json import JSONEncoder

class StructEncoder(JSONEncoder):
	def default(self, o):
		if isinstance(o, Struct):
			return o.__dict__

		#return o
		return super(StructEncoder, self).default(o)


class Struct(object):
	def __init__(self, **kwds):
		for k, v in kwds.items():
			if isinstance(v, dict):
				setattr(self, k, Struct(**v))
			elif isinstance(v, Decimal):
				setattr(self, k, float(v))
			else:
				setattr(self, k, v)

	def __str__(self):
		return "{ %s }" % ", ".join(["%s=%s" % (key, value) for key, value in self.__dict__.items()])

	def __iter__(self):
		return iter(self.__dict__)

	def get(self, key, default = None):
		return self.__dict__.get(key, default)

	def items(self):
		return self.__dict__.items()

class Logger(object):
	def __init__(self, file_handler, logger_name):
		self._log = logging.getLogger(logger_name)
		self._log.addHandler(file_handler)
		self._log.setLevel(file_handler.level)

	def __getattr__(self, *args, **kwds):
		return getattr(self._log, *args, **kwds)


def uri_builder(uri, query):
	return "{0}?{1}".format(uri, urllib.urlencode(query))

def md5_sign_string(string_to_sign):
	return hashlib.md5(string_to_sign).hexdigest()

def get_request_info(request):
	if request.method == "GET":
		request_data = ""
	elif request.method == "POST":
		request_data = unicode(dict(request.form.items()))
	else:
		request_data = unicode(request.text)

	return Struct(request_data=request_data, request_ip=request.remote_addr,
			request_url=request.url, request_method=request.method)

def get_response_info(response):
	headers = Struct(**dict(response.headers.items()))
	return Struct(body=response.text, headers=headers, code=response.status_code)
