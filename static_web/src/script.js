const endPointURL = "$URL$"
var spinner = new Spinner({
    color: '#3d3d3d',
    length: 0,
    left: '1%',
    top: '1%',
    scale: 0.5
}).spin(document.getElementById("spinner-container"));

function showLoading() {
    $("#spinner-container").show();
}

function hideLoading() {
    $("#spinner-container").hide();
}
async function getRequest({
    verb,
    url,
    responseType = "json",
    headers = {},
    body = null
}) {
    return new Promise((resolve, reject) => {
        var username = $("#username").val();
        var password = $("#password").val();
        var xhr = new XMLHttpRequest();
        xhr.open(verb, url, true);
        xhr.setRequestHeader("Authorization", "Basic " + btoa(username + ":" + password));
        for (let key in headers) {
            xhr.setRequestHeader(key, headers[key]);
        }
        xhr.responseType = responseType;
        xhr.onload = function () {
            if (xhr.status === 200) {
                resolve(xhr.response);
            } else {
                reject(Error(xhr.statusText));
            }
        };
        xhr.onerror = function () {
            reject(Error("Network Error"));
        };
        if (body) {
            xhr.send(body);
        } else {
            xhr.send();
        }

    });
}
async function submitForm() {
    showLoading();
    try {
        var response = await getRequest({
            verb: "GET",
            url: endPointURL + "configuration"
        });
        $("#login-form").hide();
        $("#tabs").show();
        $("#google_secret").val(response.google_secret);
        $("#sheet_url").val(response.sheet_url);
        pullStatus();
    } catch (error) {
        console.log(error.message)
        alert("Authentication failed. Please check your username and password.");
    }
    hideLoading();
}
async function saveConfig() {
    showLoading();
    try {
        await getRequest({
            verb: "POST",
            url: endPointURL + "configuration",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                google_secret: $("#google_secret").val(),
                sheet_url: $("#sheet_url").val()
            })
        })
        alert("Config saved successfully");
    } catch (error) {
        console.log(error.message)
        alert("Failed to save config");
    }
    hideLoading();
}
async function showQR() {
    try {
        var response = await getRequest({
            verb: "GET",
            url: endPointURL + "qr-code",
            responseType: "blob"
        });
        hideLoading();
        var img = $("<img>");
        img.attr("src", URL.createObjectURL(response));
        $("#image-container").html(img);
    } catch (error) {
        console.log(error.message)
        alert("Error in loading the QR code. Please check your username and password.");
    }
}
async function pullStatus() {
    showLoading();
    try {
        const response = await getRequest({
            verb: "GET",
            url: endPointURL + "device-status"
        });
        $("#agent_status").html(response.device_status);
        if (response.device_status === "Disconnected") {
            await showQR();
            $("#disconnect").hide();
            $("#image-container").show();
        } else {
            $("#disconnect").show();
            $("#image-container").hide();
        }
        $("#last_message_arrived_value").html(new Date(response.last_message_arrived).toLocaleString())
        $("#total_messages_today_value").html(response.total_today)
    } catch (error) {
        console.log(error.message)
    }
    hideLoading();
    setTimeout(pullStatus, 5000);
}
async function disconnect() {
    showLoading();
    try {
        await getRequest({
            verb: "POST",
            url: endPointURL + "disconnect",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({})
        })
    } catch (error) {
        console.log(error.message)
        alert("Failed disconnecting");
    }
    hideLoading();

}
$(document).ready(function () {
    $('.nav-link').click(function () {
        // Remove the active class from all tabs
        $('.nav-link').removeClass('active');
        // Add the active class to the clicked tab
        $(this).addClass('active');
        // Get the id of the clicked tab
        var tabId = $(this).attr('href');
        // Hide all tab content
        $('.tab-pane').removeClass('active');
        // Show the content of the clicked tab
        $(tabId).addClass('active');
    });
});