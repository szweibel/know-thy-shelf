import re
import operator


class BookCheck(object):

    def __init__(self, outside_book_list=None):
        if outside_book_list is None:
            self.test_ideal_tags = []  # bind list with a new, empty list
        else:
            self.test_ideal_tags = outside_book_list  # bind list with provided list

        self.order_list = []

    def call_number_split(self, call_number_list):
        for index, call_number in enumerate(call_number_list):
            a = re.findall(r'\w+', call_number)
            call_number_list[index] = a
        return call_number_list

    def rearrange_call_number(self, call_list):
        for index, call_number in enumerate(call_list):
        # if len(call_number) is 4:
        #     call_number.insert(3, call_number.pop(2))
        #     a = join_call_number(call_number)
            if len(call_number) is 3:
                call_number.insert(2, 0)
        return call_list

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
        order_list = []

        for index, book in enumerate(booklist):
            #print correct_list
            if self.order(book, last_book):
                correct_list.append(book)
                last_book = book
            elif self.shelf_gap(book, correct_list, order_list):
                if self.order(last_book, book):
                    misplaced_list.append(correct_list.pop())
                misplaced_list.append(book)
                last_book = correct_list[-1]  # SHOULD BE 'Last TRUE Book'
                #print last_book, book
            else:
                print "Error!"

        print "misplaced list: ", misplaced_list
        print "correct: ", correct_list

        for index, book in enumerate(booklist):
            order_list.append(self.final_order(book, misplaced_list, correct_list))
            booklist[index] = self.final_order(book, misplaced_list, correct_list)

        return order_list

    #Determine whether a book is in the right place
    def order(self, x, y):
        if x >= y:
            return True
        else:
            return False

    def final_order(self, book, wrong_list, correct_list):
        if book in wrong_list:
            return 'M'
        elif book in correct_list:
            return 'O'
        else:
            return 'X'

    def shelf_gap(self, misplaced_book, earlier_books, ordered_books):
        for index, earlier_book in enumerate(earlier_books):
            if misplaced_book <= earlier_book:
                return True
            else:
                continue

    def library_slice(self, first_scanned, last_scanned, library_book):
        if library_book >= first_scanned and library_book <= last_scanned:
            return True
        else:
            return False


# scanned_books = ['AA240 B142 1999',  'AA240.B14323 1956', 'AA240 B142 2000', 'AB240.B14.C22 1976',
# 'AB101.B14.K12 1976', 'AB10.B14.K12 1976', 'JR364 .H876 .G52 1946', 'CK364 .H876 .G52 1946', 'R4364 .K6 .I52 1995']

# correct_books = (['AA240 B142 1999', 'AA240 B142 2000', 'AA240.B14323 1956', 'AB240.B14.C22 1976',
# 'AB10.B14.K12 1976', 'AB101.B14.K12 1976', 'CK364 .H876 .G52 1946', 'JR364 .H876 .G52 1946', 'R4364 .K6 .I52 1995'])

# x = BookCheck()

# v = x.split_arrange(correct_books)

# fake_library = [range(100)]

# fake_list = [2, 3, 4, 5, 70, 60, 6, 10, 9, 13, 11, 12, 14, 15, 16, 50, 120]
# #fake_bookshelf = fake_library[(

# #print 'Unordered: ', fake_list
# print x.compare_order(v)
