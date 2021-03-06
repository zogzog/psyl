from datetime import date
import operator as op

from dateutil.relativedelta import relativedelta
import pytest

from psyl.lisp import (
    Env,
    evaluate,
    Keyword,
    parse,
    pevaluate,
    serialize,
    Symbol
)


def test_things():
    env = Env({
        '+': op.add,
        '*': op.mul,
        'today': date.today,
    })

    assert evaluate('(+ 3 5)', env) == 8
    print( evaluate('(today)', env) )

    assert parse('(+ 3 (* 4 5))') == ['+', 3, ['*', 4, 5]]
    assert parse('(and #t #f)') == ['and', True, False]

    assert repr(Symbol('s')) == "'s"
    assert repr(Keyword('k')) == '#:k'


def test_parallel_eval():
    def nope():
        raise ValueError('nope')
    env = Env({
        '+': op.add,
        'cat': op.add,
        'list': lambda *x: list(x),
        'raise': nope
    })
    assert pevaluate('(cat (list "a" "b" "c") (list 1 2 3))', env) == [
        "a", "b", "c", 1, 2, 3
    ]
    assert pevaluate('(+ 3 5)', env) == 8
    assert pevaluate(
        '(cat (list "a" "b" "c") '
        '     (cat (list 1 2 3) (list "d" "e" "f")))',
        env) == [
        "a", "b", "c", 1, 2, 3, "d", "e", "f"
    ]
    with pytest.raises(ValueError) as err:
        pevaluate('(list (raise) (raise) (raise))', env)
    assert err.value.args[0] == 'nope'


def test_broken():
    env = Env({
        '+': op.add,
    })

    with pytest.raises(SyntaxError):
        assert evaluate('(+', env)
    with pytest.raises(SyntaxError):
        assert evaluate('(+ 3 4', env)

    # not too pretty (we are being generous ;)
    assert evaluate('4)', env) == 4
    assert evaluate('(+ 2 2))', env) == 4


def test_blocking():
    env = Env({
        '+': op.add,
    })
    with pytest.raises(SyntaxError):
        evaluate('(+ "3" 3")', env)


def test_keywords():
    def fun(a, b=42, c=None):
        out = a + b
        if c is not None:
            out = out + c
        return out

    env = Env({
        'fun': fun,
        '+': op.add
    })

    assert evaluate('(fun 1 #:c 5)', env) == 48
    assert evaluate('(fun 1 #:b 2 #:c 5)', env) == 8
    assert evaluate('(+ 2 (fun 1 #:b 2 #:c 5))', env) == 10
    assert evaluate('(fun 1 #:b (+ 1 1)))', env) == 3
    assert evaluate('(fun (fun 2 #:b 0) #:b 2)', env) == 4


def test_parse_serialize():
    expr = parse('(fun 1 "foo" nil #f #:c 5 (zogzog 42 #t))')
    assert [
        node.__class__.__name__
        for node in expr
    ] == [
        'Symbol', 'int', 'str', 'NoneType', 'bool', 'Keyword', 'int', 'list'
    ]

    assert serialize(parse('(fun 1 #t #f #:c "babar")')) == '(fun 1 #t #f #:c "babar")'
    assert serialize(parse('(fun 1 nil #:c (+ 5.0 7))')) == '(fun 1 nil #:c (+ 5.0 7))'
