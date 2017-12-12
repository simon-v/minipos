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

// Form button controls
function textAppend(value) {
	document.getElementById("amountbox").value += value;
}
function textRemove() {
	var field = document.getElementById("amountbox"),
	value = field.value;
	field.value = value.substring(0, value.length - 1);
}

// Add the tax to the entered amount
function addTax() {
	var field = document.getElementById("amountbox"),
	percents = document.getElementById("percents").innerHTML,
	tax = percents.substring(0, percents.length - 1) / 100 + 1;
	field.value = (field.value * tax).toFixed(0);
}

// Cycle currency sign
var currencies = %s,
cur = 1;
function cycleCurrency() {
	var button = document.getElementById("currency");
	button.value = currencies[cur++ %% currencies.length];
	document.getElementById("currencybox").value = button.value;
}

// Turn cancel button into confirm button
function showConfirmButton(response) {
	if (response == 1) {
		document.getElementById("cancel").style.display = "none";
		document.getElementById("finish").style.display = "inline";
	}
	else {
		setTimeout(checkPayment, 5000);
	}
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
		document.getElementById("popup_text").innerHTML = "The email was sent to the configured address.";
	}
	else {
		document.getElementById("popup_text").innerHTML = "There was an error sending the email.";
	}
	document.getElementById("popup").style.display = "block";
}
function dismissPopup() {
	document.getElementById("popup_text").innerHTML = "";
	document.getElementById("popup").style.display = "none";
}
