HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/spin.js/2.3.2/spin.min.js"></script>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
    <script src="https://code.jquery.com/jquery-3.6.3.min.js" integrity="sha256-pvPw+upLPUjgMXY0G+8O0xUf+/Im1MZjXxxgOcBQBXU=" crossorigin="anonymous"></script>
    <title>Basic Authentication</title>
  </head>
  <body>
    <div id="spinner-container"  style="display: none;"></div>
    <div class="container">
      <div id="login-form" class="form-group" style="display: block;">
        <form>
          <div class="form-group">
            <label for="username">Username:</label>
            <input type="text" id="username" name="username" class="form-control">
          </div>
          <div class="form-group">
            <label for="password">Password:</label>
            <input type="password" id="password" name="password" class="form-control">
          </div>
          <input type="button" value="Submit" class="btn btn-primary" onclick="submitForm()">
        </form>
      </div>
      <div id="tabs" style="display: none;">
        <ul class="nav nav-tabs">
          <li class="nav-item">
            <a class="nav-link active" href="#google-sheets-config" data-toggle="tab">Google Configuration</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="#whatsapp-agent-status" data-toggle="tab">WhatsApp Client Status</a>
          </li>
        </ul>
        <div class="tab-content">
          <div id="google-sheets-config" class="tab-pane active">
            <form>
              <div class="form-group">
                <label for="google_secret">Google Secret:</label>
                <textarea id="google_secret" name="google_secret" class="form-control" style="height: 10em"></textarea>
              </div>
              <div class="form-group">
                <label for="sheet_url">Sheet URL:</label>
                <input type="text" id="sheet_url" name="sheet_url" class="form-control">
              </div>
              <div class="form-group">
                <input type="button" value="Save" class="btn btn-success" onclick="saveConfig()">
              </div>
            </form>
          </div>
          <div id="whatsapp-agent-status" class="tab-pane">
            <h3 class="text-center font-weight-bold" id="agent_status">NA</h3>
            <input type="button" id="disconnect" value="Disconnect" class="btn btn-info" onclick="disconnect()">
            <div id="image-container" class="text-center"></div>
          </div>
        </div>
      </div>
    </div>
    <script>
      var spinner = new Spinner({
        color: '#3d3d3d',
        length:0, left:'1%',top:'1%', scale:0.5
      }).spin(document.getElementById("spinner-container"));

      function showLoading() {
        $("#spinner-container").show();
      }

      function hideLoading() {
        $("#spinner-container").hide();
      }
      async function getRequest({verb, url, responseType = "json", headers = {}, body = null}) {
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
          xhr.onload = function() {
            if (xhr.status === 200) {
              resolve(xhr.response);
            } else {
              reject(Error(xhr.statusText));
            }
          };
          xhr.onerror = function() {
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
          var response = await getRequest({verb: "GET", url: "https://" + window.location.hostname + "/configuration"});
          $("#login-form").hide();
          $("#tabs").show();
          $("#google_secret").val(response.google_secret);
          $("#sheet_url").val(response.sheet_url);
          pullDeviceStatus();
        } catch (error) {
          console.log(error.message)
          alert("Authentication failed. Please check your username and password.");
        }
        hideLoading();
      }
      async function saveConfig() {
        showLoading();
        try {
          await getRequest({verb:"POST", url:"https://" + window.location.hostname + "/configuration", headers:{"Content-Type": "application/json"},body: JSON.stringify({
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
          var response = await getRequest({verb: "GET", url: "https://" + window.location.hostname + "/qr-code", responseType: "blob"});
          hideLoading();
          var img = $("<img>");
          img.attr("src", URL.createObjectURL(response));
          $("#image-container").html(img);
        } catch (error) {
          console.log(error.message)
          alert("Error in loading the QR code. Please check your username and password.");
        }
      }
      async function pullDeviceStatus() {
        showLoading();
        try {
          const response = await getRequest({verb: "GET",url: "https://" + window.location.hostname + "/device-status"});
          $("#agent_status").html(response.device_status);
          if (response.device_status === "Disconnected") {
            await showQR();
            $("#disconnect").hide();
            $("#image-container").show();
          } else {
            $("#disconnect").show();
            $("#image-container").hide();
          }
        } catch (error) {
          console.log(error.message)
        }
        hideLoading();
        setTimeout(pullDeviceStatus, 5000);
      }
      async function disconnect() {
        showLoading();
        try {
          await getRequest({verb:"POST", url:"https://" + window.location.hostname + "/disconnect", headers:{"Content-Type": "application/json"},body: JSON.stringify({})})
        } catch (error) {
          console.log(error.message)
          alert("Failed disconnecting");
        }
        hideLoading();
        
      }
      $(document).ready(function() {
        $('.nav-link').click(function() {
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
    </script>
  </body>
</html>

"""
