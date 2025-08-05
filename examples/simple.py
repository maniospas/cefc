from cefc import service

@service
def func(a: list, b: int):
    a[0] = 1
    a[0] /= b

@service
def outer_func(a: list, b:int):
    return func(a, b)

a = [1,2,3]
outer_func(a, b=0)
print(a)

