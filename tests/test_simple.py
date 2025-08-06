from cefc import service, commit


def test_list_failure():
    @service
    def func(a: list, b: int):
        a[2] = 100
        a.append(4)
        # commit(a) # (enable to apply all modifications till now)
        a[0] = 1
        a[0] /= b

    @service
    def outer_func(a: list, b: int):
        a[1] = 100
        # commit(a) # (enable to apply all modifications till now)
        return func(a, b)

    a = [1, 2, 3]
    outer_func(a, b=0)
    assert len(a) == 3
    assert a[2] == 3


def test_list_success():
    @service
    def func(a: list, b: int):
        a[2] = 100
        a.append(4)
        # commit(a) # (enable to apply all modifications till now)
        a[0] = 1
        a[0] /= b

    @service
    def outer_func(a: list, b: int):
        a[1] = 100
        # commit(a) # (enable to apply all modifications till now)
        return func(a, b)

    a = [1, 2, 3]
    outer_func(a, b=2)
    assert len(a) == 4
    assert a[2] == 100

