%include header_template title="Know Thy Shelf"

<p>Scan books to check if they're out of place, or lost:</p>
<form action="/scan" method="GET">
<textarea type="text" name="tags"></textarea>
<input type="submit" name="save" value="Scan!">
</form>
<p><a href="/books">Back</a></p>
