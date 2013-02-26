import os
import callnumber
from collections import OrderedDict
from flask import Flask, request, session, redirect, url_for, abort, render_template, flash, make_response
from flask.ext.sqlalchemy import SQLAlchemy
# from flask.ext.security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required
from booksorting import BookCheck
import requests


# create application
app = Flask(__name__)
app.config.from_pyfile('settings.cfg')

# connect to database
db = SQLAlchemy(app)

"""
MODELS
"""


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    call_number = db.Column(db.String(80))
    normalized_call_number = db.Column(db.String(80))
    doc_number = db.Column(db.String(80))
    RFID_tag = db.Column(db.String(80))
    located = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(80))
    collection_id = db.Column(db.Integer, db.ForeignKey('lib_collection.id'))

    def __repr__(self):
        return '<Book %r>' % self.call_number


class Lib_collection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    books = db.relationship('Book', backref='lib_collection')

    def __repr__(self):
        return '<Library %r>' % self.name

"""
LOGIC
"""


def lookup_doc(doc_number):
    payload = {'docNumber': doc_number}
    r = requests.get('http://mighty-wildwood-7308.herokuapp.com/details', params=payload)
    JSON_record = r.json()
    return JSON_record


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
    current_library_id = request.values.get('library_id') or 1
    current_library = Lib_collection.query.filter_by(id=current_library_id).first() or Lib_collection.query.first()
    books = Book.query.filter_by(located=True).filter_by(lib_collection=current_library).all()
    lost_books = Book.query.filter_by(located=False).filter_by(lib_collection=current_library).all()
    return render_template('show_entries.html', books=books, lost=lost_books)


@app.route('/new', methods=['POST'])
def new_item():
    if not session.get('logged_in'):
        abort(401)

    default = Lib_collection.query.first()
    current_library_id = request.cookies.get('library_id') or default.id
    current_library = Lib_collection.query.filter_by(id=current_library_id).first()

    new_book = request.form['call_number']
    fixed_book = new_book.replace(u"\u00A0", " ")
    lccn = callnumber.LC(fixed_book)
    stored_book = lccn.denormalized
    normalized_call = lccn.normalized
    newtag = request.form['tag']
    title = request.form['title']
    doc_number = request.form['doc_number']
    book = Book(call_number=stored_book, normalized_call_number=normalized_call, RFID_tag=newtag, doc_number=doc_number, title=title, located=True)
    current_library.books.append(book)
    db.session.commit()
    flash(stored_book + ' was inserted into the database.')
    return redirect(url_for('add_item'))


@app.route('/newcollection', methods=['POST'])
def new_collection():
    if not session.get('logged_in'):
        abort(401)
    new_collection = request.form['collection']
    newest_collection = Lib_collection(name=new_collection)
    db.session.add(newest_collection)
    db.session.commit()
    flash(new_collection + ' was created as a new collection.')
    the_library_id = request.cookies.get('library_id')
    return redirect(url_for('show_entries', library_id=the_library_id))


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
    edited_book = request.form['call_number']
    tag = request.form['tag']
    status = request.form['status']
    lccn = callnumber.LC(edited_book)
    edited_book = lccn.denormalized
    if status == 'found':
        status = True
    else:
        status = False
    book = Book.query.filter_by(id=no).first()
    book.call_number = edited_book
    book.normalized_call_number = lccn.normalized
    book.RFID_tag = tag
    book.located = status
    db.session.commit()
    the_library_id = request.cookies.get('library_id')
    flash('%s was successfully updated.' % lccn.denormalized)
    return redirect(url_for('show_entries', library_id=the_library_id))


@app.route('/delete', methods=['POST'])
def delete_item():
    if not session.get('logged_in'):
        abort(401)
    no = request.form['no']
    book = Book.query.filter_by(id=no).first()
    flash('Book %s was successfully deleted.' % book.call_number)
    db.session.delete(book)
    db.session.commit()
    the_library_id = request.cookies.get('library_id')
    return redirect(url_for('show_entries', library_id=the_library_id))


