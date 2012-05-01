from virtualmachine import VirtualMachine
from virtualmachine import Thread  # FIXME: eraseme
from patterns import Pattern, Any, Star, Group


class Match(object):
    """
    Non-opaque class used to return RE match information.
    """
    def __init__(self, state=None):
        self.state = state

    def span(self):
        return self[None]

    def start(self):
        return self[None][0]

    def end(self):
        return self[None][1]

    def __getitem__(self, key):
        try:
            return self.state[(key, 0)], self.state[(key, 1)]
        except KeyError:
            raise KeyError(key)

    def offset(self, amount):
        self.state = {key: i + amount for key, i in self.state.iteritems()}


def _match(pattern, iterable):
    assert isinstance(pattern, Pattern)
    code = pattern.compile()
    vm = VirtualMachine(code)
    m = Match()
    # Start VM
    vm.do_epsilon_transitions()
    m.state = vm.accepting_state(None)
    vm.cutoff()
    for x in iterable:
        if not vm.is_alive():
            break
        vm.feed(x)
        vm.do_epsilon_transitions()
        m.state = vm.accepting_state(m.state)
        vm.cutoff()
    if m.state == None:
        return None
    return m


def match(pattern, iterable):
    pattern = Group(pattern, None)
    return _match(pattern, iterable)


def search(pattern, iterable):
    assert isinstance(pattern, Pattern)
    pattern = Star(Any(), greedy=False) + Group(pattern, None)
    return _match(pattern, iterable)


def finditer_lame(pattern, sequence):
    """
    The lame implementation
    """
    offset = 0
    while offset <= len(sequence):
        it = (sequence[i] for i in xrange(offset, len(sequence)))
        m = search(pattern, it)
        if m == None:
            break
        m.offset(offset)
        yield m
        i, offset = m.span()
        if i == offset:
            offset += 1


def finditer_alt(pattern, iterable):
    assert isinstance(pattern, Pattern)
    pattern = Star(Star(Any(), greedy=False) + Group(pattern, None))
    code = pattern.compile()
    vm = VirtualMachine(code)
    m = Match()
    new = Match()
    # Start VM
    vm.do_epsilon_transitions()
    vm.cutoff()
    for x in iterable:
        if not vm.is_alive():
            break
        vm.feed(x)
        vm.do_epsilon_transitions()
        new.state = vm.accepting_state(None)
        if new.state != None:
            if m.state == None:
                m.state = new.state
            elif m.start() == new.start() and m.end() < new.end():
                m.state = new.state
            elif m.start() != new.start():
                yield m
                m = new
                new = Match()
        vm.cutoff()
    if m.state != None:
        yield m


finditer = finditer_lame


"""
def finditer(pattern, iterable):
    assert isinstance(pattern, Pattern)
    #pattern = Star(Any(), greedy=False) + Group(pattern, None)
    pattern = Group(pattern, None)
    code = pattern.compile()
    vm = VirtualMachine(code)
    start = 0
    end = -1
    m = Match()
    new = Match()
    # Start VM
    vm.do_epsilon_transitions()
    new.state = vm.accepting_state(None)
    if new.state != None:
        m = Match(new.state)
    vm.cutoff()
    for x in iterable:
        if not vm.is_alive():
            break
        vm.feed(x)
        vm.threads.append(Thread(vm.code))
        vm.do_epsilon_transitions()
        new.state = vm.accepting_state(None)
        if new.state != None:
            print "new state", new.span()
            if start == new.start() and end < new.end():
                m = Match(new.state)
            elif end <= new.start():
                yield m
                m = Match(new.state)
            start, end = m.span()
        vm.cutoff()
    if m.state != None:
        yield m
"""
