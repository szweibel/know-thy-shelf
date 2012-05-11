%include header_template title="Know Thy Shelf"

<p>
<ul class="bookshelf">
%for book in books:
        %da = book[0].replace(' 0', ' ')
    <dt class="{{book[1]}}">{{da}}</dt>

%end
</ul>
</p>
<p>Key:</p>
<p>Green: Correct</p>
<p>Red: Misplaced</p>
<p>Blue?: Weirdness</p>
<p>Purple?: More Weirdness, Likely Correct</p>
<div>---------------------</div>
<p>MISSING: <p>
%for book in missing:
    %ka = ' '.join(book)
    %fa = ka.replace(' 0', ' ')
    <p class="missing">{{fa}}</p>
%end

