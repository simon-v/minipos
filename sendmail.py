#!/usr/bin/env python3
# sendmail.py - A mail-sending abstraction library
# Author: Simon Volpert <simon@simonvolpert.com>
# This program is free software, released under the Apache License, Version 2.0. See the LICENSE file for more information

import subprocess
import sys
import smtplib
from email.mime.text import MIMEText

email_from = 'nobody <noreply@localhost.localdomain>'

def send(config, to, subject, text_body, headers={}):
	use_smtp = True
	# Select email backend
	for setting in ['server', 'login', 'passwd']:
		if setting not in config or config[setting] == '':
			use_smtp = False
	if 'email_from' not in config.keys() or config['email_from'] == '':
		config['email_from'] = email_from
	# Create email message
	message = MIMEText(text_body)
	message['From'] = config['email_from']
	message['To'] = to
	message['Subject'] = subject
	message['Auto-Submitted'] = 'auto-generated'
	for header in headers.keys():
		message[header] = headers[header]
	# Send the message
	if use_smtp:
		try:
			server = smtplib.SMTP(config['server'])
			server.login(config['login'], config['passwd'])
			server.sendmail(message['From'], message['To'], message.as_string())
			server.quit()
		except KeyboardInterrupt:
			sys.exit()
		except:
			print('SMTP failed: %s' % sys.exc_info()[1])
			return False
	else:
		try:
			server = subprocess.Popen(['/usr/sbin/sendmail','-i', message['To']], stdin=subprocess.PIPE, stderr=subprocess.PIPE)
			server.communicate(bytes(message.as_string(), 'UTF-8'))
		except:
			print('Sendmail failed: %s' % sys.exc_info()[1])
			return False

	return True
