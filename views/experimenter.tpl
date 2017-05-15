<!DOCTYPE HTML><!-- PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">-->
<html>

<head>
    <meta content="text/html; charset=utf-8" http-equiv="content-type">
    <link rel="shortcut icon" type="image/png" href="static/favicon.ico" />
</head>

<body>
    <img src="static/softfire.jpg" alt="SoftFIRE" align="middle" class="heightSet">
    <h1>Experimenter Page</h1>
    <h5>Welcome User {{current_user.username}}</h5>
    <table>
        <tr>
            <td>
                <table class="main">
                  <colgroup>
                     <col span="1" style="width: 70%;">
                     <col span="1" style="width: 30%;">
                  </colgroup>
                    <tr>
                        <th id="main">
                            <h2>Available Resources</h2>
                        </th>
                        <th id="main">
                            <h2>Reserve Resources</h2>
                        </th>
                    </tr>
                    <tr>
                        <td>
                            <br />
                                <div id='commands'>
                                    <form action="list_resources" method="get">
                                        <table class="listResTable" cellpadding="10px">
                                          <colgroup>
                                             <col span="1" style="width: 10%;">
                                             <col span="1" style="width: 10%;">
                                             <col span="1" style="width: 5%;">
                                             <col span="1" style="width: 30%;">
                                          </colgroup>
                                            <tr>
                                                <th>Resource Id</th>
                                                <th>NodeType</th>
                                                <th>Cardinality</th>
                                                <th>Description</th>
                                            </tr>
                                            %for r in resources:
                                            <tr>
                                                <td>{{r['resource_id']}}</td>
                                                <td>{{r['node_type']}}</td>
                                                <td>{{r['cardinality']}}</td>
                                                <td>{{r['description']}}</td>
                                            </tr>
                                            %end
                                        </table>
                                        <p> To refresh the list, refresh the page.</p>
                                    </form>
                                </div>
                        </td>
                        <td>
                          <br />

                                <form action="/reserve_resources" method="post" enctype="multipart/form-data">
                                  <table class="formUpload" cellpadding="10px">
                                    <tr class="formUpload">
                                      <td class="formUpload">Select a file to upload:</td>
                                    </tr>
                                    <tr class="formUpload">
                                      <td class="formUpload"><input type="file" name="data" /></td>
                                    </tr>
                                    <tr class="formUpload">
                                      <td class="formUpload"><button type="submit" style="float: left;"> Reserve </button></td>
                                    </tr>
                                    </table>
                                </form>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>

        <tr>
            <td style="padding: 10px; padding-bottom: 50px">
              <table class="formUpload" cellpadding="10px">
                <tr class="formUpload">
                  <td class="formUpload"><h2>Your experiment {{experiment_id}}</h2></td>
                  <td class="formUpload"><form action="delete_resources" method="post"><button type="submit" style="float: left;"> Delete </button></form></td>
                </tr>
                </table>


                <table class="experimentTable" cellpadding="10px">
                  <colgroup>
                     <col span="1" style="width: 20%;">
                     <col span="1" style="width: 10%;">
                     <col span="1" style="width: 70%;">
                  </colgroup>
                    <tr>
                        <th>Resource Id</th>
                        <th>Status</th>
                        <th>Value</th>
                    </tr>
                    %for er in experiment_resources:
                    <tr>
                        <td>{{er['name']}}</td>
                        <td>{{er['status']}}</td>
                        <td>{{er['value']}}</td>
                    </tr>
                    %end

                </table>
            </td>
        </tr>
    </table>

    <div class="clear"></div>

    <div id='status'>Ready...</div>
    <div id="urls">
        <a href="/logout">logout</a>
    </div>

    <script src="//ajax.googleapis.com/ajax/libs/dojo/1.10.4/dojo/dojo.js"
            data-dojo-config="async: true"></script>
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>
    <script>
        // Prevent form submission, send POST asynchronously and parse returned JSON
        $("div#status").delay(2800).fadeOut(700);
        $('form').submit(function() {
            $("div#status").fadeIn(100);
            z = $(this);
            $.post($(this).attr('action'), $(this).serialize(), function(j) {
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

    <style>
        h1 {
            color: #111;
            font-family: "Lucida Grande", "Lucida Sans Unicode", "Lucida Sans", Geneva, Verdana, sans-serif;
            font-size: 45pt;
            font-weight: bold;
            letter-spacing: -1px;
            line-height: 1;
            text-align: center;
        }
        h5 {
            color: #111;
            font-family: "Lucida Grande", "Lucida Sans Unicode", "Lucida Sans", Geneva, Verdana, sans-serif;
            font-size: 25pt;
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
            font-family: "Lucida Grande", "Lucida Sans Unicode", "Lucida Sans", Geneva, Verdana, sans-serif;
        }

        div#users {
            width: 45%;
            float: right
            font-family: "Lucida Grande", "Lucida Sans Unicode", "Lucida Sans", Geneva, Verdana, sans-serif;
        }

        div#main {
            color: #777;
            margin: auto;
            font-size: medium;
            margin: auto;
            width: 20em;
            text-align: left;
            vertical-align: top;
            font-family: "Lucida Grande", "Lucida Sans Unicode", "Lucida Sans", Geneva, Verdana, sans-serif;
        }

        input:hover {
            background: #fefefe
        }

        label {
            font-family: "Lucida Grande", "Lucida Sans Unicode", "Lucida Sans", Geneva, Verdana, sans-serif;
            width: 8em;
            float: left;
            text-align: right;
            margin-right: 0.5em;
            display: block
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
            font-family: "Lucida Grande", "Lucida Sans Unicode", "Lucida Sans", Geneva, Verdana, sans-serif;
        }

        div#urls {
            position: absolute;
            top: 0;
            right: 1em;
            font-size: large;
            box-shadow: inset 0 1px 1px darkgray, 0 0 8px darkgray;
            padding: 3px 3px 3px 3px;
            font-family: "Lucida Grande", "Lucida Sans Unicode", "Lucida Sans", Geneva, Verdana, sans-serif;
        }

        table {
            width: 90%;
            border: 1px solid #ddd;
            margin: 0px auto;
            font-family: "Lucida Grande", "Lucida Sans Unicode", "Lucida Sans", Geneva, Verdana, sans-serif;
        }

        td,
        th {
            border: 1px solid #ddd;
            font-family: "Lucida Grande", "Lucida Sans Unicode", "Lucida Sans", Geneva, Verdana, sans-serif;
        }

        td#formUpload,
        th#formUpload {
            border: 0;
        }

        th#main,
        td#main {
            padding: 8px;
        }

        th#main {
            background-color: darkorange;
            color: black;
        }

        tr#main:nth-child(even) {
            background-color: #f2f2f2
        }


        .clear {
            clear: both;
        }


        .main {
            border-collapse: collapse;
            width: 100%;
            text-align: left;
            background-color: #f2f2f2;
            border: 1px solid #ddd;
        }

        .experimentTable {
            border-collapse: collapse;
            width: 100%;
            border: 3px solid #ddd;

        }

        .formUpload {
          border-collapse: collapse;
          margin: 0px auto;
          border: 0px
        }

        .listResTable {
            border-collapse: collapse;
            width: 98%;
            margin: 0px auto;
            border: 1px solid #ddd;
            text-align: justify;
        }

    </style>
</body>

</html>
