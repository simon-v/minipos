#!/usr/bin/env python2
import sys
from wsgiref.simple_server import make_server

# Load and parse the config file
config = {}
try:
	f = open('minipos.cfg', 'r')
	lines = f.readlines()
	f.close()
except:
	print('No configuration file found')
	sys.exit(1)
for line in lines:
	# Skip blank lines and comments
	if line.strip() == '' or line.startswith('#'):
		continue
	# Split to key and value pairs
	words = line.strip().split('=')
	key = words[0].strip()
	value = '='.join(words[1:]).strip()
	config[key] = value
# Sanitize config file
try:
	config['taxrate'] = float(config['taxrate'])
except:
	config['taxrate'] = 0
if 'currencies' not in config.keys():
	config['currencies'] = ['USD']
else:
	config['currencies'] = config['currencies'].split(',')
try:
	config['multiplier'] = float(config['multiplier'])
except:
	config['multiplier'] = 1
if 'addresses' not in config.keys():
	print('Required key `addresses` is missing from configuration file')
	sys.exit(2)
else:
	config['addresses'] = config['addresses'].split(',')

# Utility wrapper function
def load_file(filename):
	src = open(filename, 'r')
	data = ''.join(src.readlines())
	src.close()
	return data

def minipos(environ, start_response):
	filler = ()
	request = environ['PATH_INFO'].lstrip('/').split('/')[-1]
	if request.endswith('.css'):
		headers = [('Content-type', 'text/css')]
	elif request.endswith('.js'):
		headers = [('Content-type', 'text/javascript')]
	elif request.endswith('.txt'):
		headers = [('Content-type', 'text/plain')]
	else:
		headers = [('Content-type', 'text/html')]
		request = 'request.html'
		filler = (config['currencies'][0], config['taxrate'])
	try:
		page = load_file(request) % filler
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
