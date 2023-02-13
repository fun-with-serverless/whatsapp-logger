HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/spin.js/2.3.2/spin.min.js"></script>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
    <title>Basic Authentication</title>
  </head>
  <body>
    <div class="container">
      <div id="login-form" class="form-group">
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

      <div id="config-form" style="display: none;">
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
            <input type="button" value="Show QR" class="btn btn-info" onclick="showQR()">
          </div>
        </form>
      </div>
      <div id="spinner-container" style="display: none;"></div>
      <div id="image-container" class="text-center"></div>
    </div>
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
                document.getElementById("config-form").style.display = 'block';
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