@app.route('/deletecollection', methods=['POST'])
def delete_collection():
    if not session.get('logged_in'):
        abort(401)
    no = request.form['library_id_del']
    library = Lib_collection.query.filter_by(id=no).first()
    flash('Collection %s was successfully deleted.' % library.name)
    db.session.delete(library)
    db.session.commit()
    the_library_id = request.cookies.get('library_id')
    return redirect(url_for('show_entries', library_id=the_library_id))


@app.route('/startscan')
def start_scan():
    return render_template('scan_books.html')


@app.route('/scan', methods=['POST'])
def scan_books():
    ordered_library_calls = []
    if not session.get('logged_in'):
        abort(401)

    default = Lib_collection.query.first()
    current_library_id = request.cookies.get('library_id') or default.id
    current_library = Lib_collection.query.filter_by(id=current_library_id).first()
    list_of_tags = request.form['tags']

    # Clean up list of scanned books, remove duplicates
    sanitized_tags = list(OrderedDict.fromkeys(list_of_tags.split('\r\n')))
    x = BookCheck()
    scanned_books = [Book.query.filter_by(RFID_tag=tag).filter_by(lib_collection=current_library).first() for tag in sanitized_tags]
    sorted_scanned_books = [book.normalized_call_number for book in scanned_books if book != None]
    print sorted_scanned_books, '!!!!!!!!'

    # to find and order the books in the library
    library_calls = Book.query.filter_by(lib_collection=current_library).all()
    calls_with_ids = {}
    for book in library_calls:
        calls_with_ids[int(book.id)] = book.normalized_call_number
    ordered_library_calls = [book.normalized_call_number for book in library_calls]
    ordered_library_calls.sort()
    ordered = x.final_order(sorted_scanned_books, ordered_library_calls)
    seconded = x.NEW_ORDER(sorted_scanned_books)

    #Find missing books
    list_to_compare = x.lib_slice(sorted_scanned_books, ordered_library_calls)
    missing_books = [book for book in list_to_compare if book not in sorted_scanned_books]
    # Determine found books vs. lost books
    found_books = [book for book in sorted_scanned_books if book not in missing_books]
    last_found_list = [book for book in library_calls if book.normalized_call_number in found_books]
    last_lost_list = [book for book in library_calls if book.normalized_call_number in missing_books]
    #UPDATE 'MISSING' OR 'FOUND' BOOKS
    for book in last_lost_list:
        book_record = lookup_doc(book.doc_number)
        print book_record
        book.located = False
    for book in last_found_list:
        try:
            book.located = True
        except Exception:
            print str(book)
    db.session.commit()

    for classed_book in seconded:
        for item in library_calls:
            if classed_book[0] == item.normalized_call_number:
                classed_book[0] = item.call_number
                print item.doc_number
                classed_book.append(item.doc_number or None)
    for book in ordered:
        for item in library_calls:
            if book[0] == item.normalized_call_number:
                book[0] = item.call_number
                book.append(item.doc_number or None)
    cleaned_positioned = [dict(call_number=row[0], status=row[1], doc_number=row[2]) for row in seconded]
    cleaned_absolute = [dict(call_number=row[0], statusleft=row[1], statusright=row[2], doc_number=row[3]) for row in ordered]
    return render_template('after_scan.html', books=cleaned_absolute, positioned=cleaned_positioned, missing=last_lost_list)


@app.context_processor
def get_library():
    default = Lib_collection.query.first()
    the_library = request.cookies.get('library_id') or default.id
    our_library = Lib_collection.query.filter_by(id=the_library).first()
    if not our_library:
        our_library = default
    libraries = Lib_collection.query.all()
    return dict(the_library=our_library, libraries=libraries)


# Change the Cookie that sets which library is being used
@app.route('/change_library', methods=['POST'])
def change_library_cookie():
    which_library_id = request.form['which_library_id']
    which_library = Lib_collection.query.filter_by(id=which_library_id).first()
    output = redirect(url_for('show_entries', library_id=which_library_id))
    output = make_response(output)
    output.set_cookie('library_name', which_library.name)
    output.set_cookie('library_id', which_library.id)
    return output


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


#Deployment
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 4999))
    app.run(host='0.0.0.0', port=port)
    # app.run()
