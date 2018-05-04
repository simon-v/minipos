#!/usr/bin/env python3
# tridenticon - A visual hash generator
# Author: Simon Volpert <simon@simonvolpert.com>
# Project page: https://github.com/simon-v/tridenticon/
# This program is free software, released under the Apache License, Version 2.0. See the LICENSE file for more information
# Consult the README file for usage instructions and other helpful hints
# Running with --test requires ImageMagick

import hashlib
import colorsys
import PIL.Image
import os
import sys
import subprocess

def generate(data, scale=1):
	'''Generate an identicon from the passed data, scaled to the given value'''
	image = PIL.Image.new('RGB', (7, 7), '#ffffff')
	# Prepare data
	if type(data) is str:
		data = bytes(data, 'UTF-8')
	elif type(data) is not bytes:
		data = bytes(data)
	# Calculate a checksum
	digest = hashlib.md5(data).hexdigest()
	c = 0
	iterator = iter(range(len(digest)))
	# Get the next color
	def get_color():
		try:
			color = digest[iterator.__next__()] + digest[iterator.__next__()]
		except StopIteration:
			return
		color = int(color, 16)
		color = tuple(int(i * 255) for i in colorsys.hsv_to_rgb(color / 255, 0.5, 0.75))
		return color

	color = get_color()
	erase = False
	for i in iterator:
		# Calculate coordinates to paint
		p = int(digest[i], 16)
		y, x = divmod(p, 3)
		# Treat out-of-bounds as an erase command
		if y == 5:
			erase = True
			continue
		if erase:
			image.putpixel((x + 1, y + 1), (255, 255, 255))
			image.putpixel((x * -1 + 5, y + 1), (255, 255, 255))
			erase = False
		# Paint the coordinates symmetrically
		elif image.getpixel((x + 1, y + 1)) == (255, 255, 255):
			image.putpixel((x + 1, y + 1), color)
			image.putpixel((x * -1 + 5, y + 1), color)
			# Switch colors for a 7/4/3/2 distribution
			c += 1
			if c == 7 or c == 11:
				color = get_color()
			elif c == 14:
				break
	# Output image
	image = image.resize((7 * scale, 7 * scale))
	return image # Use .show() to preview

if __name__ == '__main__':
	usage = '''Usage:	tridenticon DATA [SCALE]
	tridenticon --test'''
	try:
		data = sys.argv[1]
	except (IndexError):
		print(usage)
		sys.exit(1)
	try:
		scale = int(sys.argv[2])
	except IndexError:
		scale = 8
	except ValueError:
		print(usage)
	if data == '--test' and scale == 8:
		t = 0
		tmp = []
		for i in range(32, 127): # All printable characters on the keyboard
			image = generate(chr(i), 8)
			image.save('tridenticon.tmp%s.png' % t)
			tmp.append('tridenticon.tmp%s.png' % t)
			t += 1
		try:
			subprocess.call(['montage', '-geometry', '+0+0'] + tmp + ['tridenticon.png'])
			print('tridenticon.png written')
		finally:
			for i in tmp:
				os.unlink(i)
	else:
		image = generate(data, scale)
		image.save('tridenticon.png')
