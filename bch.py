#!/usr/bin/env python3
# bch.py - A Bitcoin Cash utility library
# Author: Simon Volpert <simon@simonvolpert.com>
# This program is free software, released under the Apache License, Version 2.0. See the LICENSE file for more information

import urllib.request
import json
import random
import sys
import datetime
import logging
#optional import pycoin.key
#optional import cashaddr # Local library file

MAX_ERRORS = 10
TIMEOUT = 5
exchanges = [
	{
		'url': 'https://api.coinmarketcap.com/v2/ticker/1831/?convert={cur}',
		'price_key': 'data.quotes.{cur}.price',
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
		'tx_double_spend_key': None,
		'tx_fee_key': 'fees',
		'tx_size_key': 'size',
		'tx_confirmations_key': 'confirmations',
		'unit_satoshi': False,
		'prefixes': '13',
	},
	{
		'url': 'https://blockdozer.com/api/addr/{address}',
		'tx_url': 'https://blockdozer.com/api/tx/{txid}',
		'balance_key': None,
		'confirmed_key': 'balance',
		'unconfirmed_key': 'unconfirmedBalance',
		'last_tx_key': 'transactions.-1',
		'tx_time_key': 'time',
		'tx_inputs_key': 'vin',
		'tx_in_double_spend_key': 'doubleSpentTxID',
		'tx_outputs_key': 'vout',
		'tx_out_value_key': 'value',
		'tx_out_address_key': 'scriptPubKey.addresses.0',
		'tx_double_spend_key': None,
		'tx_fee_key': 'fees',
		'tx_size_key': 'size',
		'tx_confirmations_key': 'confirmations',
		'unit_satoshi': False,
		'prefixes': 'qp13',
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
		'tx_double_spend_key': None,
		'tx_fee_key': 'fees',
		'tx_size_key': 'size',
		'tx_confirmations_key': 'confirmations',
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
		'tx_inputs_key': 'data.inputs',
		'tx_in_double_spend_key': None,
		'tx_outputs_key': 'data.outputs',
		'tx_out_value_key': 'value',
		'tx_out_address_key': 'addresses.0',
		'tx_double_spend_key': 'data.is_double_spend',
		'tx_fee_key': 'data.fee',
		'tx_size_key': 'data.vsize',
		'tx_confirmations_key': 'data.confirmations',
		'unit_satoshi': True,
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
		'tx_double_spend_key': None,
		'tx_fee_key': 'fees',
		'tx_size_key': 'size',
		'tx_confirmations_key': 'confirmations',
		'unit_satoshi': False,
		'prefixes': '13',
	},
	{
		'url': 'https://rest.bitbox.earth/v1/address/details/{address}',
		'tx_url': 'https://rest.bitbox.earth/v1/transaction/details/{txid}',
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
		'tx_double_spend_key': None,
		'tx_fee_key': 'fees',
		'tx_size_key': 'size',
		'tx_confirmations_key': 'confirmations',
		'unit_satoshi': False,
		'prefixes': 'qp13',
	},
]

# Initialize explorer and exchange list
random.seed()
random.shuffle(explorers)
for _server in explorers:
	# Using urllib.parse here would require an instruction similar to this:
	#     _server['name'] = '.'.join(urllib.parse.urlparse(_server['url'])[1].split('.')[-2:])
	# Which is neither any shorter, nor simpler, AND requires an additional import to work
	_server['name'] = '.'.join(_server['url'].split('/')[2].split('.')[-2:])
for _server in exchanges:
	_server['name'] = '.'.join(_server['url'].split('/')[2].split('.')[-2:])


def btc(amount):
	'''Return a native bitcoin amount representation'''
	result = ('%.8f' % float(amount)).rstrip('0.')
	if result == '':
		return '0'
	return result


def bits(amount):
	'''Return the amount represented in bits/cash'''
	amount = fiat(float(amount) * 1000000)
	if amount.endswith('.00'):
		amount = amount[:-3]
	return amount


