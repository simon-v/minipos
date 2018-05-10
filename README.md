# MiniPOS
## A self-hosted, 0-confirmation Bitcoin Cash point-of-sale server

MiniPOS is a simple self-hosted point-of-sale server, intended for use by small merchants and brick-and-mortar stores, that can be operated from any device with a relatively modern web browser.

With MiniPOS you can set up receiving Bitcoin Cash payments without exposing your funds to a third party, or even to your own cashiers at any point in the process, by simply giving it a list of Bitcoin Cash addresses to work with.

### Setup

For the server, you will need an Internet-connected computer with Python 3 and the following extra packages:

* `python-qrcode` — _(required)_ for generating payment QR codes
* `python-pil` or `python-pillow` — _(required)_ for generating payment QR codes
* `python-urllib3` - _(required)_ for fetching the exchange rate and detecting incoming payments
* `python-pycoin` — _(recommended)_ for generating receiving addresses, key validation and improved block explorer load balancing

The server does not need to be Internet-accessible, unless it is your explicit intention. It can also reside on the same computer you will be connecting from, if convenient.

Place the executable and accompanying library files in a convenient location. Decide where to keep your local data. MiniPOS will look for it in the following places:

* `$HOME/.minipos`
* `$HOME/.config/minipos`
* The same directory as the executable and the library files
* The current directory

A best-practice setup would have the library installed system-wide (e.g., to `/usr/share` or `/opt`) and the data directory per (unprivileged) user.

Copy `minipos.cfg.sample` to `minipos.cfg` in your data directory and edit it to your liking.

Add your extended public key (xpub), or some static receiving addresses to the config file. If using static receiving addresses, you will need to add at least as many as the number of simultaneous payments you expect to receive; So, if at no point do you expect to process more than one customer at once, then one receiving address is enough.

Start the `minipos` executable, either manually, or using the provided systemd service file. Take note of this computer's IP address. You will use it to connect to the MiniPOS server.

### Usage

Navigate to the server's IP address and port from any device with a relatively modern browser.

In the request creation page, enter the amount you wish to charge. You can use the percent button to apply a sales tax or crypto discount to the amount you have entered. Press the green check mark button.

Have your buyer scan the resulting QR code with their Bitcoin Cash wallet and authorize the transaction. Alternatively, you can click/tap on the QR code to copy the request URI to clipboard and send it to your buyer in a text message.

Wait for the transaction to be detected by the system. Press the `Finish` button and hand the buyer his purchase (in any order).

To review your sales, use the built-in log browser, accessible from the triple bar button. You can view a daily, weekly, monthly and yearly summary, print it, or email it to yourself at the configured email address.

A fully-refunding [live demo installation](https://simonvolpert.com/minipos-demo/) with an exposed configuration file is available for demonstrative purposes.

### Customization

The following template files are used to insert content to various pages:

* `templates/welcome_footer.html` — The "welcome" page, under the "Click/tap to begin" invitation
* `templates/log_header.html` — The log viewer, after the navigation buttons and before the summary
* `templates/log_footer.html` — The log browser, in the bottom, after the transaction list
* `templates/invoice_text.html` — The invoice page, the details between the QR code and the control button
* `assets/style.css` — The main front-end stylesheet
* `assets/logo.svg` — The Bitcoin Cash logo on the "welcome" page
* `assets/icon.svg` — The Bitcoin Cash icon, placed before Bitcoin Cash addresses

Additionally, any file placed in the `assets` directory will be served directly to the connecting browser.

### Setting up with a web server

MiniPOS doesn't need a web server to run, as it provides its own. It also doesn't care what the URL used to access it looks like, and will happily serve its content on a bare IP address, a subdomain or a directory. However, if you wish it to be accessible on port 80, you will need to set up a reverse proxy. An example Nginx configuration, similar to the one used by the live demo installation is provided below:

    upstream miniposdemo {
        server 127.0.0.1:8888 max_fails=3;
    }
    
    server {
    #
    # Some server configuration
    #
        location ~ /minipos-demo/ {
            proxy_pass http://miniposdemo;
            proxy_cache off;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_pass_header Server;
        }
    #
    # More server configuration
    #

### Other Notes

This program is free software, released under the Apache License, Version 2.0. See the LICENSE file for more information.

The program's canonical project page resides at https://github.com/simon-v/minipos/

I gratefully accept appreciation for my work in material form at __[bitcoincash:qzm0p0arejsejvlszclvmnqqt93hd5l0vsy78acq88](bitcoincash:qzm0p0arejsejvlszclvmnqqt93hd5l0vsy78acq88)__.

### Similar Projects

* https://github.com/acidsploit/pyxpub and https://github.com/acidsploit/react-pos
* https://github.com/stabwah/cheddrme
* https://github.com/monsterbitar/SPOS4BCH
