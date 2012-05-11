import re
import operator


class BookCheck(object):

    def __init__(self, outside_book_list=None):
        if outside_book_list is None:
            self.test_ideal_tags = []  # bind list with a new, empty list
        else:
            self.test_ideal_tags = outside_book_list  # bind list with provided list

        self.order_list = []
        self.gapped_list = []

    def call_number_split(self, call_number_list):
        for index, call_number in enumerate(call_number_list):
            a = re.findall(r'\w+', call_number)
            call_number_list[index] = a
        return call_number_list

    def rearrange_call_number(self, call_list):
        for index, call_number in enumerate(call_list):
            if call_number[0] is 'u':
                del call_number[0]
            # if len(call_number) is 5:
            if len(call_number) is 4:
                call_number.insert(1, '0')
            if len(call_number) is 3:
                call_number.insert(1, '0')
                call_number.insert(2, '0')
        return call_list

    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def sort_table(self, table, cols):
        """ sort a table by multiple columns
            table: a list of lists (or tuple of tuples) where each inner list
                represents a row
            cols:  a list (or tuple) specifying the column numbers to sort by
                e.g. (1,0) would sort by column 1, then by column 0
        """
        for col in reversed(cols):
            table = sorted(table, key=operator.itemgetter(col))
        return table

    def split_arrange(self, call_number_list):
        g = self.call_number_split(call_number_list)
        self.rearrange_call_number(g)
        return g

    def compare_order(self, booklist):
        correct_list = []
        misplaced_list = []
        last_book = 0
        last_last_book = 0
        order_list = []
        moved_list = []
        rehabilitated_list = []

        for index, book in enumerate(booklist):
            # print 'correct: ', correct_list
            # print 'wrong: ', misplaced_list
            # print 'Moved back from correct: ', moved_list
            # print 'Looking at: ', book, '>', last_book, '?'
            # print 'rehabilitated: ', rehabilitated_list
            # print "Gapped list: ", self.gapped_list
            # print '__________'

            if self.order(book, last_book):
                correct_list.append(book)
                #if the last book is below this one, make the last book correct
                if self.gapped_list:
                    print 'is ', book, '>', self.gapped_list[-1]
                    if self.order(book, self.gapped_list[-1]):
                        hh = self.gapped_list[-1]
                        print "yay!",  hh, "saved!"
                        rehabilitated_list.append(hh)
                        #?rehabilitated_list.append(last_last_book)
                        self.gapped_list.remove(hh)
                    # if self.order(book, last_last_book, last_book):
                    #     rehabilitated_list.append(last_last_book)
                    #     print "WYAYAYAYAYA"
                last_last_book = last_book
                last_book = book
            elif self.shelf_gap(book, correct_list, order_list):
                if self.order(last_book, book):
                    self.gapped_list.append(book)
                    print 'Found a gap for', self.gapped_list
                    incorrectly_filed = correct_list.pop()
                    misplaced_list.append(incorrectly_filed)
                    moved_list.append(incorrectly_filed)
                misplaced_list.append(book)
                last_last_book = last_book
                if correct_list:
                    last_book = correct_list[-1]  # SHOULD BE 'Last TRUE Book'
                #print last_book, book
            else:
                print "Error!"
        #print "misplaced list: ", misplaced_list
        #print "correct: ", correct_list

        newest_list = booklist[:]
        for index, book in enumerate(newest_list):
            order_list.append(self.final_order(book, misplaced_list, correct_list, rehabilitated_list))
            newest_list[index] = self.final_order(book, misplaced_list, correct_list, rehabilitated_list)

        return order_list

    #Determine whether a book is in the right place
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
    def final_order(self, book, wrong_list, correct_list, rehabilitated_list):

        if book in correct_list:
            return [' '.join(book), 'correct']
        elif book in rehabilitated_list:
            return ' '.join(book), 'rehabilitated'
        elif book in self.gapped_list:
            return ' '.join(book), 'gapped'
        elif book in wrong_list:
            return ' '.join(book), 'misplaced'
        else:
            return ' '.join(book), 'BAD'

    def find_missing(self, library_slice, scan_slice):
        lost_list = []
        for book in library_slice:
            if book not in scan_slice:
                lost_list.append(book)
        return lost_list

    # Determine if a book would fit earlier in the bookshelf
    def shelf_gap(self, misplaced_book, earlier_books, ordered_books):
        for index, earlier_book in enumerate(earlier_books):
            if misplaced_book <= earlier_book:
                return True
            else:
                continue

    def new_lib_slice(self, scanned_list, library_list):

        first_scanned = scanned_list[0]
        last_scanned = scanned_list[-1]
        start = self.scan_spot_find(first_scanned, library_list)
        end = self.scan_spot_find(last_scanned, library_list)
        #print start, end
        right_set = library_list[start:end]
        return right_set

    def scan_spot_find(self, scanned, library_list):
        for key, book in enumerate(library_list):
            if scanned == book:
                return key

    def find_call_from_tag(self, tag, call_number_dict):
        for index, book in call_number_dict.items():
            if tag == index:
                return book


scanned_books = ['AA240 B142 2000', 'AB240.B14.C22 1976', 'AB101.B14.K12 1976',
'AB10.B14.K12 1976', 'CK364 .H876 .G52 1946']

correct_books = ['AA240 B142 1999', 'AA240 B142 2000', 'AA240.B14323 1956', 'AB10.B14.K12 1976',
'AB101.B14.K12 1976', 'AB240.7.B14 C22 1976', 'CK364.54 .G52 1946', 'J4375 .H876 .G52 1946',
'JR437 .K6 .I52 1995']

u = BookCheck()

h = u.split_arrange(correct_books)

i = u.split_arrange(scanned_books)
#print h

#list_to_compare not working... Or, it works but doesn't work right. Needs to include last book.
list_to_compare = u.new_lib_slice(i, h)
#print "Scanned: ", scanned_books
# fake_list = [2, 3, 4, 5, 70, 60, 6, 10, 9, 13, 11, 12, 14, 15, 16, 50, 510, 17]

fake_list2 = [1, 2, 3, 4, 10, 5, 6, 70, 71, 72, 7, 8, 9, 11, 12, 13, 14]

#print u.compare_order(fake_list2)
