from datetime import date
import operator as op

from dateutil.relativedelta import relativedelta

from psyl.lisp import evaluate, GLOBALENV, parse


def test_things():
    GLOBALENV.update({
        '+': op.add,
        '-': op.sub,
        '*': op.mul,
        '/': op.truediv,
        'today': date.today,
        'monthstart': lambda dt: dt.replace(day=1),
        'yearstart': lambda dt: dt.replace(day=1, month=1),
        'yearend': lambda dt: dt.replace(day=31, month=12),
        'deltadays': lambda dt, days: dt + relativedelta(days=days),
        'deltamonths': lambda dt, months: dt + relativedelta(months=months),
        'deltayears': lambda dt, years: dt + relativedelta(years=years)
    })

    assert evaluate('(+ 3 5)') == 8
    print( evaluate('(today)') )

    assert parse('(+ 3 (* 4 5))') == ['+', 3, ['*', 4, 5]]

