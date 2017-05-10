<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>

<head>
    <meta content="text/html; charset=utf-8" http-equiv="content-type">
    <link rel="shortcut icon" type="image/png" href="static/favicon.ico" />
</head>

<body>
    <img src="static/softfire.jpg" alt="SoftFIRE" align="middle" class="heightSet">
    <h1>Experimenter Page</h1>
    <table class="main">
        <tr>
            <th id="main">
                <h2>Available Resources</h2>
            </th>
            <th id="main">
                <h2>Reserve Resources</h2>
            </th>
            <th id="main">
                <h2>Delete Resources</h2>
            </th>
        </tr>
        <tr>
            <td>
                <div>
                    <p>Welcome {{current_user.username}}, access time: {{current_user.session_accessed_time}}</p>
                    <div id='commands'>
                        <p>List Resources:</p>
                        <form action="list_resources" method="get">
                            <table class="innerTable">
                                <tr>
                                    <th>Id</th>
                                    <th>Name</th>
                                    <th>Description</th>
                                </tr>
                                %for r in resources:
                                <tr>
                                    <td>{{r['id']}}</td>
                                    <td>{{r['name']}}</td>
                                    <td>{{r['description']}}</td>
                                </tr>
                                %end
                            </table>
                            <p> To refresh the list, refresh the page.</p>
                        </form>
                    </div>
            </td>
            <td>
                <div>
                    <form action="/reserve_resources" method="post" enctype="multipart/form-data">
                        <p>
                            Select a file to upload<br />
                            <input type="file" name="data" />
                        </p>
                        <button type="submit"> Send </button>
                    </form>
                </div>
            </td>
            <td>
                <div>
                    <form action="delete_resources" method="post">
                        <p><label>resource id: </label><br /> <input type="text" name="resource_id" /></p>
                        <button type="submit"> OK </button>
                    </form>
                </div>
            </td>
        </tr>
    </table>

    <div class="clear"></div>

    <div id='status'>Ready...</div>
    <div id="urls">
        <a href="/logout">logout</a>
    </div>

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
    </div>
    <style>
        h1 {
          color: #111;
          font-family: 'Helvetica Neue', sans-serif;
          font-size: xx-large;
          font-weight: bold;
          letter-spacing: -1px;
          line-height: 1;
          text-align: center;
        }
        img {
          display: block;
          margin: 0 auto;
          horizontal-align: middle;
        }
        div#commands {
          width: 100%;
          float: left;
        }
        div#users {
          width: 45%;
          float: right
        }
        div#main {
          color: #777;
          margin: auto;
          font-size: medium;
          margin: auto;
          width: 20em;
          text-align: left;
          vertical-align: top;
        }
        input {
          background: #f8f8f8;
          border: 1px solid #777;
          margin: auto;
        }
        input:hover {
          background: #fefefe
        }
        label {
          width: 8em;
          float: left;
          text-align: right;
          margin-right: 0.5em;
          display: block
        }
        button {
            margin-left: 13em;
        }
        button.close {
            margin-left: .1em;
        }
        div#status {
            border: 1px solid #999;
            padding: .5em;
            margin: 2em;
            width: 15em;
            left: 40%;
            position: fixed;
            -moz-border-radius: 10px;
            border-radius: 10px;
        }
        .clear { clear: both;}
        div#urls {
          position:absolute;
          top:0;
          right:1em;
          font-size: large;
          box-shadow: inset 0 1px 1px darkgray, 0 0 8px darkgray;
          padding: 3px 3px 3px 3px;

        }
        .main {
            border-collapse: collapse;
            width: 80%;
            margin: 0px auto;
            background-color: #f2f2f2;
            border: 1px solid #ddd;
        }

        .innerTable {
          border-collapse: collapse;
          width: 100%;
          margin: 0px auto;
          border: 1px solid #ddd;
        }

        table, td, th {
            border: 1px solid #ddd;
            text-align: left;
        }

        th, td {
            text-align: left;
            padding: 8px;
        }

        th#main {
            background-color: darkorange;
            color: black;
        }
        tr:nth-child(even){background-color: #f2f2f2}
    </style>
</body>

</html>
