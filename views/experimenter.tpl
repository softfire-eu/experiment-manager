<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta content="text/html; charset=utf-8" http-equiv="content-type">
<div id='main'>
    <h2>Experimenter page</h2>
    <p>Welcome {{current_user.username}},
    access time: {{current_user.session_accessed_time}}</p>
    <div id='commands'>
      <p>List Resources:</p>
      <form action="list_resources" method="get">
        <table>
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
      <br />

      <p>Reserve Resources:</p>
      <form action="/reserve_resources" method="post" enctype="multipart/form-data">
        <label> Select a file to upload</label>
        <input type="file" name="data" />
        <br />
        <button type="submit" > Send </button>
      </form>
      <br />
      <p>Delete Resources:</p>
      <form action="delete_resources" method="post">
            <p><label>resource id: </label> <input type="text" name="resource_id" /></p>
          <button type="submit" > OK </button>
      </form>

    <div class="clear"></div>

    <div id='status'><p>Ready.</p></div>
    <div id="urls">
      <a href="/">index</a> <a href="/logout">logout</a>
    </div>


    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>
    <script>
        // Prevent form submission, send POST asynchronously and parse returned JSON
        $('form').submit(function() {
            $("div#status").fadeIn(100);
            z = $(this);
            $.post($(this).attr('action'), $(this).serialize(), function(j){
              if (j.ok) {
                $("div#status").css("background-color", "#f0fff0");
                $("div#status p").text('Ok.');
              } else {
                $("div#status").css("background-color", "#fff0f0");
                $("div#status p").text(j.msg);
              }
              $("div#status").delay(800).fadeOut(500);
            }, "json");
            return false;
        });
    </script>
</div>
<style>
div#commands { width: 45%%; float: left}
div#users { width: 45%; float: right}
div#main {
    color: #777;
    margin: auto;
    margin-left: 5em;
    font-size: 80%;
}
input {
    background: #f8f8f8;
    border: 1px solid #777;
    margin: auto;
}
input:hover { background: #fefefe}
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
    -moz-border-radius: 10px;
    border-radius: 10px;
}
.clear { clear: both;}
div#urls {
  position:absolute;
  top:0;
  right:1em;
}
</style>

