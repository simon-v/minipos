#!/usr/bin/env python3
# bch.py - A Bitcoin Cash utility library
# Author: Simon Volpert <simon@simonvolpert.com>
# This program is free software, released under the Apache License, Version 2.0. See the LICENSE file for more information

import urllib.request
import json
import random
import sys
#optional import pycoin.key
#optional import cashaddr # Local library file

MAX_ERRORS = 10
exchanges = [
	{
		'url': 'https://api.coinmarketcap.com/v1/ticker/bitcoin-cash/?convert={cur}',
		'price_key': '0.price_{cur_lower}',
	},
	{
		'url': 'https://api.coinbase.com/v2/exchange-rates?currency=BCH',
		'price_key': 'data.rates.{cur}',
	},
	{
		'url': 'https://apiv2.bitcoinaverage.com/indices/global/ticker/short?crypto=BCH&fiat={cur}',
		'price_key': 'BCH{cur}.last',
	},
	{
		# Extremely limited ticker set
		'url': 'https://api.kraken.com/0/public/Ticker?pair=BCH{cur}',
		'price_key': 'result.BCH{cur}.c.0',
	},
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
		'prefixes': 'qp',
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

# Initialize explorer and exchange list
random.seed()
random.shuffle(explorers)
for i in range(len(explorers)):
	explorers[i]['name'] = '.'.join(explorers[i]['url'].split('/')[2].split('.')[-2:])
for i in range(len(exchanges)):
	exchanges[i]['name'] = '.'.join(exchanges[i]['url'].split('/')[2].split('.')[-2:])
del(i) # Cleanup for help(bch)

def btc(amount):
	'''Return a native bitcoin amount representation'''
	result = ('%.8f' % amount).rstrip('0.')
	if result == '':
		return '0'
	return result

def bits(amount):
	'''Return the amount represented in bits/cash'''
	bit, sat = fiat(amount * 1000000).split('.')
	sat = sat.rstrip('0')
	if sat == '':
		return bit
	return(bit + '.' + sat)

def fiat(amount):
	'''Return the amount represented in a dollar/cent notation'''
	return ('%.2f' % amount)

def jsonload(url):
	'''Load a web page and return the resulting JSON object'''
	request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
	with urllib.request.urlopen(request) as webpage:
		data = str(webpage.read(), 'UTF-8')
		data = json.loads(data)
	return data

def get_value(json_object, key_path):
	'''Get the value at the end of a dot-separated key path'''
	# Workaround for explorers that return "null" for unused addresses
	error = bool(json_object['err_no']) if 'err_no' in json_object else False
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
		except TypeError:
			if not error:
				return 0
			raise
	return json_object

def get_price(currency, exchange=exchanges[0]['name']):
	'''Get the current Bitcoin Cash price in the desired currency'''
	found = False
	for server in exchanges:
		if server['name'] == exchange:
			found = True
			break
	if not found:
		raise KeyError('{src} is not in list of exchanges'.format(src=config['price_source']))
	data = jsonload(server['url'].format(cur=currency, cur_lower=currency.lower()))
	rate = float(get_value(data, server['price_key'].format(cur=currency, cur_lower=currency.lower())))
	if rate == 0.0:
		raise ValueError('Returned exchange rate is zero')
	return round(rate, 2)

def get_balance(address, explorer=None, verify=False, confirmed_only=False):
	'''Get the current balance of an address from a block explorer
Returns tuple(confirmed_balance, unconfirmed_balance)

Keyword arguments:
address         (str) bitcoin_address or tuple(str xpub, int index)
explorer        (str) the name of a specific explorer to query
verify          (bool) the results should be verified with another explorer
confirmed_only  (bool) ignore servers without a separate unconfirmed balance'''
	# Generated address request
	xpub = None
	if type(address) is tuple:
		xpub, idx = address
	# Strip prefix
	elif address[0].lower() == 'b':
		address = address.split(':')[1]
	# Normalize case
	if address[0] in 'QP':
		address = address.lower()
	# Add a temporary separator
	server = None
	results = []
	while True:
		# Cycle to the next server
		explorers.append(server)
		server = explorers.pop(0)
		# Populate server error count if necessary
		if server is not None and 'errors' not in server:
			server['errors'] = 0
		# If the end of the server list was reached without a single success, assume a network error
		if server is None:
			for i in range(len(explorers)):
				if explorers[i]['errors'] > 0:
					explorers[i]['errors'] -= 1
			if results == []:
				raise ConnectionError('Connection error')
			return(results[-1])
		# Select only the desired server if requested
		if explorer is not None and server['name'] != explorer:
			continue
		# Avoid servers with excessive errors
		if server['errors'] > MAX_ERRORS:
			continue
		#print(server['name']) # DEBUG
		# Convert wrong address type
		if xpub is None and address[0] not in server['prefixes']:
			try:
				address = convert_address(address)
			except ImportError:
				continue
		# Generate address if necessary
		if xpub is not None:
			if 'q' in server['prefixes'] or 'p' in server['prefixes']:
				address = generate_address(xpub, idx)
			else:
				address = generate_address(xpub, idx, False)
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

def generate_address(xpub, idx, cash=True):
	'''Generate a bitcoin cash or bitcoin legacy address from the extended public key at the given index'''
	# Optional dependencies if unused
	import pycoin.key
	import cashaddr
	subkey = pycoin.key.Key.from_text(xpub).subkey(0).subkey(idx)
	if cash:
		return cashaddr.encode('bitcoincash', 0, subkey.hash160())
	return subkey.address()

def validate_key(key):
	'''Check the validity of a key or an address'''
	# Optional dependencies if unused
	import pycoin.key
	import cashaddr
	if ':' in key:
		key = key.split(':')[1]
	if key[0] in '13x':
		try:
			pycoin.key.Key.from_text(key)
		except pycoin.encoding.EncodingError:
			return False
	elif key[0] in 'qpQP':
		try:
			subkey = cashaddr.decode('bitcoincash:' + key.lower())
		except ValueError:
			return False
	else:
		return False
	return True

def convert_address(address):
	'''Convert an address back and forth between cash and legacy formats'''
	# Optional dependencies if unused
	import pycoin.key
	import cashaddr
	if address[0] in '13':
		subkey = pycoin.key.Key.from_text(address)
		return cashaddr.encode('bitcoincash', 0, subkey.hash160())
	elif address[0] in 'qpQP':
		subkey = cashaddr.decode('bitcoincash:' + address.lower())[2]
		return pycoin.key.Key(hash160=subkey).address()
	else:
		raise ValueError('Unsupported address format')

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
		except (KeyError, ValueError, urllib.error.HTTPError):
			print('{src} does not provide {cur} exchange rate: {err}'.format(src=server['name'], cur=cur, err=sys.exc_info()[1]))
			support = False
		except KeyboardInterrupt:
			sys.exit()
		if support:
			print(server['name'])
