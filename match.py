from virtualmachine import VirtualMachine
from patterns import Pattern, Any, Star, Group, _start, _end


class Match(object):
    """
    Non-opaque class used to return RE match information.
    Matching soubgroup key `None` is reserved for the matching of the whole
    string.
    """
    def __init__(self, state=None):
        self.state = state

    def span(self, key=None):
        return self[key]

    def start(self, key=None):
        return self[key][0]

    def end(self, key=None):
        return self[key][1]

    def group(self, key=None):
        return self[key]

    def __getitem__(self, key):
        try:
            return self.state[_start(key)], self.state[_end(key)]
        except KeyError:
            raise KeyError(key)

    def __contains__(self, key):
        return _start(key) in self.state

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
    """
    An experimental implementation of finditer.
    The idea here is to make an implementation that is able to work with any
    iterator, not necessariry the indexable ones.
    This implies (among other things) that each element is feeded only once and
    then discarded.
    """
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
