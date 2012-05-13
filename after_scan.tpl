%include header_template title="Know Thy Shelf"
<div class="row">
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
</div>
<div>---------------------</div>
<div class="row">
<ul class="bookshelf">
%for book in secondary:
        %da = book[0].replace(' 0', ' ')
    <dt class="{{book[1]}}">{{da}}</dt>

%end
</ul>
<p>Key:</p>
<p>Green: Correct</p>
<p>Red: Misplaced</p>
<p>Blue: Weirdness</p>
<p>Purple: Likely Correct</p>
</div>
<div>---------------------</div>
<div class="row">
<p>MISSING:</p>
<ul>
%for call_number in missing:
    %ba = ' '.join(call_number)
    %clean = ba.replace(' 0',' ')
    <dt class="missing">{{clean}}</dt>
%end
</ul>
</div>