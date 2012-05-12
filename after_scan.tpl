%include header_template title="Know Thy Shelf"

<p>
<ul class="bookshelf">
%for book in books:
    %sa = ' '.join(book[0])
    %call_number = sa.replace(' 0', ' ')
    <dt class="left{{book[1]}}">{{call_number}}</dt>
    <dt class="right{{book[2]}}"></dt>

%end
</ul>
</p>
<p>Key:</p>
<p>Green: Correct</p>
<p>Red: Misplaced</p>
<div>---------------------</div>

