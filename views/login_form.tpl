<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
  <head>
    <meta content="text/html; charset=utf-8" http-equiv="content-type">
    <link rel="shortcut icon" type="image/png" href="static/favicon.ico" />
  </head>
  <body>
    <img src="static/softfire.jpg" alt="SoftFIRE" align="middle" class="heightSet">
    <div id="box">
      <div class="box">
        <h2>Login</h2>
        <p>Please insert your credentials:</p>
        <form action="login" method="post" name="login">
          <table class="centerTable">
            <tr>
              <td><label class="loginLabel">Username: </label></td>
              <td><input type="text" name="username" /> </td>
            </tr>
            <tr>
              <td><label class="loginLabel">Password: </label></td>
              <td><input type="password" name="password" /></td>
            </tr>
          </table>
          <br/><br/>
          <button type="submit"> OK </button>
          <button type="button" class="close"> Cancel </button>
        </form>
        <br />
      </div>
    </div>
    <div id="box" >
      <div id='status' align="center" class="divMiddle">Ready...</div>
    </div>
    <div id="box">
      <br />
      <!--
      <div class="box">
        <h2>Signup</h2>
        <p>Please insert your credentials:</p>
        <form action="register" method="post" name="signup">
          <table class="centerTable">
            <tr>
              <td><label class="loginLabel">Username: </label></td>
              <td><input type="text" name="username" /></td>
            </tr>
            <tr>
              <td><label class="loginLabel">Password: </label></td>
              <td><input type="password" name="password" /></td>
            </tr>
            <tr>
              <td><label class="loginLabel">Email: </label></td>
              <td><input type="text" name="email_address" /></td>
            </tr>
          </table>
          <br/><br/>
          <button type="submit"> OK </button>
          <button type="button" class="close"> Cancel </button>
        </form>
        <br />
      </div>
    -->
      <!--
        <div class="box">
            <h2>Password reset</h2>
            <p>Please insert your credentials:</p>
            <form action="reset_password" method="post" name="password_reset">
                <input type="text" name="username" value="username"/>
                <input type="text" name="email_address" value="email address"/>

                <br/><br/>
                <button type="submit" > OK </button>
                <button type="button" class="close"> Cancel </button>
            </form>
            <br />
        </div>
        -->
      <br style="clear: left;" />
    </div>
    <!-- Bootstrap Core CSS
      <link href="static/bootstrap.min.css" rel="stylesheet">
      -->
    <!-- Custom CSS -->
    <!--
      <link href="static/simple-sidebar.css" rel="stylesheet">
      -->
    <style>

    div#status {
        border: 1px solid #999;
        padding: .5em;
        margin: 2em;
        width: 15em;
        -moz-border-radius: 10px;
        border-radius: 10px;
        font-size: medium;
        align: middle;
    }

      img {
      display: block;
      margin: 0 auto;
      horizontal-align: middle;
      }
      div#hbox {width: 100%;}
      div#hbox div.box {float: left; width: 33%;}
      input {
      background: #f8f8f8;
      border: 1px solid #777;
      margin: auto;
      }
      input:hover { background: #fefefe}
      h2 {
      font-size: xx-large;
      color: #111;
      }
      div {
      color: #777;
      font-size: x-large;
      margin: auto;
      width: 20em;
      text-align: center;
      }
      .clear { clear: both;}
      .centerTable { margin: 0px auto; }
      .divMiddle {
        width: 50%;
        margin: 0 auto;
      }
      .loginLabel {
      font-size: large;
      }
      .heightSet {
      max-height: 300px;
      }
    </style>

    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>
    <script>
        // Prevent form submission, send POST asynchronously and parse returned JSON
        $("div#status").delay(2800).fadeOut(700);
        $('form').submit(function() {
            $("div#status").fadeIn(100);
            z = $(this);
            $.post($(this).attr('action'), $(this).serialize(), function(j){
              console.log('here')
              console.log(j)
              console.log('j: ' + j)
              if (j.ok) {
                $("div#status").css("background-color", "#f0fff0");
                $("div#status").text('Ok.');
                window.location = j.redirect;
              } else {
                $("div#status").css("background-color", "#fff0f0");
                $("div#status").text(j.msg);
              }
              $("div#status").delay(1800).fadeOut(700);
            }, "json");
            return false;
        });
    </script>
  </body>
</html>
