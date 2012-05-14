%include header_template title="Know Thy Shelf"


<div class="span3">
<p>Know Thy Shelf:</p>
<table border="1">
%for row in rows:
    %cols = list(row)
  <tr>
    <td><a href="/edit/{{cols[0]}}">{{cols[2]}}</td></a>
  </tr>
%end
</table>
</div>
<div class="span3">
<p>Lost:</p>
<table border="1">
%for part in lost:
    %colls = list(part)
  <tr>
    <td><a href="/edit/{{colls[0]}}">{{colls[2]}}</td></a>
  </tr>
%end
</table>
</div>
<div class="span2">
<p><a href="/new">Add new book</a></p>
<p><a href="/scan">Scan bookshelves</a></p>
</div>

%include footer_template
