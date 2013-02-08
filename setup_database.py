from shelf import *
import callnumber

ctx = app.test_request_context('/?next=http://example.com/')
ctx.push()
# Kill everything and recreate tables
db.drop_all()
db.create_all()

book_list = ['BF173 J7253', 'HM 621 N2 v11', 'HM 621 N2 v13', 'PE1408 S772 2005', 'PR6015 O7885 R68 2007',
'QA93 G69 2002', 'QK118 B66 2012', 'TJ181 B87 2005']
i = 0

new_collection = Lib_collection(name='test')
db.session.add(new_collection)
another_new_collection = Lib_collection(name='rando')
db.session.add(another_new_collection)
db.session.commit()

for book in book_list:
    i += 1
    lccn = callnumber.LC(book)
    denormalized_lccn = lccn.denormalized
    book = Book(RFID_tag=i, call_number=denormalized_lccn, normalized_call_number=lccn.normalized)
    new_collection.books.append(book)
db.session.commit()
