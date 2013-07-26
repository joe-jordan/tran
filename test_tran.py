import tran
import unittest

class SuccessError(Exception):
    pass

def dummy_function(a, b):
    raise SuccessError('values: a=' + repr(a) + ' and b=' + repr(b))

class TestNoFirstArg(unittest.TestCase):
    def setUp(self):
        self.tran = tran.Transaction()
        # push functions into the queue:
        self.tran.push(dummy_function, [1, 2])

    def test_push(self):
        self.assertEqual(len(self.tran.queue), 1)

    def test_commit(self):
        # running commit on the tran should run dummy_function, which should
        # raise a SuccessError:
        with self.assertRaises(SuccessError):
            self.tran.commit()

class TestNoFirstArg2(unittest.TestCase):
    def setUp(self):
        self.tran = tran.Transaction()
        # push functions into the queue:
        self.tran.push(dummy_function, [1, 2])
    
    def test_commits_are_singular(self):
        with self.assertRaises(SuccessError):
            self.tran.commit()
        
        with self.assertRaises(tran.TransactionError):
            self.tran.commit()


class FailureError(Exception):
    pass

class TestDataObject:
    def my_func(self):
        raise SuccessError()
    def my_other_func(self):
        raise FailureError()

class TestWithFirstArg(unittest.TestCase):
    def setUp(self):
        self.tran = tran.Transaction(TestDataObject())
        # push functions into the queue:
        self.tran.push(TestDataObject.my_func, [])

    def test_argument_transfer(self):
        self.assertEqual(len(self.tran.queue[0]['arguments']), 1)

    def test_commit(self):
        # running commit on the tran should run dummy_function, which should
        # raise a SuccessError:
        with self.assertRaises(SuccessError):
            self.tran.commit()

if __name__ == '__main__':
    unittest.main()