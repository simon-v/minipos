#!/usr/bin/env python3
# bch.py - A Bitcoin Cash utility library
# Author: Simon Volpert <simon@simonvolpert.com>
# This program is free software, released under the Apache License, Version 2.0. See the LICENSE file for more information

MAX_ERRORS = 10
currency_url = 'http://api.fixer.io/latest?base=USD&symbols={cur}'
exchanges = [
	{
		'url': 'https://api.coinmarketcap.com/v1/ticker/bitcoin-cash/?convert={cur}',
		'price_key': '0.price_{cur_lower}',
	},
	{
		'url': 'https://api.coinbase.com/v2/exchange-rates?currency=BCH',
		'price_key': 'data.rates.{cur}',
	}
]
explorers = [
	{
		'url': 'https://cashexplorer.bitcoin.com/api/addr/{address}',
		'balance_key': 'balance',
		'confirmed_key': None,
		'unconfirmed_key': 'unconfirmedBalance',
		'unit_satoshi': False,
		'prefixes': '13',
	},
	{
		'url': 'https://blockdozer.com/insight-api/addr/{address}',
		'balance_key': 'balance',
		'confirmed_key': None,
		'unconfirmed_key': 'unconfirmedBalance',
		'unit_satoshi': False,
		'prefixes': '13',
	},
	{
		'url': 'https://blockdozer.com/insight-api/addr/bitcoincash:{address}',
		'balance_key': 'balance',
		'confirmed_key': None,
		'unconfirmed_key': 'unconfirmedBalance',
		'unit_satoshi': False,
		'prefixes': 'qp',
	},
	{
		'url': 'https://bccblock.info/api/addr/{address}',
		'balance_key': 'balance',
		'confirmed_key': None,
		'unconfirmed_key': 'unconfirmedBalance',
		'unit_satoshi': False,
		'prefixes': '13',
	},
	{
		'url': 'https://bch-insight.bitpay.com/api/addr/{address}',
		'balance_key': 'balance',
		'confirmed_key': None,
		'unconfirmed_key': 'unconfirmedBalance',
		'unit_satoshi': False,
		'prefixes': 'CH',
	},
	{
		# Non-realtime source; https://github.com/Blockchair/Blockchair.Support/blob/master/API.md
		'url': 'https://api.blockchair.com/bitcoin-cash/dashboards/address/{address}',
		'balance_key': None,
		'confirmed_key': 'data.0.sum_value_unspent',
		'unconfirmed_key': None,
		'unit_satoshi': True,
		'prefixes': 'qp13',
	},
	{
		'url': 'https://bch-chain.api.btc.com/v3/address/{address}',
		'balance_key': 'data.balance',
		'confirmed_key': None,
		'unconfirmed_key': 'data.unconfirmed_received',
		'unit_satoshi': True,
		'prefixes': '13',
	},
	{
		'url': 'https://bch-bitcore2.trezor.io/api/addr/{address}',
		'balance_key': 'balance',
		'confirmed_key': None,
		'unconfirmed_key': 'unconfirmedBalance',
		'unit_satoshi': False,
		'prefixes': '13',
	},
	{
		'url': 'https://bitcoincash.blockexplorer.com/api/addr/{address}',
		'balance_key': 'balance',
		'confirmed_key': None,
		'unconfirmed_key': 'unconfirmedBalance',
		'unit_satoshi': False,
		'prefixes': '13',
	},
#	'https://api.explorer.cash/%s/balance', # broken
#	'https://api.blocktrail.com/v1/bcc/address/%s?api_key=MY_APIKEY', # API key required
]


import urllib.request
import json
import random
import sys

# Initialize explorer and exchange list
random.seed()
random.shuffle(explorers)
for i in range(len(explorers)):
	explorers[i]['errors'] = 0
	explorers[i]['name'] = explorers[i]['url'].split('/')[2]
for i in range(len(exchanges)):
	exchanges[i]['name'] = exchanges[i]['url'].split('/')[2]

# float amount -> str formatted amount
def btc(amount):
	result = ('%.8f' % amount).rstrip('0.')
	if result == '':
		return '0'
	return result

def bits(amount):
	bit, sat = fiat(amount * 1000000).split('.')
	sat = sat.rstrip('0')
	if sat == '':
		return bit
	return(bit + '.' + sat)

def fiat(amount):
	return ('%.2f' % amount)

# str URL -> str JSON data from the URL
def jsonload(url):
	request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
	with urllib.request.urlopen(request) as webpage:
		data = json.load(webpage)
	return data

# Return the value at the end of the key hierarchy in the json object
def get_value(json_object, key_path):
	for k in key_path.split('.'):
		# Process integer indices
		try:
			k = int(k)
		except ValueError:
			pass
		# Expand the key
		try:
			json_object = json_object[k]
		except KeyError:
			raise KeyError('Key "{k}" from "{key_path}" not found in JSON'.format(k=k, key_path=key_path))
	return json_object

