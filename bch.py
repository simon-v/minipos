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
		'tx_url': 'https://cashexplorer.bitcoin.com/api/tx/{txid}',
		'balance_key': None,
		'confirmed_key': 'balance',
		'unconfirmed_key': 'unconfirmedBalance',
		'last_tx_key': 'transactions.0',
		'tx_time_key': 'time',
		'tx_inputs_key': 'vin',
		'tx_in_double_spend_key': 'doubleSpentTxID',
		'tx_outputs_key': 'vout',
		'tx_out_value_key': 'value',
		'tx_out_address_key': 'scriptPubKey.addresses.0',
		'tx_fee_key': 'fees',
		'unit_satoshi': False,
		'prefixes': '13',
	},
	{
		'url': 'https://blockdozer.com/insight-api/addr/bitcoincash:{address}',
		'tx_url': 'https://blockdozer.com/insight-api/tx/{txid}',
		'balance_key': None,
		'confirmed_key': 'balance',
		'unconfirmed_key': 'unconfirmedBalance',
		'last_tx_key': 'transactions.0',
		'tx_time_key': 'time',
		'tx_inputs_key': 'vin',
		'tx_in_double_spend_key': 'doubleSpentTxID',
		'tx_outputs_key': 'vout',
		'tx_out_value_key': 'value',
		'tx_out_address_key': 'scriptPubKey.addresses.0',
		'tx_fee_key': 'fees',
		'unit_satoshi': False,
		'prefixes': 'qp',
	},
	{
		'url': 'https://bccblock.info/api/addr/{address}',
		'tx_url': 'https://bccblock.info/api/tx/{txid}',
		'balance_key': None,
		'confirmed_key': 'balance',
		'unconfirmed_key': 'unconfirmedBalance',
		'last_tx_key': 'transactions.0',
		'tx_time_key': 'time',
		'tx_inputs_key': 'vin',
		'tx_in_double_spend_key': 'doubleSpentTxID',
		'tx_outputs_key': 'vout',
		'tx_out_value_key': 'value',
		'tx_out_address_key': 'scriptPubKey.addresses.0',
		'tx_fee_key': 'fees',
		'unit_satoshi': False,
		'prefixes': '13',
	},
	{
		'url': 'https://bch-insight.bitpay.com/api/addr/{address}',
		'tx_url': 'https://bch-insight.bitpay.com/api/tx/{txid}',
		'balance_key': 'balance',
		'confirmed_key': None,
		'unconfirmed_key': 'unconfirmedBalance',
		'last_tx_key': 'transactions.0',
		'tx_time_key': 'time',
		'tx_inputs_key': 'vin',
		'tx_in_double_spend_key': 'doubleSpentTxID',
		'tx_outputs_key': 'vout',
		'tx_out_value_key': 'value',
		'tx_out_address_key': 'scriptPubKey.addresses.0',
		'tx_fee_key': 'fees',
		'unit_satoshi': False,
		'prefixes': 'qp',
	},
	{
		'url': 'https://bch-chain.api.btc.com/v3/address/{address}',
		'tx_url': 'https://bch-chain.api.btc.com/v3/tx/{txid}',
		'balance_key': 'data.balance',
		'confirmed_key': None,
		'unconfirmed_key': 'data.unconfirmed_received',
		'last_tx_key': 'data.last_tx',
		'tx_time_key': 'data.created_at',
		'tx_outputs_key': 'data.outputs',
		'tx_out_value_key': 'value',
		'tx_out_address_key': 'addresses.0',
		'tx_double_spend_key': 'data.is_double_spend',
		'tx_fee_key': 'fee',
		'unit_satoshi': True,
		'prefixes': '13',
	},
	{
		'url': 'https://bch-bitcore2.trezor.io/api/addr/{address}',
		'tx_url': 'https://bch-bitcore2.trezor.io/api/tx/{txid}',
		'balance_key': None,
		'confirmed_key': 'balance',
		'unconfirmed_key': 'unconfirmedBalance',
		'last_tx_key': 'transactions.0',
		'tx_time_key': 'time',
		'tx_inputs_key': 'vin',
		'tx_in_double_spend_key': 'doubleSpentTxID',
		'tx_outputs_key': 'vout',
		'tx_out_value_key': 'value',
		'tx_out_address_key': 'scriptPubKey.addresses.0',
		'tx_fee_key': 'fees',
		'unit_satoshi': False,
		'prefixes': '13',
	},
	{
		'url': 'https://bitcoincash.blockexplorer.com/api/addr/{address}',
		'tx_url': 'https://bitcoincash.blockexplorer.com/api/tx/{txid}',
		'balance_key': None,
		'confirmed_key': 'balance',
		'unconfirmed_key': 'unconfirmedBalance',
		'last_tx_key': 'transactions.0',
		'tx_time_key': 'time',
		'tx_inputs_key': 'vin',
		'tx_in_double_spend_key': 'doubleSpentTxID',
		'tx_outputs_key': 'vout',
		'tx_out_value_key': 'value',
		'tx_out_address_key': 'scriptPubKey.addresses.0',
		'tx_fee_key': 'fees',
		'unit_satoshi': False,
		'prefixes': '13',
	},
]

# Initialize explorer and exchange list
random.seed()
random.shuffle(explorers)
for _server in explorers:
	_server['name'] = '.'.join(_server['url'].split('/')[2].split('.')[-2:])
