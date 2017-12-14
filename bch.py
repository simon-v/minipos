#!/usr/bin/env python2
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
	'https://api.blockchair.com/bitcoin-cash/dashboards/address/%s',
	'https://api.blocktrail.com/v1/bcc/address/%s?api_key=MY_APIKEY',
	'https://bch-chain.api.btc.com/v3/address/%s',
#	'https://bch-bitcore2.trezor.io/api/addr/%s', # scripts not allowed
#	'https://bitcoincash.blockexplorer.com/api/addr/%s', # scripts not allowed
]
bitpay_url = 'https://bch-insight.bitpay.com/api/addr/%s'
test_explorers = [
]

import urllib, json, random

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
		webpage = urllib.urlopen(url)
		data = json.load(webpage)
		webpage.close()
	except:
		print('Error loading ' % url.split('/')[2])
		raise
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
	#print('Using %s as data source' % block_url.split('/')[2])
	data = jsonload(block_url % address)
	if 'data' in data:
		data = data['data']
	if type(data) is list:
		data = data[0]
	# Particular block explorer quirks
	if 'balance' in data:
		balance = float(data['balance'])
		# BlockTrail requires special handling
		if 'balanceSat' not in data:
			balance /= 100000000
	elif 'sum_value_unspent' in data:
		# BlockChair requires special handling
		balance = float(data['sum_value_unspent']) / 100000000
	else:
		print('Could not decode balance in API response from %s' % block_url.split('/')[2])
		raise ValueError
	if 'unconfirmedBalance' in data:
		unconfirmed = float(data['unconfirmedBalance'])
	elif 'unconfirmed_received' in data:
		# BTC.com has its own unconfirmed balance scheme
		unconfirmed = float(data['unconfirmed_received']) / 100000000
	else:
		# Explorer.Cash does not provide the unconfirmed balance field; Getting it would require an extra query and some calculation
		print('No unconfirmed balance field in API response from %s' % block_url.split('/')[2])
		unconfirmed = 0.0
	return balance, unconfirmed
