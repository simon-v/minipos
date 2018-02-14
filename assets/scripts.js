// HTTP request wrapper
function loadHTTP(url, callback) {
	var xmlhttp = new XMLHttpRequest();
	xmlhttp.onreadystatechange = function() {
		if (xmlhttp.readyState == 4 && callback) {
			callback(xmlhttp.responseText.trim());
		}
	};
	xmlhttp.open("GET", url, true);
	xmlhttp.send();
}

// Check if JavaScript is enabled
function jsCheck() {
	loadHTTP('check?id=0', jsCheckReady);
}
function jsCheckReady(code) {
	if ( code == 2 ) {
		document.getElementById("begin").style.display = "block";
		document.getElementById("noscript").style.display = "none";
	}
}

// Form button controls
function textAppend(value) {
	document.getElementById("amountbox").value += value;
	validateInput();
	return_timer = 0;
}
function textRemove() {
	var field = document.getElementById("amountbox"),
	value = field.value;
	field.value = value.substring(0, value.length - 1);
	return_timer = 0;
}
function addCents() {
	if ( document.getElementById("cents").value == "00" ) {
		textAppend(0);
		textAppend(0); // To allow validation to trigger
	}
	else {
		var field = document.getElementById("amountbox"),
		value = field.value;
		if ( !~ value.indexOf(".") ) {
			field.value = value + ".";
		}
		validateInput();
	}
	return_timer = 0;
}

// Form input validation
function validateInput() {
	var field = document.getElementById("amountbox"),
	value = field.value;
	// Decimal number leading zero
	if ( value[0] == "." ) {
		field.value = "0" + value;
	}
	// Two decimal places
	else if ( ~ value.indexOf(".") && value.length - value.indexOf(".") > 3 ) {
		textRemove();
	}
	// Leading zeroes
	else if ( value.length > 1 && value[0] == "0" && value[1] != "." ) {
		field.value = value.substring(1, value.length);
	}
	// Numbers only
	else if ( !~ "1234567890.".indexOf(value[value.length - 1]) ) {
		field.value = value.substring(0, value.length - 1);
	}
}

// Add the tax to the entered amount
function addTax() {
	var field = document.getElementById("amountbox"),
	percents = document.getElementById("percents").innerHTML,
	tax = percents.substring(0, percents.length - 1) / 100.0 + 1;
	if ( document.getElementById("cents").value == "." ) {
		var decimals = 2;
	}
	else {
		var decimals = 0;
	}
	field.value = (field.value * tax).toFixed(decimals);
	if ( field.value.substring(field.value.length - 3, field.value.length) == ".00" ) {
		field.value = field.value.substring(0, field.value.length - 3);
	}
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
	if ( response == 1 ) {
		document.getElementById("cancel").style.display = "none";
		document.getElementById("finish").style.display = "inline";
		displayPopup("Payment received.");
	}
	else if ( response == 2 ) {
		displayPopup("The payment request has timed out.");
	}
	else {
		setTimeout(checkPayment, 2000);
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
