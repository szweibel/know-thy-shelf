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
    c.execute("SELECT id, call_number FROM tada")
    result = c.fetchall()
    c.close()
    output = template('book_table', rows=result)
    return output


@route('/new', method='GET')
def new_item():
    if request.GET.get('save', '').strip():
        new = request.GET.get('call_number', '').strip()
        newtag = request.GET.get('tag', '').strip()
        conn = sqlite3.connect('tada.db')
        c = conn.cursor()

        c.execute("INSERT INTO tada (call_number,tag,status) VALUES (?,?,?)", (new, newtag, 1))
        #new_id = c.lastrowid

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
        tag = request.GET.get('tag', '').strip()
        status = request.GET.get('status', '').strip()

        if status == 'found':
            status = 1
        else:
            status = 0

        conn = sqlite3.connect('tada.db')
        c = conn.cursor()
        c.execute("UPDATE tada SET call_number = ?, tag = ?, status = ? WHERE id LIKE ?", (edit, tag, status, no))
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

        return template('edit_book', old=cur_data, oldtag=cur_data_tag, no=no)


@route('/forum')
def display_forum():
    forum_id = request.query.id
    page = request.query.page or '1'
    return 'Forum ID: %s (page %s)' % (forum_id, page)


@route('/scan', method='GET')
def scan_books():
    test_list = []
    if request.GET.get('save', '').strip():
        list_of_tags = request.GET.get('tags', '').strip()
        
        sanitized_list = list_of_tags.split('\r\n')

        # conn = sqlite3.connect('tada.db')
        # c = conn.cursor()
        # c.execute("SELECT tag, call_number FROM tada")
        # result = dict(c.fetchall())
        # c.close()
        # for ident, book in enumerate(sanitized_list):
        #     for tag, value in result.items():
        #         if book in sanitized_list:
        #             sanitized_list[ident] = value
        # for tag, value in result.items():
        #     for ident, book in enumerate(sanitized_list):
        #         if not book in result:
        #             pass
        #             sanitized_list[ident] = value
        #             test_list.append(value)
        x = BookCheck()
        v = x.split_arrange(sanitized_list)
        send = x.compare_order(v)
        #return str(sanitized_list)
        return template('after_scan', books=send)
    else:
        return template('scan_books')


#add this at the very end:
debug(True)
run(reloader=True)
