<p>Add a new book to the list:</p>
%get(flash)
%if flash:
    <p>{{flash}}</p>
%end
<form action="/new" method="GET">
<p>Call Number:<input type="text" size="100" maxlength="100" name="call_number"></br>
RFID tag:<input type="text" size="100" maxlength="100" name="tag"></p>
<input type="submit" name="save" value="save">
</form>
<p><a href="/books">Back</a></p>