for _server in exchanges:
	_server['name'] = '.'.join(_server['url'].split('/')[2].split('.')[-2:])

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
			if not error:
				return False
			raise KeyError('Key "{k}" from "{key_path}" not found in JSON'.format(k=k, key_path=key_path))
		except (TypeError, IndexError):
			if not error:
				return False
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

def pick_explorer(server_name=None, address_prefix=None):
	'''Advance the list of explorers until one that matches the requirements is found'''
	for __ in explorers:
		# Cycle to the next server
		server = explorers.pop(0)
		if server is None:
			raise StopIteration('Server list depleted')
		explorers.append(server)
		# Populate server error count if necessary
		if 'errors' not in server:
			server['errors'] = 0
			server['last_error'] = None
			server['last_data'] = None
		# Filter by server name
		if server_name is not None and server['name'] != server_name:
			continue
		# Filter by error rate
		if server['errors'] > MAX_ERRORS and server['name'] != server_name:
			continue
		# Filter by address prefix
		if address_prefix is not None and address_prefix not in server['prefixes']:
			continue
		return server
	raise KeyError('No servers match the requirements')

class AddressInfo(object):
	'''A representation of a block explorer's idea of a bitcoin address state

Provided properties:
address         (str) the address in cash format
legacy_address  (str) the address in legacy format
confirmed       (float) the confirmed balance of the address
unconfirmed     (float) the unconfirmed balance of the address
'''

	def __init__(self, address, explorer=None, verify=False):
		'''Keyword arguments:
address         (str) bitcoin_address or tuple(str xpub, int index)
explorer        (str) the name of a specific explorer to query
verify          (bool) the results should be verified with another explorer
'''
		# Incompatible parameters
		if verify and explorer is not None:
			raise ValueError('The "verify" and "explorer" parameters are incompatible')
		# Generated address request
		xpub = None
		idx = None
		if type(address) is tuple:
			xpub, idx = address
		# Strip prefix
		elif address[0].lower() == 'b':
			address = address.split(':')[1]
		# Normalize case
		if address[0] in 'QP':
			address = address.lower()
		# Generate all address versions
		if address[0] in 'qp':
			self.address = address
			self.legacy_address = None
		elif address[0] in '13':
			self.address = None
			self.legacy_address = address
		try:
			import pycoin.key
			import cashaddr
		except ImportError:
			pass
		else:
			if xpub is not None:
				self.address = generate_address(xpub, idx)
				self.legacy_address = generate_address(xpub, idx, False)
			elif self.address is None:
				self.address = convert_address(self.legacy_address)
			elif self.legacy_address is None:
				self.legacy_address = convert_address(self.address)
		# Add a temporary separator
		explorers.append(None)
		results = []
		# Figure out specific address type availability
		if self.address is not None and self.legacy_address is not None:
			prefixes = 'qp13'
		elif self.legacy_address is None:
			prefixes = 'qp'
		else:
			prefixes = '13'
		while explorers[0] is not None:
			# Query the next explorer
			if prefixes == 'qp13':
				server = pick_explorer(explorer)
			else:
				server = pick_explorer(explorer, address_prefix=prefixes[0])
			# Try to get balance
			try:
				# Get and cache the received data for possible future analysis
				if 'q' in server['prefixes']:
					json = jsonload(server['url'].format(address=self.address))
				else:
					json = jsonload(server['url'].format(address=self.legacy_address))
				server['last_data'] = json
				# Conditional balance processing
				# TODO: This is a mighty convoluted way of doing it and needs rethinking
				if server['confirmed_key'] is not None and server['unconfirmed_key'] is not None:
					confirmed = float(get_value(json, server['confirmed_key']))
					unconfirmed = float(get_value(json, server['unconfirmed_key']))
				elif server['confirmed_key'] is not None and server['balance_key'] is not None:
					confirmed = float(get_value(json, server['confirmed_key']))
					balance = float(get_value(json, server['balance_key']))
					unconfirmed = balance - confirmed
				elif server['unconfirmed_key'] is not None and server['balance_key'] is not None:
					balance = float(get_value(json, server['balance_key']))
					unconfirmed = float(get_value(json, server['unconfirmed_key']))
					confirmed = balance - unconfirmed
				else:
					raise RuntimeError('Cannot figure out address balance')
				# Get the last txid
				try:
					txid = get_value(server['last_data'], server['last_tx_key'])
				except (KeyError, IndexError):
					txid = None
				if not txid:
					txid = None
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
			data = (confirmed, unconfirmed, txid)
			if verify:
				if data not in results:
					results.append(data)
					continue
			results.append(data)
			break
		# If the end of the server list was reached without a single success, assume a network error
		explorers.remove(None)
		if results == []:
			for server in explorers:
				if server['errors'] > 0:
					server['errors'] -= 1
			raise ConnectionError('Connection error')
		# Populate instance attributes
		self.confirmed, self.unconfirmed, self.last_txid = results[-1]

def get_balance(address, explorer=None, verify=False):
	'''Get the current balance of an address from a block explorer
Takes the same arguments as AddressInfo()
Returns tuple(confirmed_balance, unconfirmed_balance)
'''
	addr = AddressInfo(address, explorer, verify)
	return addr.confirmed, addr.unconfirmed

def get_last_txid(address, explorer=None, verify=False):
	'''Get the last tx associated with an address
Takes the same arguments as AddressInfo()
Returns str(txid)
'''
	addr = AddressInfo(address, explorer, verify)
	return addr.last_txid

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
