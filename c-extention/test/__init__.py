
import os
import sys
import random
import timeit
import unittest

for d in os.listdir("./build"):
    if d.startswith('lib'):
        sys.path.append(os.path.join('build', d))
        break

from sort_example import insertion_sort, merge_sort, heap_sort, quick_sort


data_set = [
    [],
    [1],
    ["aa", "bb"],
    ["bb", "aa"],
]

data_set += [[random.randint(0, i) for j in range(i)]
             for i in range(3, 1000, 10)]

big_data = [random.randint(0, 1000000) for i in range(1024000)]
big_data_set = [
    big_data[0:2000],
    big_data[0:4000],
    big_data[0:8000],
    big_data[0:16000],
    big_data[0:32000],
    big_data[0:64000],
    big_data[0:128000],
    big_data[0:256000],
    big_data[0:512000],
    big_data
]


class CaseInsertionSort(unittest.TestCase):

    def test_ref(self):
        test_reference_count(insertion_sort)

    def test_result(self):
        test_result(insertion_sort)

    def test_performance(self):
        test_performance(insertion_sort)


class CaseMergeSort(unittest.TestCase):

    def test_ref(self):
        test_reference_count(merge_sort)

    def test_result(self):
        test_result(merge_sort)

    def test_performance(self):
        test_performance(merge_sort, 10)


class CaseHeapSort(unittest.TestCase):

    def test_ref(self):
        test_reference_count(heap_sort)

    def test_result(self):
        test_result(heap_sort)

    def test_performance(self):
        test_performance(heap_sort, 10)


class CaseQuickSort(unittest.TestCase):

    def test_ref(self):
        test_reference_count(quick_sort)

    def test_result(self):
        test_result(quick_sort)

    def test_performance(self):
        test_performance(quick_sort, 10)


class CaseBuiltSort(unittest.TestCase):

    def test_performance(self):
        test_performance(sorted, 10)


class CasePythonQuick(unittest.TestCase):

    def test_ref(self):
        test_reference_count(quick_sort_in_python)

    def test_result(self):
        test_result(quick_sort_in_python)

    def test_performance(self):
        test_performance(quick_sort_in_python, 9)


def quick_sort_in_python(o):
    new_list = list(o)
    _quick_sort(new_list, 0, len(o)-1)
    return new_list


def _partition(o, l, r):

    index_s = l-1
    for i in range(l, r):
        if o[i] <= o[r]:
            index_s += 1
            tmp = o[index_s]
            o[index_s] = o[i]
            o[i] = tmp

    index_s += 1
    tmp = o[index_s]
    o[index_s] = o[r]
    o[r] = tmp

    return index_s


def _quick_sort(o, l, r):

    if r > l:
        m = _partition(o, l, r)
        _quick_sort(o, l, m-1)
        _quick_sort(o, m+1, r)


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
    raw_stmt = "%s(big_data_set[%s])"
    new_t = old_t = 0
    print()
    print(func.__name__)

    for i in range(num):
        stmt = raw_stmt % (func.__name__, i)
        old_t = new_t
        new_t = timeit.timeit(stmt, number=1, globals=globals())
        content = ("%4sK ->" % (len(big_data_set[i])//1000), round(new_t, 3))
        if i > 0:
            content += ("x%s" % round(new_t/old_t, 1),)

        print(*content, sep=" ")




