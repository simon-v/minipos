# minipos
## A self-hosted, 0-confirmation Bitcoin Cash point-of-sale server

`minipos` is a simple self-hosted point-of-sale server, intended for use by small merchants and brick-and-mortar stores, that can be operated from any device with a relatively modern web browser.

With `minipos` you can set up receiving Bitcoin Cash payments without exposing your funds to a third party, or even to your own cashiers at any point in the process, by simply giving it a list of Bitcoin Cash addresses to work with.

__Setup__

You will need an Internet-connected computer with Python 2 and `python-qrcode` installed as the server. It does not need to be Internet-accessible, unless it is your explicit intention. It can also reside on the same computer you will be connecting from, if convenient.

Place the executable, the accompanying library and configuration files in a convenient location. Copy `minipos.cfg.sample` to `minipos.cfg` and edit it to your liking.

Next, create a file named `address.list` and put your receiving addresses there, one address per line. You will need at least one address, and at least as many as the number of simultaneous payments you expect to receive (if at no point do you expect to process more than one customer at once, then one receiving address is enough).

Finally, start the `minipos` executable, and take note of this computer's IP address. You will use it to connect to the `minipos` server.

__Usage__

Navigate to the server's address and port from any device with a relatively modern browser.

In the request creation page, enter the amount, taking the multiplier into account; For example, if the multiplier is x0.01 (representing cents), enter two trailing zeroes for whole dollar amounts, as if the cent point is there. Press the green check mark button.

Have your buyer scan the resulting QR code with their Bitcoin Cash wallet and authorize the transaction.

Wait for the transaction to be detected by the system. Press the `Confirm` button and hand the buyer his purchase.

To review your sales, use the built-in log browser, accessible from the triple bar button. You can view a daily, weekly, monthly and yearly summary, print it, or email it to yourself at the configured email address.

__Other Notes__

This program is free software, released under the Apache License, Version 2.0. See the LICENSE file for more information.

The program's canonical project page resides at https://github.com/simon-v/minipos/

I gratefully accept appreciation for my work in material form at __13JSnRst7PJiMUr6fyVAkFWTwf9XKivWLh__.

