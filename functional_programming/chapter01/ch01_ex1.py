def sum_numeric():
    s = 0
    for n in range(1, 10):
        if n % 3 == 0 or n % 5 == 0:
            s += n
    print(s)


def sum_object_light():
    m = list()
    for n in range(1, 10):
        if n % 3 == 0 or n % 5 == 0:
            m.append(n)
    print(sum(m))


class Summable_List(list):
    def sum(self):
        s = 0
        for v in self:
            s += v
        return s


def sum_full_oo():
    m = Summable_List()
    for n in range(1, 10):
        if n % 3 == 0 or n % 5 == 0:
            m.append(n)
    print(m.sum())


def foldr(seq, op, init):
    if len(seq) == 0:
        return init
    return op(seq[0], sum(seq[1:]))


def until(n, filter_func, v):
    if v == n:
        return []
    if filter_func(v):
        return [v] + until(n, filter_func, v + 1)
    else:
        return until(n, filter_func, v + 1)


def sum_functional():
    mult_3_5 = lambda x: x % 3 == 0 or x % 5 == 0
    add = lambda x, y: x + y
    return foldr(until(10, mult_3_5, 1), add, 0)


def sum_hybrid():
    print(sum(n for n in range(1, 10) if n % 3 == 0 or n % 5 == 0))


def folding():
    print("foldl:", timeit.timeit("((([]+[1])+[2])+[3])+[4]"))
    print("foldr:", timeit.timeit("[]+([1]+([2]+([3]+[4])))"))


demo_1 = """
>>> def sumr(seq):
...     if len(seq) == 0: return 0
...     return seq[0] + sumr(seq[1:])
>>> sumr([7, 11])
18
>>> sumr([11])
11
>>> sumr([])
0
"""

__test__ = {
    "demo_1": demo_1,
}


def test():
    import doctest
    doctest.testmod(verbose=True)
if __name__ == "__main__":
    test()
    # import timeit
    # folding()
