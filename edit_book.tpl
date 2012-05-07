
%include header_template title="Know Thy Shelf"

<p>Edit the book with ID = {{no}}</p>

<form action="/edit/{{no}}" method="get">
<input type="hidden" name="{{no}}" value="{{no}}">
<input type="text" name="call_number" value="{{old[0]}}" size="100" maxlength="100">
<input type="text" name="tag" value="{{oldtag[0]}}" size="100" maxlength="100">

<select name="status">
<option>found</option>
<option>lost</option>
</select>
<br/>
<input type="submit" name="save" value="save">
<input type="submit" name="delete" value="delete">
</form>
