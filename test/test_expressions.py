from datetime import date
import operator as op

from dateutil.relativedelta import relativedelta

from psyl.lisp import evaluate, GLOBALENV, parse, serialize


def test_things():
    GLOBALENV.update({
        '+': op.add,
        '*': op.mul,
        'today': date.today,
    })

    assert evaluate('(+ 3 5)') == 8
    print( evaluate('(today)') )

    assert parse('(+ 3 (* 4 5))') == ['+', 3, ['*', 4, 5]]
    assert parse('(and #t #f)') == ['and', True, False]


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


def test_parse_serialize():
    expr = parse('(fun 1 "foo" #:c 5 (zogzog 42))')
    assert [
        node.__class__.__name__
        for node in expr
    ] == [
        'Symbol', 'int', 'str', 'Keyword', 'int', 'list'
    ]

    assert serialize(parse('(fun 1 #:c "babar")')) == '(fun 1 #:c "babar")'
    assert serialize(parse('(fun 1 #:c (+ 5.0 7))')) == '(fun 1 #:c (+ 5.0 7))'
