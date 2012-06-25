import os
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import sqlite3
from booksorting import *

# create application
app = Flask(__name__)
app.config.from_pyfile('settings.cfg')


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


# def init_db():
#     with closing(connect_db()) as db:
#         with app.open_resource('schema.sql') as f:
#             db.cursor().executescript(f.read())
#         db.commit()


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    g.db.close()


@app.route('/')
def show_entries():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    cur = g.db.execute("SELECT id, tag, call_number FROM tada WHERE status = 1")
    lost = g.db.execute("SELECT id, tag, call_number FROM tada WHERE status = 0")
    books = [dict(id=row[0], tag=row[1], call_number=row[2]) for row in cur.fetchall()]
    lost_books = [dict(id=row[0], tag=row[1], call_number=row[2]) for row in lost.fetchall()]
    return render_template('show_entries.html', books=books, lost=lost_books)


# @app.route('/view/')
# @app.route('/view/<int:id>')
# def show_entry(id=0):
#     cur = g.db.execute('select title, content, date from entries where id = ?', (id,))
#     _entry = cur.fetchone()
#     if not _entry:
#         flash('Entry could not be found')
#         return redirect(url_for('show_entries'))
#     entry = dict(title=_entry[0], content=_entry[1], date=_entry[2])
#     return render_template('show_entry.html', entry=entry)


@app.route('/new', methods=['POST'])
def new_item():
    if not session.get('logged_in'):
        abort(401)
    new = request.form['call_number']
    x = BookCheck()
    cleaned = x.just_split_call_number(new)
    joined = ' '.join(cleaned)
    newtag = request.form['tag']
    g.db.execute("INSERT INTO tada (call_number,tag,status) VALUES (?,?,?)", (joined, newtag, 1))
    g.db.commit()
    flash('The new book was inserted into the database.')
    return redirect(url_for('add_item'))


@app.route('/add')
def add_item():
    if not session.get('logged_in'):
        abort(401)
    return render_template('new_book.html')


@app.route('/edit/<int:book_id>')
def edit_item(book_id):
    no = book_id
    bookget = g.db.execute("SELECT call_number, tag, status FROM tada WHERE id = ?", [(str(no))])
    book = [dict(call_number=row[0], tag=row[1], status=row[2]) for row in bookget.fetchall()]
    return render_template('edit_book.html', book=book, no=no)


@app.route('/change', methods=['POST'])
def change_item():
    if not session.get('logged_in'):
        abort(401)
    no = request.form['no']
    edit = request.form['call_number']
    tag = request.form['tag']
    status = request.form['status']

    x = BookCheck()
    cleaned = x.just_split_call_number(edit)
    joined = ' '.join(cleaned)
    if status == 'found':
        status = 1
    else:
        status = 0

    g.db.execute("UPDATE tada SET call_number = ?, tag = ?, status = ? WHERE id LIKE ?", (joined, tag, status, no))
    g.db.commit()
    flash('%s was successfully updated.' % joined)
    return redirect(url_for('show_entries'))


@app.route('/delete', methods=['POST'])
def delete_item():
    if not session.get('logged_in'):
        abort(401)
    no = request.form['no']
    g.db.execute("DELETE FROM tada WHERE id LIKE ?", [(str(no))])
    g.db.commit()
    flash('The item number %s was successfully deleted.' % no)
    return redirect(url_for('show_entries'))


@app.route('/startscan')
def start_scan():
    return render_template('scan_books.html')


@app.route('/scan', methods=['POST'])
def scan_books():
    next_list = []
    ordered_library_calls = []
    if not session.get('logged_in'):
        abort(401)

    list_of_tags = request.form['tags']

    sanitized_list = list_of_tags.split('\r\n')

    # to find books for order
    gotten = g.db.execute("SELECT tag, call_number FROM tada")
    result = dict(gotten)

    # to find books for missing
    library_calls = g.db.execute("SELECT call_number FROM tada")
    # library_calls = [dict(call_number=row[0]) for row in library_calls.fetchall()]
    library_calls = [row for row in library_calls.fetchall()]
    all_books = library_calls[:]

    # to find the IDs of books
    calls = g.db.execute("SELECT id, call_number FROM tada")
    calls_with_ids = dict(calls)
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
    for book in last_lost_list:
        g.db.execute("UPDATE tada SET status = 0 WHERE id LIKE ?", (book,))
    g.db.commit()

    for bookf in cleaned_found:
        g.db.execute("UPDATE tada SET status = 1 WHERE call_number = ?", (bookf,))
    g.db.commit()

    super_cleaned = [dict(call_number=row[0].replace(' 0', ' '), status=row[1]) for row in seconded]
    duper_cleaned = [dict(call_number=(' '.join(row[0])).replace(' 0', ' '), statusleft=row[1], statusright=row[2]) for row in ordered]
    return render_template('after_scan.html', books=duper_cleaned, positioned=super_cleaned, missing=bla)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

#Development
# if __name__ == '__main__':
#     app.run()

#Deployment
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
