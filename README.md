# minipos
## A self-hosted, 0-confirmation Bitcoin Cash point-of-sale server

`minipos` is a simple self-hosted point-of-sale server, intended for use by small merchants and brick-and-mortar stores, that can be operated from any device with a relatively modern web browser.

With `minipos` you can set up receiving Bitcoin Cash payments without exposing your funds to a third party, or even to your own cashiers at any point in the process, by simply giving it a list of Bitcoin Cash addresses to work with.

### Setup

For the server, you will need an Internet-connected computer with Python 3 and the following extra packages:

* `python-qrcode` — _(required)_ for generating payment QR codes
* `python-pil` or `python-pillow` — _(required)_ for generating payment QR codes
* `python-pycoin` — _(optional)_ for generating receiving addresses

The server does not need to be Internet-accessible, unless it is your explicit intention. It can also reside on the same computer you will be connecting from, if convenient.

Place the executable and accompanying library files in a convenient location. Decide where to keep your local data. `minipos` will look for it in the following places:

* `$HOME/.minipos`
* `$HOME/.config/minipos`
* The same directory as the executable and the library files
* The current directory

Copy `minipos.cfg.sample` to `minipos.cfg` in your data directory and edit it to your liking.

Next, create a file in your data directory named `address.list` and put your receiving addresses there, one address per line. You will need at least one address, and at least as many as the number of simultaneous payments you expect to receive (if at no point do you expect to process more than one customer at once, then one receiving address is enough).

Finally, start the `minipos` executable, and take note of this computer's IP address. You will use it to connect to the `minipos` server.

A systemd service file is provided to ease this process.

### Usage

Navigate to the server's address and port from any device with a relatively modern browser.

In the request creation page, enter the amount, taking the multiplier into account; For example, if the multiplier is x0.01 (representing cents), enter two trailing zeroes for whole dollar amounts, as if the cent point is there. Press the green check mark button.

Have your buyer scan the resulting QR code with their Bitcoin Cash wallet and authorize the transaction. Alternatively, you can click/tap on the QR code to copy the request URI to clipboard and send it to your buyer in a text message.

Wait for the transaction to be detected by the system. Press the `Confirm` button and hand the buyer his purchase.

To review your sales, use the built-in log browser, accessible from the triple bar button. You can view a daily, weekly, monthly and yearly summary, print it, or email it to yourself at the configured email address.

A fully-refunding [live demo installation](https://simonvolpert.com/minipos-demo/) with an exposed configuration file is available for demonstrative purposes.

### Customization

If you would like to have a custom header and footer on your log pages, add the relevant HTML to the `log_header.html` and `log_footer.html` files.

Any file placed in the data directory overrides its counterpart in the library directory. Images and other files that you want to be directly accessible to the web browser should be placed in the `assets` subdirectory.

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
