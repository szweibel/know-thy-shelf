%include header_template title="Know Thy Shelf"

<p>
%for book in books:
|
   %for part in book:
    <tr>
        <td>{{part}}</td>
    </tr>
    %end
%end
</p>
<p>Key:</p>
<p>O: Correct</p>
<p>M: Misplaced</p>
<p>?: Weirdness</p>