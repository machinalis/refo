from patterns import *  # Fixme, imports all
from refo import *  # Fixme, imports all


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


class CodeChecker(object):

    def __init__(self, code):
        delta = {}
        q = [code]
        seen = set()
        while len(q) != 0:
            current = q.pop()
            if current in seen:
                continue
            seen.add(current)
            xs = []
            x = getattr(current, "next", None)
            if x != None:
                xs.append(x)
            x = getattr(current, "split", None)
            if x != None:
                xs.append(x)
            q.extend(xs)
            delta[current] = []
            if isinstance(current, Split) or isinstance(current, Save):
                delta[current].extend(xs)

        reachable = {}
        for node in delta:
            q = list(delta[node])
            seen = set()
            while len(q) != 0:
                current = q.pop()
                if current in seen:
                    continue
                seen.add(current)
                q.extend(delta[current])
            reachable[node] = seen
            if node in seen:
                print "Warning!", node, "can reach itself"

# A toy to catch xml tags
tag = Literal("<") + Plus(Any(), greedy=False) + Literal(">")
test = """
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE source SYSTEM "source.dtd">
<moses:source xmlns:moses="http://www.statmt.org/moses/">>
<moses:meta lang="" source="path/file.xml" domain="" project=""/>
<moses:ut id="u1">This is ac current, the same as AC CuRRent.</moses:ut>
<moses:ut id="u1">Single word glossary: alloy Alloy.</moses:ut>
</moses:source>
"""

"""
for m in finditer(tag, test):
    i, j = m.span()
    #print repr(test[i:j])

contents = tag + Group(Star(Any(), greedy=False), 0) + tag

for m in finditer(contents, test):
    i, j = m[0]
    #print repr(test[i:j])
"""


s = "aaaaabaaa"
regex = Star(Literal("a"), greedy=True)
for m in finditer_lame(regex, s):
    i, j = m.span()
    print i, j, s[i:j]

import refo

pattern = regex
#pattern = Star(Star(Any(), greedy=False) + Group(pattern, None))
cp = CodePrinter(pattern.compile())
print cp.tostr()
CodeChecker(pattern.compile())
assert False
m = refo._match(pattern, s)
if m != None:
    i, j = m.span()
    print i, j, s[i:j]
