from cefc import service


def test_obj_error_fallback():
    class ValueWrapper:
        def __init__(self, value):
            self.value = value
        def inc(self):
            self.value += 1
            return self.value
    @service
    def incinv(a):
        return 1.0 / a.value.inc()
    a = ValueWrapper(ValueWrapper(-1))
    print(incinv(a))
    assert a.value.value == -1


def test_obj_success():
    class ValueWrapper:
        def __init__(self, value):
            self.value = value
        def inc(self):
            self.value += 1
            return self.value
    @service
    def incinv(a):
        return 1.0 / a.value.inc()
    a = ValueWrapper(ValueWrapper(2))
    assert incinv(a) == 1.0/3
    assert a.value.value == 3