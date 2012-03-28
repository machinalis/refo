from instructions import Atom, Match, Split, Save


class Pattern(object):
    def _compile(self):
        raise NotImplementedError

    def compile(self):
        return self._compile(Match())

    def __or__(self, other):
        return Disjunction(self, other)

    def __add__(self, other):
        if isinstance(self, Concatenation):
            self.push_back(other)
            return self
        if isinstance(other, Concatenation):
            other.push_front(self)
            return other
        return Concatenation(self, other)

    def __mul__(self, x):
        if isinstance(x, int):
            mn = x
            mx = x
        else:
            assert isinstance(x, tuple)
            mn, mx = x
            if mn == None:
                mn = 0
        return Repeat(self, mn=mn, mx=mx)


class Any(Pattern):
    def __str__(self):
        return "Any()"

    def __repr__(self):
        return "Any()"

    def __call__(self, y):
        return True

    def _compile(self, cont):
        x = Atom(self, next=cont)
        return x


class Literal(Pattern):
    def __init__(self, x):
        self.x = x

    def __str__(self):
        return str(self.x)

    def __repr__(self):
        return "Literal({0})".format(self.x)

    def __call__(self, y):
        return self.x == y

    def _compile(self, cont):
        x = Atom(self, next=cont)
        return x


class Disjunction(Pattern):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def _compile(self, cont):
        a = self.a._compile(cont)
        b = self.b._compile(cont)
        return Split(a, b)

    def __str__(self):
        return "(" + " | ".join(map(str, self.xs)) + ")"

    def __repr__(self):
        return "(" + " | ".join(map(repr, self.xs)) + ")"


class Concatenation(Pattern):
    def __init__(self, *patterns):
        self.xs = list(patterns)
        assert len(self.xs) != 0

    def _compile(self, cont):
        code = cont
        for x in reversed(self.xs):
            code = x._compile(code)
        return code

    def push_back(self, p):
        self.xs.append(p)

    def push_front(self, p):
        self.xs.insert(p, 0)

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

    # !! FIXME: put __str__ and __repr__

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
        if self.mn == 0 and self.mx == None:
            return "({0})*".format(str(self.x))
        if self.mn == self.mx:
            return "({0})*{1}".format(str(self.x), self.mn)
        return "({0})*({1},{2})".format(str(self.x), self.mn, self.mx)

    def __repr__(self):
        if self.mn == 0 and self.mx == None:
            return "({0})*".format(repr(self.x))
        if self.mn == self.mx:
            return "({0})*{1}".format(repr(self.x), self.mn)
        return "({0})*({1},{2})".format(repr(self.x), self.mn, self.mx)


class CodePrinter:
    def __init__(self, code):
        xs = []
        d = {}
        q = [code]
        while len(q) != 0:
            c = q.pop()
            if c in d:
                continue
            d[c] = len(xs)
            xs.append(c)
            x = getattr(c, "split", None)
            if x != None:
                q.append(x)
            x = getattr(c, "next", None)
            if x != None:
                q.append(x)
        self.xs = xs
        self.d = d

    def _code_to_line(self, code):
        lineno = self._lineno(code)
        if isinstance(code, Split):
            mnemonic = "Split"
            i = self._lineno(code.next)
            j = self._lineno(code.split)
            jump = "-> {0:<4}-> {1}".format(i, j)
        else:
            mnemonic = str(code)
            jump = ""
            if code.next != None:
                to = self._lineno(code.next)
                if to != lineno + 1:
                    jump = "-> {0}".format(to)
        return "{0:<8}{1:24}{2}".format(lineno, mnemonic, jump)

    def _lineno(self, code):
        return self.d[code] + 1

    def tostr(self):
        lines = []
        for code in self.xs:
            line = self._code_to_line(code)
            lines.append(line)
        return "\n".join(lines)


if __name__ == "__main__":
    from virtualmachine import VirtualMachine

    #base = (Literal(1) + Literal(2)) | Literal(3)
    #expr =  Group(base, "key") + Star(Literal(1))
    #expr =    Star(Any()) | Literal(1)
    #expr = Question(Literal(1), greedy=False) + Literal(1)
    #expr = Repetition(Literal(1), 1, 3, greedy=True)
    expr = Star(Literal("a") + Literal(1)) + Literal(2)

    expr = Group(expr, 0)
    code = expr.compile()

    printer = CodePrinter(code)
    print
    print repr(expr)
    print
    print printer.tostr()
    print
    vm = VirtualMachine(code)
    #sequence = [1,1,1,4,2]
    sequence = (["a",3] * 1) + [2]
    #sequence = [3,3,3]
    state = vm.match(sequence)
    if state == None:
        print "\nDoes not accept\n"
    else:
        print "\nAccepts. State:\n"
        groups = set((key for key, _ in state.iterkeys()))
        for key in groups:
            i = state[(key, 0)]
            j = state[(key, 1)]
            s = "{0!r} spans between {1} and {2} and has captured: {3!r}"
            print s.format(key, i, j, sequence[i:j])
