#!/usr/bin/env python2
# bch.py - A Bitcoin Cash utility library
# Author: Simon Volpert <simon@simonvolpert.com>
# This program is free software, released under the Apache License, Version 2.0. See the LICENSE file for more information

price_url = 'https://api.coinmarketcap.com/v1/ticker/bitcoin-cash/'
currency_url = 'http://api.fixer.io/latest?base=USD&symbols=%s'
block_explorers = [
	'https://cashexplorer.bitcoin.com/insight-api/addr/%s',
]
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
	webpage = urllib.urlopen(url)
	data = json.loads(''.join(webpage.readlines()))
	webpage.close()
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
	block_url = random.choice(block_explorers)
	data = jsonload(block_url % address)
	balance = data['balance']
	unconfirmed = data['unconfirmedBalance']
	return balance, unconfirmed