# Get the conversion rate
def get_price(currency, config={'price_source': exchanges[0]['name']}):
	found = False
	for server in exchanges:
		if server['name'] == config['price_source']:
			found = True
			break
	if not found:
		raise KeyError('{src} is not in list of exchanges'.format(src=config['price_source']))
	try:
		data = jsonload(server['url'].format(cur=currency, cur_lower=currency.lower()))
	except KeyboardInterrupt:
		raise
	rate = float(get_value(data, server['price_key'].format(cur=currency, cur_lower=currency.lower())))
	if rate == 0.0:
		raise KeyError('{src} does not provide {cur} exchange rate'.format(src=server['name'], cur=currency))
	return rate

# Get the address balance
def get_balance(address, config={}, verify=False):
	if address.startswith('b'):
		address = address.split(':')[1]
	confirmed_only = True if 'unconfirmed' not in config else not config['unconfirmed']
	# If the passed config defines a custom explorer, use that instead
	try:
		custom_explorer = {
			'name': config['custom_explorer_url'].split('/')[2],
			'url': config['custom_explorer_url'],
			'balance_key': config['custom_balance_key'],
			'confirmed_key': config['custom_confirmed_key'],
			'unconfirmed_key': config['custom_unconfirmed_key'],
			'unit_satoshi': config['custom_unit_satoshi'],
			'prefixes': 'qp13CH', # Accept all prefixes by default
			'errors': 0
		}
	except KeyError:
		pass
	else:
		explorers.clear()
		explorers.append(custom_explorer)
	# Add a temporary separator
	server = None
	results = []
	while True:
		# Cycle to the next server
		explorers.append(server)
		server = explorers.pop(0)
		# If the end of the server list was reached without a single success, assume a network error
		if server is None:
			for i in range(len(explorers)):
				if explorers[i]['errors'] > 0:
					explorers[i]['errors'] -= 1
			if results == []:
				raise ConnectionError('Connection errors when trying to fetch balance')
			return(results[-1])
		# Wrong address type
		if address[0] not in server['prefixes']:
			continue
		# Avoid servers with excessive errors
		if server['errors'] > MAX_ERRORS:
			continue
		# Try to get balance
		try:
			# Conditional balance processing
			# TODO: This is a mighty convoluted way of doing it and needs rethinking
			if server['confirmed_key'] is not None and server['unconfirmed_key'] is not None:
				json = jsonload(server['url'].format(address=address))
				confirmed = float(get_value(json, server['confirmed_key']))
				unconfirmed = float(get_value(json, server['unconfirmed_key']))
			elif server['confirmed_key'] is not None and server['balance_key'] is not None:
				json = jsonload(server['url'].format(address=address))
				confirmed = float(get_value(json, server['confirmed_key']))
				balance = float(get_value(json, server['balance_key']))
				unconfirmed = balance - confirmed
			elif server['unconfirmed_key'] is not None and server['balance_key'] is not None:
				json = jsonload(server['url'].format(address=address))
				balance = float(get_value(json, server['balance_key']))
				unconfirmed = float(get_value(json, server['unconfirmed_key']))
				confirmed = balance - unconfirmed
			elif confirmed_only and server['confirmed_key'] is not None:
				json = jsonload(server['url'].format(address=address))
				confirmed = float(get_value(json, server['confirmed_key']))
				unconfirmed = 0.0
			elif not confirmed_only and server['balance_key'] is not None:
				json = jsonload(server['url'].format(address=address))
				balance = float(get_value(json, server['balance_key']))
				confirmed = balance
				unconfirmed = 0.0
			else:
				continue
		except KeyboardInterrupt:
			explorers.remove(None)
			raise
		except:
			server['errors'] += 1
			exception = sys.exc_info()[1]
			try:
				server['last_error'] = str(exception.reason)
			except AttributeError:
				server['last_error'] = str(exception)
			if server['errors'] > MAX_ERRORS:
				print('Excessive errors from {server}, disabling. Last error: {error}'.format(server=server['name'], error=server['last_error']))
			continue
		# Convert balances to native units
		if server['unit_satoshi']:
			confirmed /= 100000000
			unconfirmed /= 100000000
		if server['errors'] > 0:
			server['errors'] -= 1
		if verify:
			if (confirmed, unconfirmed) not in results:
				results.append((confirmed, unconfirmed))
				continue

		break
	# Clean up
	explorers.append(server)
	explorers.remove(None)
	return confirmed, unconfirmed

if __name__ == '__main__':
	print('===== Known block explorers =====')
	for server in explorers:
		print(server['name'])
	try:
		cur = sys.argv[1].upper()
		print('\n===== Known exchange rate sources with {cur} support ====='.format(cur=cur))
	except IndexError:
		print('\n===== Known exchange rate sources =====')
	for server in exchanges:
		support = True
		try:
			get_price(cur, config={'price_source': server['name']})
		except KeyError:
			print(sys.exc_info()[1])
			support = False
		if support:
			print(server['name'])