def fiat(amount):
	'''Return the amount represented in a dollar/cent notation'''
	return ('%.2f' % float(amount))


def color(amount):
	'''Return the amount as colorized HTML'''
	# Inspired by Thomas Zander's proposal; Reference:
	# https://twitter.com/FloweeTheHub/status/996341710027403265
	# Only works for white or near-white background!
	wholes, sats = '{:.8f}'.format(float(amount)).split('.')
	mils = sats[0:3]
	bits = sats[3:6]
	sats = sats[6:8]
	whole_color = 'gray' if wholes == '0' else 'black'
	dot_color = 'lightgray' if mils == '000' and bits == '000' and sats == '00' else 'gray'
	mil_color = 'lightgray' if mils == '000' and bits == '000' and sats == '00' else 'green'
	bit_color = 'lightgray' if bits == '000' and sats == '00' else 'darkgreen'
	if sats == '00':
		sats = '&mdash;'
	result = '''<span style="color: {}">{}</span><span style="color: {}; padding-left: 0">.</span><span style="color: {}; padding-left: 0">{}</span><span style="color: {}; padding-left: 0.25em">{}</span><span style="color: gray; padding-left: 0.25em">{}</span>'''.format(whole_color, wholes, dot_color, mil_color, mils, bit_color, bits, sats)
	return result


def jsonload(url):
	'''Load a web page and return the resulting JSON object'''
	request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
	with urllib.request.urlopen(request, timeout=TIMEOUT) as webpage:
		data = str(webpage.read(), 'UTF-8')
		data = json.loads(data)
	return data


def get_value(json_object, key_path):
	'''Get the value at the end of a dot-separated key path'''
	# Make sure the explorer did not return an error
	if 'err_no' in json_object:
		if json_object['err_no'] == 1:
			raise urllib.error.HTTPError(None, 404, 'Resource Not Found', None, None)
		elif json_object['err_no'] == 2:
			raise urllib.error.HTTPError(None, 400, 'Parameter Error', None, None)
	for k in key_path.split('.'):
		# Process integer indices
		try:
			k = int(k)
		except ValueError:
			pass
		# Expand the key
		try:
			json_object = json_object[k]
		except (TypeError, IndexError):
			# The key rightfully doesn't exist
			return False
	return json_object


def get_price(currency, exchange=exchanges[0]['name']):
	'''Get the current Bitcoin Cash price in the desired currency'''
	found = False
	for server in exchanges:
		if server['name'] == exchange:
			found = True
			break
	if not found:
		raise KeyError('{src} is not in list of exchanges'.format(src=exchange))
	data = jsonload(server['url'].format(cur=currency.upper(), cur_lower=currency.lower()))
	rate = float(get_value(data, server['price_key'].format(cur=currency.upper(), cur_lower=currency.lower())))
	if rate == 0.0:
		raise ValueError('Returned exchange rate is zero')
	return round(rate, 2)


