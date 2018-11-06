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

