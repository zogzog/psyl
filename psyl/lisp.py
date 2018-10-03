# Lisp Interpreter in Python
# inpired from See http://norvig.com/lispy2.html
import re
import io
import operator as op


class Env(dict):

    def find(self, var):
        if var in self:
            return self
        raise LookupError(var)

    def add_globals(self, symbols):
        "Add some Scheme standard procedures."
        self.update(symbols)
        return self


class Symbol(str):

    @staticmethod
    def get(s, symbol_table={}):
        "Find or create unique Symbol entry for str s in symbol table."
        if s not in symbol_table:
            symbol_table[s] = Symbol(s)
        return symbol_table[s]


def parse(source):
    reader = Reader(io.StringIO(source))
    return expand(reader.read())


def expand(x):
    if not isinstance(x, list):
        return x
    else:
        return [expand(item) for item in x]


class Reader(object):
    "Reads line of chars."
    tokenizer = r"""\s*(,@|[('`,)]|"(?:[\\].|[^\\"])*"|;.*|[^\s('"`,;)]*)(.*)"""
    eof = Symbol('#<eof-object>')  # Note: uninterned; can't be read

    def __init__(self, stream):
        self.stream = stream
        self.line = ''

    def next_token(self):
        while True:
            if self.line == '':
                self.line = self.stream.readline()
            if self.line == '':
                return self.eof
            token, self.line = re.match(self.tokenizer, self.line).groups()
            if token != '' and not token.startswith(';'):
                return token

    def read(self):
        def read_ahead(token):
            if '(' == token:
                l = []
                while True:
                    token = self.next_token()
                    if token == ')':
                        return l
                    else:
                        l.append(read_ahead(token))
            elif ')' == token:
                raise SyntaxError('unexpected )')
            elif token is self.eof:
                raise SyntaxError('unexpected EOF in list')
            else:
                return atom(token)

        # body of read:
        token1 = self.next_token()
        return self.eof if token1 is self.eof else read_ahead(token1)


def atom(token):
    if token[0] == '"':
        return token[1:-1]
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return Symbol.get(token)


def to_string(x):
    if isinstance(x, Symbol):
        return x
    elif isinstance(x, str):
        return '"%s"' % x.encode('string_escape').replace('"', r'\"')
    elif isinstance(x, list):
        return '(' + ' '.join(map(to_string, x)) + ')'
    return str(x)


global_env = Env().add_globals({
    '+': op.add,
    '-': op.sub,
    '*': op.mul,
    '/': op.truediv
})


def leval(x, env=global_env):
    if isinstance(x, map):
        x = list(x)
    if isinstance(x, Symbol):
        return env.find(x)[x]
    elif not isinstance(x, list):
        return x
    exps = [leval(exp, env) for exp in x]
    proc = exps.pop(0)
    return proc(*exps)


def evaluate(expr, env=global_env):
    return leval(parse(expr), env=env)
