#!/usr/bin/env python3
# bch.py - A Bitcoin Cash utility library
# Author: Simon Volpert <simon@simonvolpert.com>
# This program is free software, released under the Apache License, Version 2.0. See the LICENSE file for more information

price_url = 'https://api.coinmarketcap.com/v1/ticker/bitcoin-cash/'
currency_url = 'http://api.fixer.io/latest?base=USD&symbols=%s'
block_explorers = [
	'https://cashexplorer.bitcoin.com/insight-api/addr/%s',
#	'https://api.explorer.cash/%s/balance', # bogus data provided
	'https://blockdozer.com/insight-api/addr/%s',
	'https://bccblock.info/api/addr/%s',
#	'https://api.blockchair.com/bitcoin-cash/dashboards/address/%s', # high error rates
#	'https://api.blocktrail.com/v1/bcc/address/%s?api_key=MY_APIKEY', # high error rates
#	'https://bch-chain.api.btc.com/v3/address/%s', # high error rates
#	'https://bch-bitcore2.trezor.io/api/addr/%s', # scripts not allowed
#	'https://bitcoincash.blockexplorer.com/api/addr/%s', # scripts not allowed
]
bitpay_url = 'https://bch-insight.bitpay.com/api/addr/%s'
test_explorers = [
]


import urllib.request
import json
import random
import sys

random.seed()

# float amount -> str formatted amount
def btc(amount):
	result = ('%.8f' % amount).rstrip('0.')
	if result == '':
		return '0'
	return result

def fiat(amount):
	return ('%.2f' % amount)

# str URL -> str JSON data from the URL
def jsonload(url):
	try:
		with urllib.request.urlopen(url) as webpage:
			data = json.load(webpage)
	except:
		raise sys.exc_info()[0]('{exception} ({explorer})'.format(exception=sys.exc_info()[1], explorer=url.split('/')[2]))
	return data

# Get the conversion rate
def get_price(currency):
	data = jsonload(price_url)
	rate = float(data[0]['price_usd'])
	if currency != 'USD':
		data = jsonload(currency_url % currency)
		rate = rate * data['rates'][currency]
	return rate

# Get the address balance
def get_balance(address):
	# BitPay's address scheme is non-standard and only recognized by its own software
	if address.startswith('C') or address.startswith('H'):
		block_url = bitpay_url
	else:
		block_url = random.choice(block_explorers)
	explorer = block_url.split('/')[2]
	data = jsonload(block_url % address)
	#print(data)
	if 'data' in data:
		data = data['data']
	if type(data) is list:
		data = data[0]
	elif data is None:
		raise ValueError(explorer + ' returned empty data')
	# Particular block explorer quirks
	if 'balance' in data:
		balance = float(data['balance'])
		# BTC.com/BlockTrail
		if 'balanceSat' not in data:
			balance /= 100000000
	elif 'sum_value_unspent' in data:
		# BlockChair requires special handling
		balance = float(data['sum_value_unspent']) / 100000000
	else:
		raise ValueError('Could not figure out balance in API response from ' + explorer)
	if 'unconfirmedBalance' in data:
		unconfirmed = float(data['unconfirmedBalance'])
	elif 'unconfirmed_received' in data:
		# BTC.com/BlockTrail
		unconfirmed = float(data['unconfirmed_received']) / 100000000
	else:
		# Explorer.Cash does not provide the unconfirmed balance field; Getting it would require an extra query and some calculation
		print('No unconfirmed balance field in API response from ' + explorer)
		unconfirmed = 0.0
	return balance, unconfirmed
