#!/usr/bin/env python2
import sys
from wsgiref.simple_server import make_server
import urlparse

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

def create_invoice(parameters):
	if 'currency' not in parameters:
		parameters['currency'] = config['currencies']
	currency = parameters['currency'][0]
	amount = float(parameters['amount'][0]) * config['multiplier']
	filler = ('0.00000000', amount, currency,
		config['addresses'][0],
		'650', currency)
	page = load_file('invoice.html') % filler
	return page

# Main webapp function
def minipos(environ, start_response):
	internal = False
	filler = ()
	request = environ['PATH_INFO'].lstrip('/').split('/')[-1]
	parameters = urlparse.parse_qs(environ['QUERY_STRING'])
	if request == 'style.css':
		headers = [('Content-type', 'text/css')]
	elif request == 'scripts.js':
		headers = [('Content-type', 'text/javascript')]
		filler = (repr(config['currencies']))
	elif request == 'invoice':
		headers = [('Content-type', 'text/html')]
		page = create_invoice(parameters)
		internal = True
	else:
		headers = [('Content-type', 'text/html')]
		request = 'request.html'
		if len(config['currencies']) == 1:
			disabled = 'disabled'
		else:
			disabled = ''
		filler = (disabled, config['currencies'][0], config['currencies'][0], config['taxrate'])
	try:
		if not internal:
			page = load_file(request) % filler
	except:
		status = '404 NOT FOUND'
		headers = []
		page = ''
		raise
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