def pick_explorer(server_name=None, address_prefix=None, ignore_errors=False):
	'''Advance the list of explorers until one that matches the requirements is found'''
	for __ in explorers:
		# Cycle to the next server
		server = explorers.pop(0)
		if server is None:
			raise StopIteration('Server list depleted')
		explorers.append(server)
		# Populate server error count if necessary
		if 'errors' not in server:
			logging.debug('Adding control fields to {} definition'.format(server['name']))
			server['errors'] = 0
			server['last_error'] = None
			server['last_data'] = None
		# Filter by server name
		if server_name is not None and server['name'] != server_name:
			continue
		# Filter by error rate
		if not ignore_errors and server['errors'] > MAX_ERRORS:
			logging.debug('Skipping {} based on error rates'.format(server['name']))
			continue
		# Filter by address prefix
		if address_prefix is not None and address_prefix not in server['prefixes']:
			logging.debug('Skipping {} due to unsupported address prefix'.format(server['name']))
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

	def __init__(self, address, explorer=None, verify=False, ignore_errors=False):
		'''Keyword arguments:
address         (str) bitcoin_address or tuple(str xpub, int index)
explorer        (str) the name of a specific explorer to query
verify          (bool) the results should be verified with another explorer
ignore_errors   (str) don't skip explorers disabled for excessive errors
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
			if xpub is not None:
				self.address = generate_address(xpub, idx)
				self.legacy_address = generate_address(xpub, idx, False)
			elif self.address is None:
				self.address = convert_address(self.legacy_address)
			elif self.legacy_address is None:
				self.legacy_address = convert_address(self.address)
		except ImportError:
			if xpub is not None:
				raise
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
				server = pick_explorer(explorer, ignore_errors=ignore_errors)
			else:
				server = pick_explorer(explorer, address_prefix=prefixes[0], ignore_errors=ignore_errors)
			# Try to get balance
			try:
				# Get and cache the received data for possible future analysis
				logging.debug('Querying {}'.format(server['name']))
				if 'q' in server['prefixes']:
					json = jsonload(server['url'].format(address=self.address))
				else:
					json = jsonload(server['url'].format(address=self.legacy_address))
				server['last_data'] = self.raw_data = json
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
					logging.error('Excessive errors from {server}, disabling. Last error: {error}'.format(server=server['name'], error=server['last_error']))
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
			raise ConnectionError('No results from any known block explorer')
		# Populate instance attributes
		self.confirmed, self.unconfirmed, self.last_txid = results[-1]


def get_balance(address, explorer=None, verify=False, ignore_errors=False):
	'''Get the current balance of an address from a block explorer
Takes the same arguments as AddressInfo()
Returns tuple(confirmed_balance, unconfirmed_balance)
'''
	addr = AddressInfo(address, explorer, verify, ignore_errors)
	return addr.confirmed, addr.unconfirmed


def get_last_txid(address, explorer=None, verify=False, ignore_errors=False):
	'''Get the last tx associated with an address
Takes the same arguments as AddressInfo()
Returns str(txid)
'''
	addr = AddressInfo(address, explorer, verify, ignore_errors)
	return addr.last_txid


class TxNotFoundError(Exception):
	'''Raised when a requested txid is not known to any block explorer'''


class TxInfo(object):
	'''A representation of a block explorer's idea of a bitcoin transaction

Provided properties:
time          (datetime) the time this transaction was first seen or mined
outputs       (dict) a mapping of receiving addresses to receiving values
              both address formats are provided if possible
double_spend  (bool) whether or not this transaction has a competing transaction
fee           (float) the transaction fee
confirmations (int) the number of confirmations this transaction has

Will raise TxNotFoundError if the passed txid is not known to any explorer
'''

	def __init__(self, txid, explorer=None, ignore_errors=None):
		'''Keyword arguments:

