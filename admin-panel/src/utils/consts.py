HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/spin.js/2.3.2/spin.min.js"></script>
  
  <title>Basic Authentication</title>
  <style>
    /* Add some general styles for the form */
    form {
      width: 500px;
      margin: 0 auto;
      padding: 10px;
      border: 1px solid gray;
      border-radius: 5px;
    }

    /* Add some styles for the form labels */
    label {
      font-size: 14px;
      font-weight: bold;
      margin-bottom: 5px;
    }

    /* Add some styles for the form inputs */
    input[type="text"], input[type="password"], textarea {
      width: 100%;
      padding: 12px 20px;
      margin: 8px 0;
      box-sizing: border-box;
      border: 1px solid gray;
      border-radius: 4px;
    }

    /* Add some styles for the submit button */
    input[type="button"] {
      width: 100%;
      background-color: #4CAF50;
      color: white;
      padding: 14px 20px;
      margin: 8px 0;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }
    /* Add some styles for the image container*/
    #image-container {
        padding: 10px;
        text-align: center;
    }
    /* Add some styles for the image*/
    #image-container img{
        width:33%;
    }
  </style>
</head>
<body>

<div id="login-form">
  <form>
    <label for="username">Username:</label>
    <input type="text" id="username" name="username"><br><br>
    <label for="password">Password:</label>
    <input type="password" id="password" name="password"><br><br>
    <input type="button" value="Submit" onclick="submitForm()">
  </form>
</div>

<div id="config-form" style="display: none;flex-direction: column">
  <form>
    <div style="display: flex; align-items: center; margin-bottom: 10px;">
    <label for="google_secret" style="width: 20%;">Google Secret:</label>
    <textarea id="google_secret" name="google_secret" style="width: 80%;"></textarea>
  </div>
  <div style="display: flex; align-items: center; margin-bottom: 10px;">
    <label for="sheet_url" style="width: 20%;">Sheet URL:</label>
    <input type="text" id="sheet_url" name="sheet_url" style="width: 80%;">
  </div>
  <div style="display: flex; flex-direction: column; margin-top: 10px;">
    <input type="button" value="Save" onclick="saveConfig()">
    <input type="button" value="Show QR" onclick="showQR()">
  </div>
  </form>
  
</div>
<div id="spinner-container" style="display: none;"></div>
<div id="image-container"></div>

<script>
  var spinner = new Spinner({color: '#3d3d3d'}).spin(document.getElementById("spinner-container"));
  
  function showLoading() {
    
    document.getElementById("spinner-container").style.display = "block";
  }

  function hideLoading() {
    document.getElementById("spinner-container").style.display = "none";
  }
  
    function getRequest(username, password, verb, url) {
        var xhr = new XMLHttpRequest();
        xhr.open(verb, url, true);
        xhr.setRequestHeader("Authorization", "Basic " + btoa(username + ":" + password));
        return xhr;
    }
  
    function submitForm() {
        showLoading()
        var username = document.getElementById("username").value;
        var password = document.getElementById("password").value;
        var xhr = getRequest(username, password, "GET", window.location.href + "configuration")
        xhr.responseType = "json";
        xhr.onload = function () {
            hideLoading()
            if (xhr.status === 200) {
                var response = xhr.response;
                document.getElementById("login-form").style.display = 'none';
                document.getElementById("config-form").style.display = 'flex';
                document.getElementById("google_secret").innerHTML = response.google_secret;
                document.getElementById("sheet_url").value = response.sheet_url;
            } else {
                alert("Authentication failed. Please check your username and password.");
            }
        }
        xhr.send();
    }
    
    function saveConfig() {
        showLoading()
        var xhr = getRequest(document.getElementById("username").value, document.getElementById("password").value, "POST", window.location.href + "configuration")
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onload = function () {
            hideLoading()
            if (xhr.status === 200) {
                alert("Config saved successfully");
            } else {
                alert("Failed to save config");
            }
        }
        xhr.send(JSON.stringify({
            google_secret: document.getElementById("google_secret").value,
            sheet_url: document.getElementById("sheet_url").value
        }));
    }
    
    function showQR() {
        showLoading()
        var xhr = getRequest(document.getElementById("username").value, document.getElementById("password").value, "GET", window.location.href + "qr-code")
        xhr.responseType = "blob";
        xhr.onload = function () {
          hideLoading()
          if (xhr.status === 200) {
              var blob = xhr.response;
              var img = document.createElement("img");
              img.src = URL.createObjectURL(blob);
              document.getElementById("image-container").innerHTML = '';
              document.getElementById("image-container").innerHTML = '<img src="' + img.src + '">';
              setTimeout(showQR, 10000);
          } else {
              alert("Error in loading the QR code. Please check your username and password.");
          }
        }
        xhr.send();
}

</script>

</body>
</html>

"""
