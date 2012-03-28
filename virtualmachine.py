# Some glossry:
#   RE  --  regular expression
#   VM  --  virtual machine
#   Epsilon transitions  --  All VM instructions that do not consume a symbol
#                            or stop the machine.

from instructions import Atom, Match, Split, Save


class Thread(object):
    def __init__(self, pc):
        self.pc = pc
        self.state = {}
        self.i = 0

    def step(self):
        """
        Take single epsilon transitions
        """
        assert not isinstance(self.pc, Atom) and not isinstance(self.pc, Match)
        ret = []
        if isinstance(self.pc, Split):
            s1 = self.pc.next
            s2 = self.pc.split
            self.pc = s1
            ret.append(self.clone(s2))
        elif isinstance(self.pc, Save):
            self.state[self.pc.record] = self.i
            self.pc = self.pc.next
        else:
            raise Exception("Unknown instruction", self.pc)
        return ret

    def feed(self, x):
        """
        Take a transition that involves consuming a symbol
        """
        assert self.idle()
        self.i += 1
        if isinstance(self.pc, Match) or not self.pc.comparison_function(x):
            self.pc = None
        else:
            self.pc = self.pc.next

    def clone(self, pc=None):
        if pc == None:
            pc = self.pc
        c = Thread(pc)
        c.state = dict(self.state)
        c.i = self.i
        return c

    def idle(self):
        return isinstance(self.pc, Atom) or isinstance(self.pc, Match)

    def accepts(self):
        return isinstance(self.pc, Match)

    def get_pc(self):
        return self.pc

    def get_state(self):
        return self.state


class VirtualMachine(object):
    def __init__(self, code):
        self.code = code
        self.reset()

    def reset(self):
        thread = Thread(self.code)
        self.threads = [thread]

    def match(self, sequence):
        ret = None
        self.advance()
        for t in self.threads:
            if t.accepts():
                self._cutoff(t)
                ret = t.get_state()
        for x in sequence:
            if len(self.threads) == 0:
                break
            self.feed(x)
            self.advance()
            for t in self.threads:
                if t.accepts():
                    self._cutoff(t)
                    ret = t.get_state()
        return ret

    def advance(self):
        new = []
        current = self.threads
        current.reverse()
        while len(current) != 0:
            # In this cycle the last thread in `current` is highest priorty
            thread = current.pop()
            if thread.idle():
                self._add(new, thread)
            else:
                split = thread.step()
                for t in split:
                    current.append(t)
                current.append(thread)
        self.threads = new

    def feed(self, x):
        new = []
        for thread in self.threads:
            assert thread.idle()
            thread.feed(x)
            self._add(new, thread)
        self.threads = new

    def _cutoff(self, thread):
        """
        Cuts off threads of lower priority than `thread`
        """
        assert thread in self.threads
        i = self.threads.index(thread)
        self.threads = self.threads[:i]

    def _add(self, xs, thread):
        pc = thread.get_pc()
        if pc != None and pc not in (x.pc for x in xs):
            xs.append(thread)
