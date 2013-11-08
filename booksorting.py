import callnumber

class BookCheck(object):

    def __init__(self, outside_book_list=None):
        if outside_book_list is None:
            self.test_ideal_tags = []  # bind list with a new, empty list
        else:
            self.test_ideal_tags = outside_book_list  # bind list with provided list

        self.order_list = []
        self.gapped_list = []

    def find_left_partner(self, book, full_list):
        if book != full_list[0]:
            try:
                x = full_list.index(book) - 1
                return full_list[x]
            except IndexError:
                return '00000000'
        else:
            return '00000000'

    def find_right_partner(self, book, full_list):
        try:
            x = full_list.index(book) + 1
            return full_list[x]
        except IndexError:
            return 'ZZZZZZZZZZZ'

    def find_both_partners(self, book, full_list):
        left_partner = self.find_left_partner(book, full_list)
        right_partner = self.find_right_partner(book, full_list)
        return left_partner, right_partner

    def compare_left_order(self, book, scan_list, full_list):
        ideal_partner = self.find_left_partner(book, full_list)
        print "FOR BOOK: ", book
        print "Ideal left: ", ideal_partner
        scanned_partner = self.find_left_partner(book, scan_list)
        print "scanned left: ", scanned_partner
        if ideal_partner == scanned_partner:
            return True
        else:
            return False

    def compare_right_order(self, book, scan_list, full_list):
        ideal_partner = self.find_right_partner(book, full_list)
        print "Ideal right: ", ideal_partner
        scanned_partner = self.find_right_partner(book, scan_list)
        print "scanned right: ", scanned_partner
        if ideal_partner == scanned_partner:
            return True
        else:
            return False

    def compare_left_and_right(self, book, scan_list, full_list):
        a = self.compare_left_order(book, scan_list, full_list)
        b = self.compare_right_order(book, scan_list, full_list)
        return [book, a, b]

    # Create a list by comparing neighbor books
    def final_order(self, scan_list, full_list):
        out = []
        for book in scan_list:
            out.append(self.compare_left_and_right(book, scan_list, full_list))
        return out

    # Determine whether a book is in the right place
    def order(self, x, y, z=None):
        if not z:
            if x >= y:
                return True
            else:
                return False
        else:
            if x >= y and y >= z:
                return True
            else:
                return False

    # Place labels on the final list of books, and remove empty columns, to show call number order
    def dynamic_final_order(self, book, wrong_list, correct_list, rehabilitated_list):
        if book in correct_list:
            return [book, 'correct']
        elif book in rehabilitated_list:
            return [book, 'rehabilitated']
        elif book in self.gapped_list:
            return [book, 'gapped']
        elif book in wrong_list:
            return [book, 'misplaced']
        else:
            return [book, 'BAD']

    # Determine if a book would fit earlier in the bookshelf
    def shelf_gap(self, misplaced_book, earlier_books):
        for index, earlier_book in enumerate(earlier_books):
            if misplaced_book <= earlier_book:
                return True
            else:
                continue

    # Get the part of the library appropriate to compare to the scanned list
    def lib_slice(self, scanned_list, library_list):
        first_scanned = scanned_list[0]
        last_scanned = scanned_list[-1]
        start = self.scan_spot_find(first_scanned, library_list)
        end = self.scan_spot_find(last_scanned, library_list)
        right_set = library_list[start:end]
        return right_set

    # Get the index, in the full list, of a scanned book
    def scan_spot_find(self, scanned, library_list):
        for key, book in enumerate(library_list):
            if scanned == book:
                return key

    def find_id_from_call(self, call_number, id_dict):
        for index, book in id_dict.items():
            if call_number == book:
                return index

    # Main function to determine 'relative' order
    def NEW_ORDER(self, booklist, first_book_error=None):
        correct_list = []
        misplaced_list = []
        last_book = 0
        last_last_book = 0
        order_list = []
        moved_list = []
        rehabilitated_list = []

        for index, book in enumerate(booklist):
            print 'correct: ', correct_list
            print 'wrong: ', misplaced_list
            print 'Moved back from correct: ', moved_list
            print 'Looking at: ', book, '>', last_book, '?'
            print 'rehabilitated: ', rehabilitated_list
            print "Gapped list: ", self.gapped_list
            print '__________'
            if book == first_book_error:
                misplaced_list.append(first_book_error)
            if self.order(book, last_book):
                correct_list.append(book)
                #if the last book is below this one, make the last book correct
                if self.gapped_list:
                    print 'is ', book, '>', self.gapped_list[-1], 'and is', book, '<', correct_list[0]
                    if self.order(book, self.gapped_list[-1]) and self.order(correct_list[0], book) :
                        hh = self.gapped_list[-1]
                        print hh, "saved!"
                        rehabilitated_list.append(hh)
                        self.gapped_list.remove(hh)
                    if self.order(book, last_last_book, last_book):
                        rehabilitated_list.append(last_last_book)
                        print "WYAYAYAYAYA"
                last_last_book = last_book
                last_book = book
            elif self.shelf_gap(book, correct_list):
                if self.order(last_book, book): # Add: if last_book left partner not correct
                    self.gapped_list.append(book)
                    print 'Found a gap for', self.gapped_list
                    incorrectly_filed = correct_list.pop()
                    misplaced_list.append(incorrectly_filed)
                    moved_list.append(incorrectly_filed)
                misplaced_list.append(book)
                last_last_book = last_book
                if correct_list:
                    last_book = correct_list[-1]  # SHOULD BE 'Last TRUE Book'
            else:
                print "Error!" + str(book)
                print booklist[0]
                first_book_error = booklist[0]
        #print "misplaced list: ", misplaced_list
        #print "correct: ", correct_list

        newest_list = booklist[:]
        for index, book in enumerate(newest_list):
            order_list.append(self.dynamic_final_order(book, misplaced_list, correct_list, rehabilitated_list))
            newest_list[index] = self.dynamic_final_order(book, misplaced_list, correct_list, rehabilitated_list)

        return order_list

id_dict = {"2": "AA240 B142 2000", "3": 'AA240 B142 1999', "9": "TR765 7 G23 I71 1896", "10": "HN657 N76 1982", "12": "CK364 H876 G52 1946",
"13": "AC875 L65 1956", "14": "Z99 U10 T49 1949", "15": "AA240 G22 2012"}

scanned_books = ['BF173 J7253', 'HM 621 N2 v13', 'HM 621 N2 v11', 'PE1408 S772 2005', 'PR6015 O7885 R68 2007', 'QA93 G69 2002',
'QK118 B66 2012', 'TJ181 B87 2005',]

correct_books = ['BF173 J7253', 'HM 621 N2 v11', 'HM 621 N2 v13', 'PE1408 S772 2005', 'PR6015 O7885 R68 2007',
'QA93 G69 2002', 'QK118 B66 2012', 'TJ181 B87 2005']

# u = BookCheck()
# for book in scanned_books:
#     loc = scanned_books.index(book)
#     book = callnumber.LC(book)
#     book = book.normalized
#     scanned_books[loc] = book

# for book in correct_books:
#     loc = correct_books.index(book)
#     book = callnumber.LC(book)
#     book = book.normalized
#     correct_books[loc] = book

# print u.final_order(scanned_books, correct_books)

# #list_to_compare = u.new_lib_slice(hh, h)

# print u.compare_order(scanned_books)
