from cefc import service

class ValueWrapper:
    def __init__(self, value):
        self.value = value
    def inc(self):
        self.value += 1
        return self.value

@service
def incinv(a):
    return 1.0/a.value.inc()

a = ValueWrapper(ValueWrapper(2))
print(incinv(a))
print(a.value.value)
