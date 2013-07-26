class TransactionError(Exception):
    pass

class Transaction:
    """a class to encapsulate SQL-transaction-like behaviour for python
    function calls. Especially useful for large complex objects whose methods
    have side effects; like modifying lists, dicts, numpy arrays and networkx
    Graphs."""
    def __init__(self, first_arg=None):
        """if first_arg is passed, it adds this object as the first argument to
        every call in the queue. If None or False, it is ignored."""
        self.oself = first_arg
        self.queue = []
        self.committed = False
    
    def push(self, function, arguments):
        """add another function call to the transaction. function should be
        callable, and arguments should be a list of non-keyword arguments."""
        if self.oself:
            arguments = [self.oself] + arguments
        self.queue.append({'function' : function, 'arguments' : arguments})
    
    def commit(self):
        """run all the queue'd function calls. It is a TransactionError to call
        this method twice."""
        if self.committed:
            raise TransactionError('transaction instance already committed.')
        
        self.committed = True
        for qi in self.queue:
            qi['function'](*qi['arguments'])

