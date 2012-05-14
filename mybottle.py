import sqlite3
from bottle import route, run, debug, template, request, validate, static_file  # response
from booksorting import *


@route('/static/:path#.+#', name='static')
def static(path):
    return static_file(path, root='static')


@route('/books')
def book_list():
    conn = sqlite3.connect('tada.db')
    c = conn.cursor()
    c.execute("SELECT id, tag, call_number FROM tada WHERE status = 1")
    result = c.fetchall()
    c.close()

    d = conn.cursor()
    d.execute("SELECT id, tag, call_number FROM tada WHERE status = 0")
    lost = d.fetchall()
    d.close()

    output = template('book_table', rows=result, lost=lost)
    return output


@route('/new', method='GET')
def new_item():
    if request.GET.get('save', '').strip():
        new = request.GET.get('call_number', '').strip()
        x = BookCheck()
        cleaned = x.just_split_call_number(new)
        joined = ' '.join(cleaned)
        newtag = request.GET.get('tag', '').strip()
        conn = sqlite3.connect('tada.db')
        c = conn.cursor()
        c.execute("INSERT INTO tada (call_number,tag,status) VALUES (?,?,?)", (joined, newtag, 1))
        conn.commit()
        c.close()
        flash = 'The new book was inserted into the database. <a href="/new">Add another</a>'
        return template('new_book.tpl', flash=flash)
    else:
        return template('new_book.tpl', flash=None)


@route('/edit/:no', method='GET')
@validate(no=int)
def edit_item(no):
    num = no
    if request.GET.get('delete', '').strip():
        request.GET.get('no', '').strip()
        conn = sqlite3.connect('tada.db')
        c = conn.cursor()
        c.execute("DELETE FROM tada WHERE id LIKE ?", [(str(no))])
        conn.commit()
        return '<p>The item number %s was successfully deleted. <a href="/books">Home</a></p>' % no

    elif request.GET.get('save', '').strip():
        edit = request.GET.get('call_number', '').strip()
        x = BookCheck()
        cleaned = x.just_split_call_number(edit)
        joined = ' '.join(cleaned)
        tag = request.GET.get('tag', '').strip()
        status = request.GET.get('status', '').strip()

        if status == 'found':
            status = 1
        else:
            status = 0

        conn = sqlite3.connect('tada.db')
        c = conn.cursor()
        c.execute("UPDATE tada SET call_number = ?, tag = ?, status = ? WHERE id LIKE ?", (joined, tag, status, no))
        conn.commit()
        return '<p>The item number %s was successfully updated. <a href="/books">Home</a></p>' % no
    else:
        conn = sqlite3.connect('tada.db')
        c = conn.cursor()
        c.execute("SELECT call_number FROM tada WHERE id LIKE ?", [(str(num))])
        cur_data = c.fetchone()
        c.close()

        d = conn.cursor()
        d.execute("SELECT tag FROM tada WHERE id = ?", [(str(num))])
        cur_data_tag = d.fetchone()
        d.close()

        r = conn.cursor()
        r.execute("SELECT status FROM tada WHERE id = ?", [(str(num))])
        cur_data_status = r.fetchone()
        r.close()

        return template('edit_book', old=cur_data, oldtag=cur_data_tag, oldstat=cur_data_status, no=no)


# @route('/forum')
# def display_forum():
#     forum_id = request.query.id
#     page = request.query.page or '1'
#     return 'Forum ID: %s (page %s)' % (forum_id, page)


@route('/scan', method='GET')
def scan_books():

    next_list = []
    ordered_library_calls = []
    if request.GET.get('save', '').strip():
        list_of_tags = request.GET.get('tags', '').strip()

        sanitized_list = list_of_tags.split('\r\n')

        # to find books for order
        conn = sqlite3.connect('tada.db')
        c = conn.cursor()
        c.execute("SELECT tag, call_number FROM tada")
        result = dict(c.fetchall())
        c.close()

        # to find books for missing
        d = conn.cursor()
        d.execute("SELECT call_number FROM tada")
        library_calls = d.fetchall()
        all_books = library_calls[:]
        d.close()

        # to find the IDs of books
        l = conn.cursor()
        l.execute("SELECT id, call_number FROM tada")
        calls_with_ids = dict(l.fetchall())
        l.close()
        #return calls_with_ids

        #Find order of books
        for book in library_calls:
            next_list.append(str(book))
        bs = BookCheck()
        split_library_calls = bs.split_arrange(next_list)
        ordered_library_calls = bs.sort_table(split_library_calls, (0, 1, 2, 3))
        x = BookCheck()
        out = [x.find_call_from_tag(tag, result) for tag in sanitized_list]
        new_list = []
        for book in out:
            new_list.append(str(book))
        sorted_scanned_books = x.split_arrange(new_list)
        to_test = sorted_scanned_books[:]
        copy = sorted_scanned_books[:]
        ordered = x.final_order(to_test, ordered_library_calls)
        seconded = x.compare_order(copy)

        #Find missing books
        list_to_compare = bs.new_lib_slice(copy, ordered_library_calls)
        missing_books = bs.find_missing(list_to_compare, to_test)
        boo = []
        bla = []
        for book in missing_books:
            for part in book:
                boo.append(part)
                boo.append(' ')
            bla.append(book)

        # Determine found books vs. lost books
        lost_books = bla[:]
        found_books = [x for x in sorted_scanned_books if x not in lost_books]
        cleaned_lost = bs.clean_up_call_numbers(lost_books)
        cleaned_found = bs.clean_up_call_numbers(found_books)
        last_lost_list = []
        for book in cleaned_lost:
            j = bs.find_id_from_call(book, calls_with_ids)
            last_lost_list.append(str(j))

        #TRYING TO CHANGE TABLE TO UPDATE 'MISSING' OR 'FOUND' BOOKS
        conn = sqlite3.connect('tada.db')
        r = conn.cursor()
        for book in last_lost_list:
            r.execute("UPDATE tada SET status = 0 WHERE id LIKE ?", (book,))
        conn.commit()

        conn = sqlite3.connect('tada.db')
        g = conn.cursor()
        for bookf in cleaned_found:
            g.execute("UPDATE tada SET status = 1 WHERE call_number = ?", (bookf,))
        conn.commit()

        return template('after_scan', books=ordered, secondary=seconded, missing=bla)
    else:
        return template('scan_books')


#add this at the very end:
debug(True)
run(reloader=True)
