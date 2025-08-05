# CEfC

A *call-effect-commit* schema for safe data management Python.

This a metaprogramming framework that enables the safe execution
of Python code by tracking data modifications and commiting to them
only after functions complete their runs without errors. In the end,
you can create fast-failing services that can retry 


## :zap: Quickstart

Install *CEfC* per `pip install cefc`. Then create the
following code snippet.

```python
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
```


![Error example](docs/error.png)