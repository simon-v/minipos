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
	title = document.getElementById("tax").title,
	tax = title.substring(0, title.length - 1) / 100 + 1;
	field.value = (field.value * tax).toFixed(0);
}

// Cycle currency sign
var currencies = %s,
cur = 1;
function cycleCurrency() {
	document.getElementById("currency").value = currencies[cur++ %% currencies.length]
}
