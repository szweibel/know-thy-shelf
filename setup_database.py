from shelf import *

ctx = app.test_request_context('/?next=http://example.com/')
ctx.push()
# Kill everything and recreate tables
db.drop_all()
db.create_all()

book = Book(RFID_tag='1', call_number='AB240 B142 1999')
book2 = Book(RFID_tag='2', call_number='AA240 B143 2000')
book3 = Book(RFID_tag='3', call_number='AA240 B14323 J40 1956')
book4 = Book(RFID_tag='4', call_number='CK364 H876 G52 1946')

db.session.add(book)
db.session.add(book2)
db.session.add(book3)
db.session.add(book4)

db.session.commit()
