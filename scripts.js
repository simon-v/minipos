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

// Set tax rate for tax button
function setTaxRate(rate) {
	rate *= 1;
	document.getElementById("tax").title = rate + "%";
}

// Set currency sign on currency button
function setCurrencySign(sign) {
	document.getElementById("sign").value = sign;
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
