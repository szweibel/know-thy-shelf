%include header_template title="Know Thy Shelf"


<p>Know Thy Shelf:</p>
<table border="1">
%for row in rows:
    %cols = list(row)
  <tr>
    <td><a href="/edit/{{cols[0]}}">{{cols[2]}}</td></a>
  </tr>
%end
</table>
<p><a href="/new">Add new book</a></p>
<p><a href="/scan">Scan bookshelves</a></p>

%include footer_template
