from datetime import date
import operator as op

from dateutil.relativedelta import relativedelta

from psyl.lisp import evaluate, GLOBALENV, parse


def test_things():
    GLOBALENV.update({
        '+': op.add,
        '*': op.mul,
        'today': date.today,
    })

    assert evaluate('(+ 3 5)') == 8
    print( evaluate('(today)') )

    assert parse('(+ 3 (* 4 5))') == ['+', 3, ['*', 4, 5]]


def test_keywords():
    def fun(a, b=42, c=None):
        out = a + b
        if c is not None:
            out = out + c
        return out

    GLOBALENV.update({
        'fun': fun,
        '+': op.add
    })

    assert evaluate('(fun 1 #:c 5)') == 48
    assert evaluate('(fun 1 #:b 2 #:c 5)') == 8
    assert evaluate('(+ 2 (fun 1 #:b 2 #:c 5))') == 10
    assert evaluate('(fun 1 #:b (+ 1 1)))') == 3
    assert evaluate('(fun (fun 2 #:b 0) #:b 2)') == 4