txid          (str) the txid to look for
explorer      (str) the name of a specific explorer to query
ignore_errors (str) don't skip explorers disabled for excessive errors
'''
		# Add a temporary separator
		explorers.append(None)
		#tx_size = 10
		while explorers[0] is not None:
			# Query the next explorer
			try:
				server = pick_explorer(explorer, ignore_errors=ignore_errors)
			except StopIteration:
				break
			try:
				# Get and cache the received data for possible future analysis
				logging.debug('Querying {}'.format(server['name']))
				json = jsonload(server['tx_url'].format(txid=txid))
				server['last_data'] = self.raw_data = json
				# Figure out if the tx is a double spend
				if server['tx_double_spend_key'] is not None:
					self.double_spend = get_value(json, server['tx_double_spend_key'])
				else:
					self.double_spend = False
					for i, __ in enumerate(get_value(json, server['tx_inputs_key'])):
						#tx_size += 148
						try:
							if get_value(json, '.'.join([server['tx_inputs_key'], str(i), server['tx_in_double_spend_key']])) is not None:
								self.double_spend = True
						# Workaround for explorers that don't provide empty double spend keys
						except KeyError as k:
							if str(k).strip('\'') != server['tx_in_double_spend_key']:
								raise
				# Assemble list of output values
				self.outputs = {}
				for i, __ in enumerate(get_value(json, server['tx_outputs_key'])):
					#tx_size += 34
					addr = get_value(json, '.'.join([server['tx_outputs_key'], str(i), server['tx_out_address_key']]))
					value = float(get_value(json, '.'.join([server['tx_outputs_key'], str(i), server['tx_out_value_key']])))
					if server['unit_satoshi']:
						value /= 100000000
					if addr[0] in 'bB':
						addr = addr.lower().split(':')[1]
					self.outputs[addr] = value
					# Provide both address formats if possible
					try:
						self.outputs[convert_address(addr)] = value
					except ImportError:
						pass
				# Figure out the tx size and fee
				self.fee = float(get_value(json, server['tx_fee_key']))
				#self.size = tx_size
				self.size = get_value(json, server['tx_size_key'])
				if server['unit_satoshi']:
					self.fee /= 100000000
				self.fee_per_byte = self.fee / self.size * 100000000
				self.time = datetime.datetime.fromtimestamp(get_value(json, server['tx_time_key']))
				self.confirmations = get_value(json, server['tx_confirmations_key'])
				break
			except KeyboardInterrupt:
				explorers.remove(None)
				raise
			except:
				exception = sys.exc_info()[1]
				if isinstance(exception, urllib.error.HTTPError) and exception.code == 404:
					continue
				server['errors'] += 1
				try:
					server['last_error'] = str(exception.reason)
				except AttributeError:
					server['last_error'] = str(exception)
				if server['errors'] > MAX_ERRORS:
					logging.error('Excessive errors from {server}, disabling. Last error: {error}'.format(server=server['name'], error=server['last_error']))
				continue
		try:
			explorers.remove(None)
		except ValueError:
			pass
		if self.__dict__ == {}:
			raise TxNotFoundError('No results from any known block explorer')


def get_tx_propagation(txid, threshold=100, callback=None, stop_on_double_spend=False, ignore_errors=False):
	'''Estimate a transaction's propagation across the Bitcoin Cash network
Returns a tuple consisting of:
  * The percentage of explorers that are aware of the txid;
  * The transaction's double spend status.

Keyword arguments:
txid       The txid to query
threshold  A percentage at which the propagation check is considered finished
callback   A function which will be called after every explorer query
           The function will be called with the perliminary results
stop_on_double_spend
           The check will be aborted as soon as a double spend is detected
'''
	sightings = 0
	double_spend = False
	num_servers = len(explorers)
	propagation = 0
	for server in explorers.copy():
		if not ignore_errors and 'errors' in server and server['errors'] > MAX_ERRORS:
			num_servers -= 1
			continue
		try:
			tx = TxInfo(txid, explorer=server['name'], ignore_errors=ignore_errors)
		except TxNotFoundError:
			continue
		except KeyboardInterrupt:
			raise
		except:
			exception = sys.exc_info()[1]
			try:
				error = exception.reason
			except AttributeError:
				error = exception
			logging.error('Could not fetch explorer data: {}'.format(error))
			continue
		if tx.double_spend:
			double_spend = True
		sightings += 1
		propagation = 100 * sightings / num_servers
		if callback is not None:
			callback(propagation, double_spend)
		if propagation >= threshold:
			break
		elif double_spend and stop_on_double_spend:
			break
	return propagation, double_spend


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
			cashaddr.decode('bitcoincash:' + key.lower())
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
	if address[0] in 'bB':
		address = address.split(':')[1]
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
			get_price(cur, exchange=server['name'])
		except (KeyError, ValueError, urllib.error.HTTPError):
			error = sys.exc_info()[1]
			try:
				error = error.reason
			except AttributeError:
				pass
			if isinstance(error, KeyError):
				error = 'Key error: ' + str(error)
			print('{src} does not provide {cur} exchange rate: {error}'.format(src=server['name'], cur=cur, error=error))
			support = False
		except KeyboardInterrupt:
			sys.exit()
		except NameError:
			pass
		if support:
			print(server['name'])
