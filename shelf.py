import os
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask import Flask, request, redirect, url_for, render_template, flash, make_response, jsonify, send_file
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import (Security, LoginForm, login_required, roles_accepted, user_datastore)
from flask.ext.security.datastore.sqlalchemy import SQLAlchemyUserDatastore
from booksorting import *

# create application
app = Flask(__name__)
app.config.from_pyfile('settings.cfg')

# connect to database
db = SQLAlchemy(app)
Security(app, SQLAlchemyUserDatastore(db))


"""
MODELS
"""


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    call_number = db.Column(db.String(80))
    RFID_tag = db.Column(db.String(80))
    located = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return '<Book %r>' % self.call_number

"""
LOGIC
"""


@app.before_request
def before_request():
    pass


@app.after_request
def shutdown_session(response):
    db.session.remove()
    return response


@app.route('/')
def show_entries():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    books = Book.query.filter_by(located=True).all()
    lost_books = Book.query.filter_by(located=False).all()
    return render_template('show_entries.html', books=books, lost=lost_books)


@app.route('/new', methods=['POST'])
def new_item():
    if not session.get('logged_in'):
        abort(401)
    new = request.form['call_number']
    new = new.upper()
    new = new.replace(" .", " ")
    new = new.replace(".", " ")
    new = new.strip()
    x = BookCheck()
    cleaned = x.just_split_call_number(new)
    joined = ' '.join(cleaned)
    newtag = request.form['tag']
    book = Book(call_number=new, RFID_tag=newtag, located=True)
    db.session.add(book)
    db.session.commit()
    flash(new + ' was inserted into the database.')
    return redirect(url_for('add_item'))


@app.route('/add')
def add_item():
    if not session.get('logged_in'):
        abort(401)
    return render_template('new_book.html')


@app.route('/edit/<int:book_id>')
def edit_item(book_id):
    book = Book.query.filter_by(id=book_id).first()
    return render_template('edit_book.html', book=book)


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
        status = True
    else:
        status = False
    book = Book.query.filter_by(id=no).first()
    book.call_number = edit
    book.RFID_tag = tag
    book.located = status
    db.session.commit()
    flash('%s was successfully updated.' % joined)
    return redirect(url_for('show_entries'))


@app.route('/delete', methods=['POST'])
def delete_item():
    if not session.get('logged_in'):
        abort(401)
    no = request.form['no']
    book = Book.query.filter_by(id=no).first()
    flash('Book %s was successfully deleted.' % book.call_number)
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for('show_entries'))


@app.route('/startscan')
def start_scan():
    return render_template('scan_books.html')


@app.route('/scan', methods=['POST'])
def scan_books():
    ordered_library_calls = []
    if not session.get('logged_in'):
        abort(401)

    list_of_tags = request.form['tags']

    sanitized_list = list_of_tags.split('\r\n')

    # to find books for order
    result = Book.query.all()
    library_calls = Book.query.all()
    all_books = library_calls[:]

    # to find the IDs of books
    calls_with_ids = {book.id : book.call_number for book in library_calls}

    next_list = [book.call_number for book in library_calls]
    bs = BookCheck()
    split_library_calls = bs.split_arrange(next_list)
    ordered_library_calls = bs.sort_table(split_library_calls, (0, 1, 2, 3))

    x = BookCheck()
    scanned_books = [Book.query.filter_by(RFID_tag=tag).first() for tag in sanitized_list]

    sorted_scanned_books = x.split_arrange([book.call_number for book in scanned_books if book != None])
    to_test = sorted_scanned_books[:]
    copy = sorted_scanned_books[:]
    ordered = x.final_order(to_test, ordered_library_calls)
    seconded = x.compare_order(copy)

    #Find missing books
    list_to_compare = bs.new_lib_slice(copy, ordered_library_calls)
    missing_books = bs.find_missing(list_to_compare, to_test)
    boo = []
    lost_books = []
    for book in missing_books:
        for part in book:
            boo.append(part)
            boo.append(' ')
        lost_books.append(book)

    # Determine found books vs. lost books
    cleaned_lost = bs.clean_up_call_numbers(lost_books)
    found_books = [x for x in sorted_scanned_books if x not in lost_books]
    cleaned_found = bs.clean_up_call_numbers(found_books)
    last_found_list = [bs.find_id_from_call(book, calls_with_ids) for book in cleaned_found]
    last_lost_list = [bs.find_id_from_call(book, calls_with_ids) for book in cleaned_lost]

    #TRYING TO CHANGE TABLE TO UPDATE 'MISSING' OR 'FOUND' BOOKS
    for book in last_lost_list:
        book = Book.query.filter_by(id=book).first()
        book.located = False

    for book in last_found_list:
        book = Book.query.filter_by(id=book).first()
        try:
            book.located = True
        except Exception:
            print str(book)
    db.session.commit()

    super_cleaned = [dict(call_number=row[0].replace(' 0', ' '), status=row[1]) for row in seconded]
    duper_cleaned = [dict(call_number=(' '.join(row[0])).replace(' 0', ' '), statusleft=row[1], statusright=row[2]) for row in ordered]
    return render_template('after_scan.html', books=duper_cleaned, positioned=super_cleaned, missing=cleaned_lost)


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
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
    # app.run()