
import sys
import socket
import struct
import timeit
import unittest
from random import randint

try:
    import Queue as queue
except ImportError:
    import queue

Empty = queue.Empty


from pympler import tracker
import ip_store


if sys.version_info[0] == 2:
    def atohl(ip):
        return socket.ntohl(struct.unpack("I", socket.inet_aton(ip))[0])
else:
    def atohl(ip):
        if hasattr(ip, "decode"):
            ip = ip.decode()
        return socket.ntohl(struct.unpack("I", socket.inet_aton(ip))[0])


def htoa(ip_int):
    return socket.inet_ntoa(struct.pack("I", socket.htonl(ip_int)))


def check_db(db):
    if len(db) == 0:
        raise Exception("empty file")

    for i in range(0, len(db)):
        r = db[i]
        if r[0] > r[1]:
            raise Exception("row %s, %s <= %s ?" % (i+1, r[0], r[1]))

    for i in range(0, len(db) -1):
        r1 = db[i]
        r2 = db[i+1]
        if r1[1] >= r2[0]:
            raise Exception("row %s, %s, [%s,%s] < [%s, %s] ?" %
                            (i+1, i+2, r1[0], r1[1], r2[0], r2[1]))

    if db[0][0] < 0:
        raise Exception("negative value found: %s" % db[0][0])
    if db[-1][1] >= 2 ** 32:
        raise Exception("ip address overflow: %s" % db[-1][1])


