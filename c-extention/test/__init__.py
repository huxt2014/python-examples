
import os
import sys
import random
import timeit
import unittest

for d in os.listdir("./build"):
    if d.startswith('lib'):
        sys.path.append(os.path.join('build', d))
        break

import sort_example


data_set = [
    [],
    [1],
    ["aa", "bb"],
    ["bb", "aa"],
]

data_set += [[random.randint(0, i) for j in range(i)]
             for i in range(3, 1000, 10)]

big_data = [random.randint(0, 10000000) for i in range(512000)]
big_data_set = [
    big_data[0:2000],
    big_data[0:4000],
    big_data[0:8000],
    big_data[0:16000],
    big_data[0:32000],
    big_data[0:64000],
    big_data[0:128000],
    big_data[0:256000],
    big_data
]


class CaseInsertionSort(unittest.TestCase):

    def test_ref(self):
        test_reference_count(sort_example.insertion_sort)

    def test_result(self):
        test_result(sort_example.insertion_sort)

    def test_performance(self):
        test_performance(sort_example.insertion_sort)


class CaseMergeSort(unittest.TestCase):

    def test_ref(self):
        test_reference_count(sort_example.merge_sort)

    def test_result(self):
        test_result(sort_example.merge_sort)

    def test_performance(self):
        test_performance(sort_example.merge_sort, 9)


def test_reference_count(func):
    i1, i2, i3 = ('aa', 'bb', 'cc')
    local_set = [
        [i1],
        [i1, i2],
        [i2, i1],
        [i1, i2, i3],
        [i3, i2, i1],
    ]
    invalid_data = [i1, i2, None]

    ref1 = [sys.getrefcount(i1),
            sys.getrefcount(i2),
            sys.getrefcount(i3)]

    for d in local_set:
        func(d)

    try:
        func(invalid_data)
    except TypeError:
        pass
    else:
        raise Exception('should get TypeError')

    ref2 = [sys.getrefcount(i1),
            sys.getrefcount(i2),
            sys.getrefcount(i3)]

    assert ref1 == ref2, (ref1, ref2)


def test_result(func):
    for data in data_set:
        r1 = func(data)
        r2 = sorted(data)
        assert r1 == r2, (r1, r2)


def test_performance(func, num=5):
    raw_stmt = "sort_example.%s(big_data_set[%s])"
    new_t = old_t = 0
    print()
    print(func.__name__)

    for i in range(num):
        stmt = raw_stmt % (func.__name__, i)
        old_t = new_t
        new_t = timeit.timeit(stmt, number=1, globals=globals())
        content = ("%3sK ->" % (len(big_data_set[i])//1000), round(new_t, 3))
        if i > 0:
            content += ("x%s" % round(new_t/old_t, 1),)

        print(*content, sep=" ")




