%include header_template title="Know Thy Shelf"


<p>Know Thy Shelf:</p>
<table border="1">
%for row in rows:
    %list1 = list(row)
  <tr>
    %for col in row:
    <td><a href="/edit/{{list1[0]}}">{{col}}</td></a>
    %#<td>{{col}}</td>
  %end
  </tr>
%end
</table>
<p><a href="/new">Add new book</a></p>
<p><a href="/scan">Scan bookshelves</a></p>

%include footer_template