def get_probes(db):
    """for test"""
    if len(db) == 0:
        raise Exception("empty db")

    probes = []

    for i in range(0, len(db)):
        r1 = db[i]
        v = r1[2:4]

        if r1[0] != r1[1]:
            probes.extend([(htoa(r1[0]), v),
                           (htoa(r1[1]), v),
                           (htoa((r1[0] + r1[1])//2), v)])
        else:
            probes.append((htoa(r1[0]), v))

        if i < len(db) - 1:
            r2 = db[i+1]
            if r2[0] - r1[1] > 1:
                probes.append((htoa(r1[1]+1), None))

    if db[0][0]-1 >= 0:
        probes.append((htoa(db[0][0]-1), None))
    if db[-1][1]+1 < 2 ** 32:
        probes.append((htoa(db[-1][1]+1), None))

    return probes


def search(db, ip_address):
    ip_int = atohl(ip_address)

    begin = 0
    end = len(db) - 1

    while begin <= end:
        mid = (begin + end)//2
        m_record = db[mid]

        if ip_int < m_record[0]:
            end = mid - 1
        elif ip_int > m_record[1]:
            begin = mid + 1
        else:
            if m_record[0] <= ip_int <= m_record[1]:
                return m_record[2:4]
            else:
                return None
    return None


class Test(unittest.TestCase):

    def setUp(self):
        ip_store.load([])

    def test_atohl(self):
        ip_list = ["127.0.0.1", "0.0.0.0", "255.255.255.255",
                   "10.10.10.1", "192.168.0.1",
                   b"127.0.0.1", b"0.0.0.0", b"255.255.255.255",
                   b"10.10.10.1", b"192.168.0.1"]
        if sys.version_info[0] == 2:
            ip_list.extend([u"127.0.0.1", u"0.0.0.0", u"255.255.255.255",
                            u"10.10.10.1", u"192.168.0.1"])

        for ip in ip_list:
            self.assertTrue(atohl(ip) == ip_store.atohl(ip),
                            (ip, atohl(ip), ip_store.atohl(ip)))

        with self.assertRaises(TypeError):
            ip_store.atohl(1)

        with self.assertRaises(ValueError):
            ip_store.atohl("123.")

    def test_store_failed(self):
        with self.assertRaises(TypeError):
            ip_store.load(1)
        assert ip_store.size() == 0, ip_store.size()

        ip_store.load([])
        assert ip_store.size() == 0, ip_store.size()

        test_db1 = [(1, 2, 'a', 'a'),
                    3]
        test_db2 = [(1, 2, 'a', 'a'),
                    ()]
        test_db3 = [(1, 2, 'a', 'a'),
                    (1.1, 1.1, 'a', 'a')]
        test_db4 = [(1, 2, 'a', 'a'),
                    (-10, 1.1, 'a', 'a')]
        test_db5 = [(1, 2, 'a', 'a'),
                    (3, 4, 'a')]
        ref_count = sys.getrefcount('a')

        def test_error(_db, error, name):
            with self.assertRaises(error):
                ip_store.load(_db)
            ref_count_new = sys.getrefcount('a')
            self.assertTrue(ref_count == ref_count_new, (name, ref_count, ref_count_new))
            self.assertTrue(ip_store.size() == 0, (name, ip_store.size())),

        test_error(test_db1, TypeError, "test_db1")
        test_error(test_db2, IndexError, "test_db2")
        test_error(test_db3, TypeError, "test_db3")
        if sys.version_info[0] == 3:
            test_error(test_db4, OverflowError, "test_db4")
        test_error(test_db5, IndexError, "test_db5")

    def test_store_succeed(self):

        test_db1 = [(1, 2, 'a', 'a'),
                    (3, 4, 'a', 'a')]
        test_db2 = [(1, 2, 'a', 'a'),
                    (3, 4, 'a', 'a'),
                    (5, 6, 'a', 'a')]
        test_db3 = [(1, 2, 'b', 'c'),
                    (3, 4, 'd', 'e')]

        ref_count = sys.getrefcount('a')
        ref_count_b = sys.getrefcount('b')

        def test_ok(_db, change, name):
            ip_store.load(_db)
            ip_store.search("0.0.0.1")
            self.assertTrue(ip_store.size() == len(_db), (ip_store.size(), len(_db), name))
            ref_count_new = sys.getrefcount('a')
            self.assertTrue(ref_count + change == ref_count_new,
                            (name, ref_count, ref_count_new))

        test_ok(test_db1, 4, "test_db1")
        test_ok(test_db2, 6, "test_db2")
        test_ok(test_db3, 0, "test_db3")

        for i in range(2):
            self.assertTrue(ip_store.get(i) == test_db3[i])

        ip_store.load([])
        new_ref_count_b = sys.getrefcount('b')
        self.assertTrue(ref_count_b == new_ref_count_b)

    def test_get_failed(self):

        with self.assertRaises(TypeError):
            ip_store.get(1.1)

        with self.assertRaises(IndexError):
            ip_store.get(-1)

        with self.assertRaises(IndexError):
            ip_store.get(0)

        ip_store.load([(1, 2, 'a', 'a')])

        ip_store.get(0)
        with self.assertRaises(IndexError):
            ip_store.get(1)


def get_test_db():
    db = []
    i = 100
    ceil = 2**26

    while i < ceil:
        v = (i, i)
        dice = randint(0, 5)
        if dice == 0:
            # begin = end
            begin = end = i
        else:
            # begin < end
            begin = i
            end = i + randint(500, 800)

        db.append((begin, end) + v)

        dice = randint(0, 5)
        if dice == 0:
            # skip
            i = end + randint(50, 500)
        else:
            i = end + 1

    check_db(db)

    return db


db = get_test_db()
probe_list = get_probes(db)


class TestSearch(unittest.TestCase):

    def test_p_search(self):
        for probe in probe_list:
            self.assertTrue(probe[1] == search(db, probe[0]))

    def test_c_search(self):
        ip_store.load(db)
        for probe in probe_list:
            self.assertTrue(probe[1] == ip_store.search(probe[0]),
                            (probe[1], ip_store.search(probe[0])))

    def test_speed(self):
        ip_store.load(db)
        raw_stmt_p = """
for probe in probe_list:
    search(db, probe[0])
        """
        raw_stmt_c = """
for probe in probe_list:
    ip_store.search(probe[0])
        """

        if sys.version_info[0] == 3:
            new_t = timeit.timeit(raw_stmt_p, number=1, globals=globals())
            print("Python time: %s" % round(new_t, 3))

            new_t = timeit.timeit(raw_stmt_c, number=1, globals=globals())
            print("C time: %s" % round(new_t, 3))


class TestMemory(unittest.TestCase):

    def test_(self):
        ip_store.load(db)
        tr = tracker.SummaryTracker()
        print(sys.getrefcount(None))

        for i in range(10):
            for probe in probe_list:
                ip_store.search(probe[0])

        tr.print_diff()
        print(sys.getrefcount(None))

"""
from test import db, probe_list, ip_store
for i in range(3000):
    ip_store.load(db)
for i in range(1000):
    for prob in probe_list:
        ip_store.search(prob[0])
"""
