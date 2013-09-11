tran
====

SQL Transactions (sort of) for Python (queue up operations and either abort or commit.)

**class Transaction**
a class to encapsulate SQL-transaction-like behaviour for python function calls. Especially useful for large complex objects whose methods have side effects; like modifying lists, dicts, numpy arrays and networkx Graphs.

Installation
------------
You can run the (very small) test suite with

    python test_tran.py

And install with

    python setup.py install --user

Or, for a system-wide install, the two-step:

    python setup.py build
    sudo python setup.py install

Simple example:
---------------

    import tran
    t = tran.Transaction()
    my_list = range(5)
    t.push(list.append, [my_list, "foo"])
    my_list
      Out: [0, 1, 2, 3, 4]
    t.commit()
    my_list
      Out: [0, 1, 2, 3, 4, 'foo']

Object-centric example:
-----------------------

    import tran
    my_dict = {4 : "four"}
    t = tran.Transaction(my_dict)
    t.push(dict.__setitem__, [5, "five"])
    my_dict
      Out: {4 : 'four'}
    t.commit()
    my_dict
      Out: {4: 'four', 5: 'five'}


note what happens if you accidentally try to commit twice:

    t.commit()
      ErrOut: tran.TransactionError: transaction instance already committed.

To cancel a transaction, simply don't ever call the commit method. The class will *not* call it for you if unresolved when garbage collection occurs; just rebind the name or let it go out of scope.

Networkx example:
-----------------

*tip:* use `Instance.__class__` to access unbound methods, so that you definitely get the correct type (`nx.Graph` vs `nx.DiGraph` ...)

    import tran, networkx as nx
    G = nx.DiGraph()
    t = tran.Transaction(G)
    t.push(G.__class__.add_cycle, [range(5)])
    G.nodes()
      Out: []
    G.edges()
      Out: []
    
    t.commit()
    G.nodes()
      Out: [0, 1, 2, 3, 4]
    G.edges()
      Out: [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]

Bound and unbound methods:
--------------------------

It does seem simpler to just use the bound methods:

    import tran, networkx as nx
    G = nx.DiGraph()
    
    # NOTE: no constructor argument this time:
    t = tran.Transaction()
    
    # Then lift the bound method directly from the object:
    t.push(G.add_cycle, [range(5)])
    G.nodes()
      Out: []
    G.edges()
      Out: []

    t.commit()
    G.nodes()
      Out: [0, 1, 2, 3, 4]
    G.edges()
      Out: [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]

Or if you're going to mix changes to a bunch of objects in one transaction.

However, by knowing a little of the implementation, you can do clever things like hot-swap the instance you want to `.commit()` on:

    import tran
    my_dict = {4 : "four"}
    t = tran.Transaction(my_dict)
    t.push(dict.__setitem__, [5, "five"])
    
    # change my mind about which instance to apply the changes to:
    my_other_dict = {7 : "seven"}
    
    t.oself = my_other_dict
    t.commit()
    
    my_dict
      Out: {4 : 'four'}
    
    my_other_dict
      Out: {5: 'five', 7 : 'seven'}

*(note that in 0.1.1 and earlier, `oself` was added to the argument list on `push()`, so this would only affect new pushes. from 0.1.2, this now changes all instances, as the result is applied during the `commit()` call.)*

You can also undo the error throwing behaviour if you want to apply the same `Transaction` to multiple objects. Calling

    t.committed = False

will ensure that the transaction can have oself swapped and be called again without copying or duplicating it (although `copy.deepcopy` works fine on transactions.)
