import tran
import unittest
import random

class SuccessError(Exception):
    pass

class FailureError(Exception):
    pass

def dummy_function(a, b):
    raise SuccessError('values: a=' + repr(a) + ' and b=' + repr(b))

def dummy_function_with_kwargs(a, b, c='foo'):
    e = SuccessError('values a=' + repr(a) + ' and b=' + repr(b))
    e.c = c
    raise e

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


class TestDataObject:
    def my_func(self):
        raise SuccessError()
    def my_other_func(self):
        raise FailureError()

class TestWithFirstArg(unittest.TestCase):
    def setUp(self):
        self.valid_tran = tran.Transaction(TestDataObject())
        # push functions into the queue:
        self.valid_tran.push(TestDataObject.my_func, [])
        
        self.invalid_tran = tran.Transaction()
        self.invalid_tran.push(TestDataObject.my_func, [])

    def test_unbound_failure(self):
        with self.assertRaises(TypeError):
            self.invalid_tran.commit()

    def test_commit(self):
        # running commit on the tran should run my_func, which should
        # raise a SuccessError:
        with self.assertRaises(SuccessError):
            self.valid_tran.commit()

class TestWithEmptyObject(unittest.TestCase):
    def setUp(self):
        self.my_empty_list = []
        self.tran = tran.Transaction(self.my_empty_list)
        
        self.tran.push(self.my_empty_list.__class__.append, [5])
    
    def test_commit(self):
        self.tran.commit()
        self.assertEqual(len(self.my_empty_list), 1)

class TestWithKwArgs(unittest.TestCase):
    def setUp(self):
        self.tran = tran.Transaction()

        self.val = random.random()
        # push functions into the queue:
        self.tran.push(dummy_function_with_kwargs, [1, 2], {'c' : self.val})

    def test_commit(self):
        try:
            self.tran.commit()
        except SuccessError as e:
            self.assertEqual(e.c, self.val)


if __name__ == '__main__':
    unittest.main()