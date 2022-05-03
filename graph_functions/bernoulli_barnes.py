from sympy import factorial
from sympy import bernoulli
from sympy import Symbol
from sympy import Pow


def get_s(a, s, k, n):
    if len(a) == k:
        summ = sum(a)
        if summ == n:
            s.append(a.copy())
        return
    for i in range(n + 1):
        a.append(i)
        get_s(a, s, k, n)
        a.pop()


def get_numbers_array(n):
    bernoulli_numbers = []
    for i in range(n):
        bernoulli_numbers.append(bernoulli(i))
    return bernoulli_numbers


def get_bernoulli(k, n):
    bernoulli_numbers = get_numbers_array(n + k)
    s = []
    get_s([], s, k, n)
    expr = 2
    for i in range(len(s)):
        expr_part = 1
        for j in range(len(s[i])):
            expr_part *= bernoulli_numbers[s[i][j]]
            expr_part /= factorial(s[i][j])
            expr_part *= Pow(Symbol('w_' + str(j + 1)), s[i][j])
        expr += expr_part
    expr -= 2
    return expr


def get_rk(k):
    expr = 1
    for s in range(k + 1):
        expr += Pow(Symbol('lambda'), s) * get_bernoulli(k, k - s) / factorial(s)
    expr -= 1
    for i in range(k):
        expr /= Symbol('w_' + str(i + 1))
    return expr
