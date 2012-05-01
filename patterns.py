from instructions import Atom, Match, Split, Save


class Pattern(object):
    def _compile(self):
        raise NotImplementedError

    def compile(self):
        return self._compile(Match())

    def __or__(self, other):
        return Disjunction(self, other)

    def __add__(self, other):
        xs = []
        if isinstance(self, Concatenation):
            xs.extend(self.xs)
        else:
            xs.append(self)
        if isinstance(other, Concatenation):
            xs.extend(other.xs)
        else:
            xs.append(other)
        return Concatenation(*xs)

    def __mul__(self, x):
        if isinstance(x, int):
            mn = x
            mx = x
        else:
            assert isinstance(x, tuple)
            mn, mx = x
            if mn == None:
                mn = 0
        return Repetition(self, mn=mn, mx=mx)


class Predicate(Pattern):
    def __init__(self, f):
        self.f = f

    def __str__(self):
        return str(self.f)

    def __repr__(self):
        return "Predicate({0!r})".format(self.f)

    def _compile(self, cont):
        x = Atom(self.f, next=cont)
        return x


class Any(Predicate):
    def __init__(self):
        super(Any, self).__init__(lambda x: True)

    def __str__(self):
        return "Any()"

    def __repr__(self):
        return "Any()"


class Literal(Predicate):
    def __init__(self, x):
        super(Literal, self).__init__(lambda y: x == y)
        self.x = x

    def __str__(self):
        return str(self.x)

    def __repr__(self):
        return "Literal({0})".format(self.x)


class Disjunction(Pattern):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def _compile(self, cont):
        a = self.a._compile(cont)
        b = self.b._compile(cont)
        return Split(a, b)

    def __str__(self):
        return "(" + " | ".join(map(str, [self.a, self.b])) + ")"

    def __repr__(self):
        return "(" + " | ".join(map(repr, [self.a, self.b])) + ")"


class Concatenation(Pattern):
    def __init__(self, *patterns):
        self.xs = list(patterns)
        assert len(self.xs) != 0

    def _compile(self, cont):
        code = cont
        for x in reversed(self.xs):
            code = x._compile(code)
        return code

    def __str__(self):
        return "(" + " + ".join(map(str, self.xs)) + ")"

    def __repr__(self):
        return "(" + " + ".join(map(repr, self.xs)) + ")"


class Star(Pattern):
    def __init__(self, pattern, greedy=True):
        self.x = pattern
        self.greedy = greedy

    def _compile(self, cont):
        ret = Split()
        xcode = self.x._compile(ret)
        if self.greedy:
            next, split = xcode, cont
        else:
            next, split = cont, xcode
        ret.next = next
        ret.split = split
        return ret

    def __str__(self):
        return str(self.x) + "*"

    def __repr__(self):
        return "Star({0!r})".format(self.x)


class Plus(Pattern):
    def __init__(self, pattern, greedy=True):
        self.x = pattern
        self.greedy = greedy

    def _compile(self, cont):
        ret = Split()
        xcode = self.x._compile(ret)
        if self.greedy:
            next, split = xcode, cont
        else:
            next, split = cont, xcode
        ret.next = next
        ret.split = split
        return xcode

    def __str__(self):
        return str(self.x) + "+"

    def __repr__(self):
        return "Plus({0!r})".format(self.x)


class Question(Pattern):
    def __init__(self, pattern, greedy=True):
        self.x = pattern
        self.greedy = greedy

    def _compile(self, cont):
        xcode = self.x._compile(cont)
        if self.greedy:
            return Split(xcode, cont)
        else:
            return Split(cont, xcode)

    def __str__(self):
        return str(self.x) + "?"

    def __repr__(self):
        return "Question({0!r})".format(self.x)


class Group(Pattern):
    def __init__(self, pattern, key):
        self.x = pattern
        self.key = key

    def _compile(self, cont):
        start = Save((self.key, 0))
        end = Save((self.key, 1))
        code = self.x._compile(end)
        start.next = code
        end.next = cont
        return start

    def __str__(self):
        return "Group({0!s}, {1!s})".format(self.x, self.key)

    def __repr__(self):
        return "Group({0!r}, {1!r})".format(self.x, self.key)


class Repetition(Pattern):
    def __init__(self, pattern, mn=0, mx=None, greedy=True):
        self.x = pattern
        self.mn = mn
        self.mx = mx
        self.greedy = greedy

    def _compile(self, cont):
        code = cont
        if self.mx != None:
            q = Question(self.x, self.greedy)
            for _ in xrange(self.mx):
                code = q._compile(code)
        else:
            code = Star(self.x, greedy=self.greedy)._compile(code)
        for _ in xrange(self.mn):
            code = self.x._compile(code)
        return code

    def __str__(self):
        return self._tostring("{0!s}")

    def __repr__(self):
        return self._tostring("{0!r}")

    def _tostring(self, s):
        base = "({" + s + "})*"
        if self.mn == 0 and self.mx == None:
            return base.format(self.x)
        if self.mn == self.mx:
            return (base + "{1}").format(self.x, self.mn)
        return (base + "*({1},{2})").format(self.x, self.mn, self.mx)
