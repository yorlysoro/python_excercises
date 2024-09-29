form typing import Callable, Iterator

# next_ = lambda n, x: (x+n/x)/2

def next_(n: float, x: float) -> float:
    return (x + n / x) / 2

def repeat(f: Callable[[float], float], a: float)-> Iterator[float]:
    yield a
    yield from repeat(f, f(a))


def within(f: Callable, iterable: Iterator[float]) -> Iterator[float]:
    def head_tail(eps: float, a: float, iterable: Iterator[float]):
        b = next(iterable)
        if abs(a - b) < eps:
            return b
        return head_tail(eps, b, iterable)
    return head_tail(eps, next(iterable), iterable)


def sqrt(a0: float, eps: float, n: float):
    return within(eps, repeat(lambda x: next_(n, x), a0))


def test():
    import doctest
    doctest.testmod(verbose=1)

if __name__ == '__main__':
    test()
