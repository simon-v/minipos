// HTTP request wrapper
function loadHTTP(url, callback) {
	var xmlhttp = new XMLHttpRequest();
	xmlhttp.onreadystatechange = function() {
		if (xmlhttp.readyState == 4) {
			callback(xmlhttp.responseText.trim());
		}
	};
	xmlhttp.open("GET", url, true);
	xmlhttp.send();
}

// Check if JavaScript is enabled
function jsCheck() {
	document.getElementById("begin").style.display = "block";
}

// Form button controls
function textAppend(value) {
	document.getElementById("amountbox").value += value;
	return_timer = 0;
}
function textRemove() {
	var field = document.getElementById("amountbox"),
	value = field.value;
	field.value = value.substring(0, value.length - 1);
	return_timer = 0;
}

// Add the tax to the entered amount
function addTax() {
	var field = document.getElementById("amountbox"),
	percents = document.getElementById("percents").innerHTML,
	tax = percents.substring(0, percents.length - 1) / 100 + 1;
	field.value = (field.value * tax).toFixed(0);
	return_timer = 0;
}

// Cycle currency sign
var cur = 1;
function cycleCurrency() {
	var button = document.getElementById("currency");
	button.value = currencies[cur++ % currencies.length];
	document.getElementById("currencybox").value = button.value;
	return_timer = 0;
}

// Turn cancel button into confirm button
function showConfirmButton(response) {
	if (response == 1) {
		document.getElementById("cancel").style.display = "none";
		document.getElementById("finish").style.display = "inline";
		displayPopup("Payment received.");
	}
	else if (response == -1) {
		displayPopup("The payment request has timed out.");
	}
	else {
		setTimeout(checkPayment, 5000);
	}
}

// Display an informational popup dialog
function displayPopup(text) {
	document.getElementById("popup_text").innerHTML = text;
	document.getElementById("popup").style.display = "block";
}

// Check whether or not payment was made
function checkPayment() {
	if (document.getElementById("finish").style.display == "none") {
		loadHTTP("check?" + request_string, showConfirmButton);
	}
}

// Open the log page
function openLogs(date) {
	if ( date )  {
		window.open("logs?date=" + date, "_self", true);
	}
	else {
		window.open("logs", "_self", true);
	}
}
function sendEmail(date) {
	if ( date ) {
		loadHTTP("email?date=" + date, emailSent);
	}
	else {
		loadHTTP("email", emailSent);
	}
}
function emailSent(response) {
	if ( response == 1 ) {
		displayPopup("The email was sent to the configured address.");
	}
	else {
		displayPopup("There was an error sending the email.");
	}
}
function dismissPopup() {
	document.getElementById("popup_text").innerHTML = "";
	document.getElementById("popup").style.display = "none";
}

// Automatically return to the welcome page after a timeout
var return_timer = 0;
function returnTimer() {
	if ( welcome_timeout > 0 ) {
		return_timer++;
		if ( return_timer == welcome_timeout ) {
			window.open("welcome", "_self");
		}
		else {
			setTimeout(returnTimer, 1000);
		}
	}
}

// Copy-to-clipboard
function copy() {
	var field = document.getElementById("copy");
	// Only process if there is no current popup
	if ( document.getElementById("popup").style.display == "none" ) {
		try {
			field.style.display = "block";
			field.select();
			document.execCommand("copy");
			field.blur();
		}
		finally {
			displayPopup("Copied to clipboard.");
			setTimeout(dismissPopup, 1000);
			field.style.display = "none";
		}
	}
}
