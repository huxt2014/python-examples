
import sys
import random
import timeit
import unittest

from tree import BinaryTree


def random_insert_ascii(tree):
    d = {}
    for i in range(255*10):
        c = random.randint(0, 255)
        tree[c] = chr(c)
        d[c] = c

    tree[ord("a")] = "a"
    tree[ord("b")] = "b"
    tree[ord("c")] = "c"

    d[ord("a")] = ord("a")
    d[ord("b")] = ord("b")
    d[ord("c")] = ord("c")

    return d


def insert_integer(tree, data):
    for i in data:
        tree[i] = i


class TestBinaryTree(unittest.TestCase):

    tree_cls = BinaryTree

    def test_dealloc(self):
        ref_a = sys.getrefcount("a")
        ref_b = sys.getrefcount("b")
        ref_c = sys.getrefcount("c")

        def dealloc_after_error(method, error, *args):
            tree = self.tree_cls()
            random_insert_ascii(tree)
            if method is not None:
                with self.assertRaises(error):
                    getattr(tree, method)(args)
            del tree

            self.assertTrue(ref_a == sys.getrefcount("a"), (method, ref_a, sys.getrefcount("a")))
            self.assertTrue(ref_b == sys.getrefcount("b"), (method, ref_b, sys.getrefcount("b")))
            self.assertTrue(ref_c == sys.getrefcount("c"), (method, ref_c, sys.getrefcount("c")))

        def only_one_element():
            tree = self.tree_cls()
            tree[ord("a")] = "a"
            tree.pop(ord("a"))
            del tree

            self.assertTrue(ref_a == sys.getrefcount("a"), (ref_a, sys.getrefcount("a")))
            self.assertTrue(ref_b == sys.getrefcount("b"), (ref_b, sys.getrefcount("b")))
            self.assertTrue(ref_c == sys.getrefcount("c"), (ref_c, sys.getrefcount("c")))

        dealloc_after_error(None, None)     # no error
        dealloc_after_error("__getitem__", TypeError, "z")
        dealloc_after_error("__setitem__", TypeError, "z", "z")
        dealloc_after_error("pop", TypeError, "z")
        # error happens in keys() values() and items() only when allocating
        # memory failed, so skip testing.
        only_one_element()

    def test_subscript(self):
        tree = self.tree_cls()
        ref_a = sys.getrefcount("a")

        # empty
        with self.assertRaises(KeyError):
            print(tree[1])
        with self.assertRaises(KeyError):
            print(tree["a"])

        # only one element
        tree[ord("a")] = "a"
        self.assertTrue(tree[ord("a")] == "a")
        with self.assertRaises(KeyError):
            print(tree[1])
        with self.assertRaises(TypeError):
            print(tree["a"])
        self.assertTrue(ref_a + 1 == sys.getrefcount("a"))

        # many element
        tree = self.tree_cls()
        d = random_insert_ascii(tree)
        self.assertTrue(tree[ord("a")] == "a")
        self.assertTrue(ref_a + 1 == sys.getrefcount("a"))

        # not found
        with self.assertRaises(KeyError):
            print(tree[300])

        # test correct
        self.assertTrue(len(d) == len(tree))
        for key, value in d.items():
            self.assertTrue(chr(value) == tree[key])

    def test_insert(self):
        tree = self.tree_cls()
        ref_a = sys.getrefcount("a")

        # the first one
        tree[ord("a")] = "a"
        self.assertTrue(tree[ord("a")] == "a")
        self.assertTrue(ref_a + 1 == sys.getrefcount("a"))

        # insert the same element
        tree[ord("a")] = "a"
        self.assertTrue(tree[ord("a")] == "a")
        self.assertTrue(ref_a + 1 == sys.getrefcount("a"))

        # insert many
        d = random_insert_ascii(tree)
        self.assertTrue(len(d) == len(tree))
        for key, value in d.items():
            self.assertTrue(chr(value) == tree[key])
        self.assertTrue(ref_a + 1 == sys.getrefcount("a"))

        # insert error
        with self.assertRaises(TypeError):
            tree["z"] = "z"

        # deallocate
        del tree
        self.assertTrue(ref_a == sys.getrefcount("a"))

    def test_pop(self):
        tree = self.tree_cls()
        ref_a = sys.getrefcount("a")

        # empty
        with self.assertRaises(KeyError):
            tree.pop(ord("a"))
        self.assertTrue(ref_a == sys.getrefcount("a"))

        # only one element
        tree[ord("a")] = "a"
        self.assertTrue(len(tree) == 1)
        with self.assertRaises(TypeError):
            tree.pop("a")
        self.assertTrue(tree.pop(ord("a")) == "a")
        self.assertTrue(len(tree) == 0)
        self.assertTrue(ref_a == sys.getrefcount("a"))

        # pop all
        d = random_insert_ascii(tree)
        i = 0
        num = len(tree)
        try:
            for key, value in d.items():
                self.assertTrue(chr(key) == tree.pop(key))
                i += 1
        except KeyError as e:
            e.args = e.args + ("%s totoal, %s finished" % (num, i), )
            raise
        self.assertTrue(len(tree) == 0)
        self.assertTrue(ref_a == sys.getrefcount("a"))

    def test_keys_values_items(self):
        tree = self.tree_cls()
        ref_a = sys.getrefcount("a")

        # empty
        self.assertTrue(tree.keys() == [])
        self.assertTrue(tree.values() == [])
        self.assertTrue(tree.items() == [])

        # one element
        tree[ord("a")] = "a"
        self.assertTrue(tree.keys() == [ord("a")])
        self.assertTrue(tree.values() == ["a"])
        self.assertTrue(tree.items() == [(ord("a"), "a")])
        self.assertTrue(ref_a+1 == sys.getrefcount("a"))

        # many element
        for i in range(100):
            tree = self.tree_cls()
            d = random_insert_ascii(tree)
            self.assertTrue(tree.keys() == sorted(d.keys()))
            self.assertTrue(tree.values() == sorted([chr(x) for x in d.values()]))
            self.assertTrue(tree.items() == sorted([(x, chr(x)) for x in d.keys()]))

        del tree
        self.assertTrue(ref_a == sys.getrefcount("a"))


    def test_pop_exactly(self):

        # predecessor is direct child and target is root
        tree = self.tree_cls()
        insert_integer(tree, [20, 10, 30, 5])
        """     20
             10    30
           5
        """
        self.assertTrue(tree.pop(20) == 20)
        self.assertTrue(tree.root() == 10)
        self.assertTrue(tree.items() == [(5, 5), (10, 10), (30, 30)])

        # successor is direct child and target is root
        tree[40] = 40
        """     10
             5     30
                      40
        """
        self.assertTrue(tree.pop(10) == 10)
        self.assertTrue(tree.root() == 30)
        self.assertTrue(tree.items() == [(5, 5), (30, 30), (40, 40)])

        # predecessor is direct child and target is not root
        tree = self.tree_cls()
        insert_integer(tree, [20, 10, 30, 5, 15, 3])
        """            20
                  10        30
               5    15
            3
        """
        self.assertTrue(tree.pop(10) == 10)
        self.assertTrue(tree.items() == [(3, 3), (5, 5), (15, 15), (20, 20), (30, 30)])

        # successor is direct child and target is not root
        tree[17] = 17
        """            20
                   5        30
                3    15
                        17
        """
        self.assertTrue(tree.pop(5) == 5)
        self.assertTrue(tree.items() == [(3, 3), (15, 15), (17, 17), (20, 20), (30, 30)])

        # predecessor is not direct child and target is root
        tree = self.tree_cls()
        insert_integer(tree, [20, 10, 30, 5, 15, 13])
        """      20
             10      30
           5    15
               13
        """
        self.assertTrue(tree.pop(20) == 20)
        self.assertTrue(tree.root() == 15)
        self.assertTrue(tree.items() == [(5, 5), (10, 10), (13, 13), (15, 15), (30, 30)])

        # successor is not direct child and target is root
        tree = self.tree_cls()
        insert_integer(tree, [20, 10, 30, 1, 25, 40, 27])
        tree.pop(20)
        """      10
              1      30
                  25    40
                    27
        """
        self.assertTrue(tree.pop(10) == 10)
        self.assertTrue(tree.root() == 25)
        self.assertTrue(tree.items() == [(1, 1), (25, 25), (27, 27), (30, 30), (40, 40)])

        # predecessor is not direct child and target is not root
        tree = self.tree_cls()
        insert_integer(tree, [20, 10, 30, 5, 15, 7, 6])
        """           20 
                  10       30
               5    15
                7
               6
        """
        self.assertTrue(tree.pop(10) == 10)
        self.assertTrue(tree.items() == [(5, 5), (6, 6), (7, 7), (15, 15), (20, 20), (30, 30)])

        # successor is not direct child and target is not root
        tree = self.tree_cls()
        insert_integer(tree, [20, 10, 30, 1, 25, 40, 35, 37])
        tree.pop(20)
        """     10
             1     30
                25    40
                    35 
                      37
        """
        self.assertTrue(tree.pop(30) == 30)
        self.assertTrue(tree.items() == [(1, 1), (10, 10), (25, 25), (35, 35), (37, 37), (40, 40)])

        # only root
        tree = self.tree_cls()
        tree[1] = 1
        self.assertTrue(tree.pop(1) == 1)

        # only left child and target is root
        insert_integer(tree, [10, 5, 1, 7])
        self.assertTrue(tree.pop(10) == 10)
        self.assertTrue(tree.root() == 5)
        self.assertTrue(tree.items() == [(1, 1), (5, 5), (7, 7)])

        # only right child and target is root
        tree = self.tree_cls()
        insert_integer(tree, [10, 20, 15, 25])
        self.assertTrue(tree.pop(10) == 10)
        self.assertTrue(tree.root() == 20)
        self.assertTrue(tree.items() == [(15, 15), (20, 20), (25, 25)])

        # only left child and target is not root
        tree = self.tree_cls()
        insert_integer(tree, [20, 10, 5, 1, 7])
        """           20 
                  10 
               5    
            1    7
        """
        self.assertTrue(tree.pop(10) == 10)
        self.assertTrue(tree.items() == [(1, 1), (5, 5), (7, 7), (20, 20)])

        # only right child and target is not root
        tree = self.tree_cls()
        insert_integer(tree, [10, 30, 40, 35, 45])
        """     10
                   30
                      40
                    35   45
        """
        self.assertTrue(tree.pop(30) == 30)
        self.assertTrue(tree.items() == [(10, 10), (35, 35), (40, 40), (45, 45)])
