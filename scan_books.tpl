%include header_template title="Know Thy Shelf"

<p>Scan books to check if they're out of place, or lost:</p>
<form action="/scan" method="GET">
<!-- <p>RFID tag:<input type="text" name="INPUT" size="30" maxlength="40" name="tag1"></br>
<p>RFID tag:<input type="text" size="30" maxlength="40" name="tag2"></br>
<p>RFID tag:<input type="text" size="30" maxlength="40" name="tag3"></br>
<p>RFID tag:<input type="text" size="30" maxlength="40" name="tag4"></br>
<p>RFID tag:<input type="text" size="30" maxlength="40" name="tag5"></br>
<p>RFID tag:<input type="text" size="30" maxlength="40" name="tag6"></br> -->
<textarea type="text" name="tags"></textarea>
<input type="submit" name="save" value="save">
</form>
<p><a href="/books">Back</a></p>
