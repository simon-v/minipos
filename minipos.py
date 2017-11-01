#!/usr/bin/env python2
from wsgiref.simple_server import make_server

def load_file(filename):
	src = open(filename, 'r')
	data = ''.join(src.readlines())
	src.close()
	return data

def minipos(environ, start_response):
	request = environ['PATH_INFO'].lstrip('/').split('/')[-1]
	if request.endswith('.css'):
		headers = [('Content-type', 'text/css')]
	elif request.endswith('.js'):
		headers = [('Content-type', 'text/javascript')]
	elif request.endswith('.txt'):
		headers = [('Content-type', 'text/plain')]
	else:
		headers = [('Content-type', 'text/html')]
		request = 'invoice.html'
	try:
		page = load_file(request)
	except:
		status = '404 NOT FOUND'
		headers = []
		page = ''
	else:
		status = '200 OK'
	start_response(status, headers)

	return [page]

# Start the web server
httpd = make_server('', 8080, minipos)
print('Serving minipos on port 8080...')
try:
	httpd.serve_forever()
except:
	print('Server stopped.')
