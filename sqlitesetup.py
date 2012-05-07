import sqlite3
con = sqlite3.connect('tada.db')  # Warning: This file is created in the current directory
con.execute("CREATE TABLE tada (id INTEGER PRIMARY KEY, call_number char(50) NOT NULL, isbn char(30), tag char(40) NOT NULL, status bool NOT NULL)")
con.execute("INSERT INTO tada (call_number, isbn, tag, status) VALUES ('AB240 B142 1999', '978-0375434525', '9346w3q',0)")
con.execute("INSERT INTO tada (call_number, isbn, tag, status) VALUES ('AA240 B143 2000', '978-0743497466', '7833wf', 1)")
con.execute("INSERT INTO tada (call_number, isbn, tag, status) VALUES ('AA240.B14323 J40 1956', '978-0312944926', '3gwe7yb', 1)")
con.execute("INSERT INTO tada (call_number, isbn, tag, status) VALUES ('CK364.H876 .G52 1946','0307454541', 'f2653dd',0)")
con.commit()
