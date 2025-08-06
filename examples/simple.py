from cefc import service, commit

@service
def func(a: list, b: int):
    a[2] = 100
    a.append(4)
    #commit(a) # (enable to apply all modifications till now)
    a[0] = 1
    a[0] /= b

@service
def outer_func(a: list, b:int):
    a[1] = 100
    #commit(a) # (enable to apply all modifications till now)
    return func(a, b)

a = [1,2,3]
err = outer_func(a, b=0)
print(a)
