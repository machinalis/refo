# -*- coding: UTF-8 -*-
import unittest
import refo
import re
import math


def isprime(x):
    if x < 2:
        return False
    top = int(math.sqrt(x))
    for i in xrange(2, top + 1):
        if x % i == 0:
            return False
    return True


def _seq2str(seq):
    xs = []
    for x in seq:
        if isprime(x):
            xs.append("a")
        else:
            xs.append("b")
    return "".join(xs)


class TestRefoModule(unittest.TestCase):
    seq = xrange(10000)
    a = refo.Predicate(isprime)
    b = refo.Predicate(lambda x: not isprime(x))
    string = _seq2str(seq)

    def _eq_span_n_stuff(self, m, strm):
        assert (m and strm) or (not m and not strm)
        self.assertNotEqual(m, None)
        self.assertNotEqual(strm, None)
        self.assertEqual(m.span(), strm.span())

    def _eq_list_n_stuff(self, xs, strxs):
        xs = [x.span() for x in xs]
        strxs = [x.span() for x in strxs]
        self.assertListEqual(xs, strxs)

    def test_match1(self):
        regex = self.b + self.b + self.a + self.a + self.b
        strregex = re.compile("bbaab")
        m = refo.match(regex, self.seq)
        strm = strregex.match(self.string)
        self._eq_span_n_stuff(m, strm)

    def test_match2(self):
        # This regular expression is known to kill the python re module
        # because it exploits the fact that the implementation has exponential
        # worst case complexity.
        # Instead, this implementation has polinomial worst case complexity,
        # and therefore this test should finish in a reasonable time.
        N = 100
        a = refo.Literal("a")
        string = "a" * N
        regex = refo.Question(a) * N + a * N
        m = refo.match(regex, string)
        self.assertNotEqual(m, None)

    def test_search1(self):
        regex = self.a + self.b + self.b + self.b + self.a
        strregex = re.compile("abbba")
        m = refo.search(regex, self.seq)
        strm = strregex.search(self.string)
        self._eq_span_n_stuff(m, strm)

    def test_search2(self):
        tab = self.a + self.b + self.a
        regex = tab + self.b * 3 + tab
        strregex = re.compile("ababbbaba")
        m = refo.search(regex, self.seq)
        strm = strregex.search(self.string)
        self._eq_span_n_stuff(m, strm)

    def test_search3(self):
        tab = self.a + self.b
        regex = tab + tab + refo.Plus(self.b)
        strregex = re.compile("ababb+")
        m = refo.search(regex, self.seq)
        strm = strregex.search(self.string)
        self._eq_span_n_stuff(m, strm)

    def test_search4(self):
        tab = self.a + self.b
        regex = tab * 2 + refo.Plus(self.b, greedy=False)
        strregex = re.compile("ababb+?")
        m = refo.search(regex, self.seq)
        strm = strregex.search(self.string)
        self._eq_span_n_stuff(m, strm)

    def test_search5(self):
        tab = self.a + self.b
        regex = tab * (2, 5)
        strregex = re.compile("(?:ab){2,5}")
        m = refo.search(regex, self.seq)
        strm = strregex.search(self.string)
        self._eq_span_n_stuff(m, strm)

    def test_finditer1(self):
        tab = self.a + self.b
        regex = tab * (2, None)
        strregex = re.compile("(?:ab){2,}")
        xs = list(refo.finditer(regex, self.seq))
        strxs = list(strregex.finditer(self.string))
        self._eq_list_n_stuff(xs, strxs)

    def test_finditer2(self):
        tab = self.a + self.b
        regex = tab * (2, None) + refo.Group(refo.Plus(self.b), "foobar")
        strregex = re.compile("(?:ab){2,}(b+)")
        xs = list(refo.finditer(regex, self.seq))
        strxs = list(strregex.finditer(self.string))
        xs = [x.group("foobar") for x in xs]
        strxs = [x.span(1) for x in strxs]
        self.assertListEqual(xs, strxs)


if __name__ == "__main__":
    unittest.main()
