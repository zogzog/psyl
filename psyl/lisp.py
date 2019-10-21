# Lisp Interpreter in Python
# inpired from See http://norvig.com/lispy2.html
import re
import io


class Env(dict):

    def find(self, var):
        if var in self:
            return self[var]
        raise LookupError(var)


class Keyword(str):
    pass


class Symbol(Keyword):

    @staticmethod
    def get(s, symbol_table={}):
        "Find or create unique Symbol entry for str s in symbol table."
        if s not in symbol_table:
            symbol_table[s] = Symbol(s)
        return symbol_table[s]


def atom(token):
    if token == '#t': return True
    if token == '#f': return False
    if token[0] == '"':
        return token[1:-1]
    if token.startswith('#:'):
        return Keyword(token[2:])

    for trytype in (int, float):
        try:
            return trytype(token)
        except ValueError:
            continue

    return Symbol.get(token)


def parse(source):
    reader = Reader(io.StringIO(source))
    return expand(reader.read())


def expand(x):
    if not isinstance(x, list):
        return x
    else:
        return [expand(item) for item in x]


def serialize(tree):
    """ transform a plain python tree made of nested lists
    and atoms into a parseable expression
    """
    expr = []
    for node in tree:
        if isinstance(node, list):
            expr.append(serialize(node))
        elif isinstance(node, Symbol):
            expr.append(node)
        elif isinstance(node, Keyword):
            expr.append(f'#:{node}')
        elif isinstance(node, str):
            expr.append(f'"{node}"')
        elif isinstance(node, bool):
            if node:
                expr.append('#t')
            else:
                expr.append('#f')
        elif isinstance(node, (int, float)):
            expr.append(str(node))

    return f'({" ".join(expr)})'


class Reader(object):
    "Reads line of chars."
    tokenizer = re.compile(
        r"""\s*(,@|[('`,)]|"(?:[\\].|[^\\"])*"|;.*|[^\s('"`,;)]*)(.*)"""
    )
    eof = Symbol('#<eof-object>')  # Note: uninterned; can't be read

    def __init__(self, stream):
        self.stream = stream
        self.line = ''

    def next_token(self):
        prevtoken = None
        while True:
            if self.line == '':
                self.line = self.stream.readline()
            if self.line == '':
                return self.eof
            token, self.line = self.tokenizer.match(self.line).groups()
            if token != '' and not token.startswith(';'):
                return token
            if prevtoken == token:
                raise SyntaxError(f'{self.line} (did you forget an opening quote ?)')
            prevtoken = token

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


def buildargs(expr_args):
    args = []
    kw = {}
    lastarg = None
    for arg in expr_args:
        if isinstance(lastarg, Keyword):
            assert not isinstance(arg, Keyword)
            kw[lastarg] = arg
            lastarg = arg
            continue
        if isinstance(arg, Keyword):
            lastarg = arg
            continue
        else:
            args.append(arg)
    return args, kw


def expreval(tree, env):
    if isinstance(tree, map):
        tree = list(tree)
    if isinstance(tree, Symbol):
        return env.find(tree)
    elif not isinstance(tree, list):
        return tree
    exps = [expreval(exp, env) for exp in tree]
    proc = exps[0]
    posargs, kwargs = buildargs(exps[1:])
    return proc(*posargs, **kwargs)


def evaluate(expr, env):
    return expreval(parse(expr), env=env)
