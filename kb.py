############################################ kb: Knowledge Base engine in Python
########################### (c) Dmitry Ponyatov <<dponyatov@gmail.com>> 2020 MIT
######################################### github: https://github.com/ponyatov/kb

def comment(text, width=80):
    print('#' * (width - len(text) - 1) + ' ' + text)
# comment('computation', 60)


################################################################# system modules

import os, sys
import pytest

############################################################# object graph types

################################################################ base node class

class Object:

    def __init__(self, V):
        # type/class tag
        self.type = self.__class__.__name__.lower()
        # scalar value
        self.val = V
        # attributes = associative array
        self.slot = {}
        # nested elements = vector = stack
        self.nest = []
        # unical storage id
        self.sid = id(self)

    ################################################## text dump

    def __repr__(self): return self.dump()

    ## special dump for tests
    def test(self): return self.dump(test=True)

    ## full tree dump
    def dump(self, depth=0, prefix='', test=False):
        # header
        tree = self.pad(depth) + self.head(prefix, test)
        # infinitive recustion on cycles
        if not depth:
            Object._dumped = []
        if self in Object._dumped:
            return tree + ' _/'
        else:
            Object._dumped.append(self)
        # slot{}s
        for i in self.slot:
            tree += self.slot[i].dump(depth + 1, prefix='%s = ' % i, test=test)
        # nest[]ed
        idx = 0
        for j in self.nest:
            tree += j.dump(depth + 1, prefix='%s = ' % idx, test=test)
            idx += 1
        # subgraph
        return tree

    ## <T:V> header
    def head(self, prefix='', test=False):
        header = '%s<%s:%s>' % (prefix, self.type, self._val())
        if test:
            return header
        else:
            return header + ' @%x' % self.sid

    ## tab padding
    def pad(self, depth):
        return '\n' + '\t' * depth

    ## .val formatting for dumps
    def _val(self):
        return '%s' % self.val

    ################################################## operators

    ## `A[key]`
    def __getitem__(self, key):
        return self.slot[key]

    ## `A[key] = B`
    def __setitem__(self, key, that):
        self.slot[key] = that
        return self

    ## `A << B -> A[B.type] = B`
    def __lshift__(self, that):
        return self.__setitem__(that.type, that)

    ## `A >> B -> A[B.val] = B`
    def __rshift__(self, that):
        return self.__setitem__(that.val, that)

    ## `A//B -> A.push(B)`
    def __floordiv__(self, that):
        self.nest.append(that)
        return self

    ########################################### stack operations

    ################################################ computation

    def eval(self, ctx):
        raise TypeError(Error('eval') // self // ctx)

    def apply(self, that, ctx):
        raise TypeError(Error('apply') // self // that // ctx)

class TestObject:

    def test_empty(self):
        assert(Object('').test() == '\n<object:>')

    def hello(self): return Object('Hello')
    def world(self): return Object('World')

    ## `Object` creation
    def test_hello(self):
        assert(self.hello().test() == '\n<object:Hello>')

    ## '//' operator
    def test_world(self):
        assert((self.hello() // self.world()).test()
               == '\n<object:Hello>\n\t0 = <object:World>')

    ## `<<` operator
    def test_left(self):
        assert((self.hello() << Object('left')).test()
               == '\n<object:Hello>\n\tobject = <object:left>')

    ## `>>` operator
    def test_right(self):
        assert((self.hello() >> Object('right')).test()
               == '\n<object:Hello>\n\tright = <object:right>')

    ## `A[key]=B` & `A[key]`
    def test_slots(self):
        # set slot
        hello = self.hello()
        hello['key'] = self.world()
        assert(hello.test()
               == '\n<object:Hello>\n\tkey = <object:World>')
        # get slot
        assert(hello['key'].test()
               == '\n<object:World>')

############################################################### error processing

class Error(Object):
    pass

##################################################################### primitives

class Primitive(Object):
    def eval(self, ctx): return self

class Symbol(Primitive):
    def eval(self, ctx): return ctx[self.val]

class String(Primitive):
    pass

class Number(Primitive):
    def __init__(self, V): Primitive.__init__(self, float(V))

class Integer(Number):
    def __init__(self, V): Primitive.__init__(self, int(V, 0x0A))

class Hex(Integer):
    def __init__(self, V): Primitive.__init__(self, int(V[2:], 0x10))
    def _val(self): return hex(self.val)

class Bin(Integer):
    def __init__(self, V): Primitive.__init__(self, int(V[2:], 0x02))
    def _val(self): return bin(self.val)


class TestPrimitive:

    def test_number(self):
        num = Number('-12.34')
        assert(num.val == -12.34)
        assert(num.test() == '\n<number:-12.34>')
        num = Number('-4e+5')
        assert(num.val == -4e+5)
        assert(num.test() == '\n<number:-400000.0>')

    def test_integer(self):
        num = Integer('-1234')
        assert(type(num.val) == int)
        assert(num.val == -1234)
        assert(num.test() == '\n<integer:-1234>')

    def test_hex(self):
        num = Hex('0xDeadBeef')
        assert(num.val == 0xDeadBeef)
        assert(num.test() == '\n<hex:0xdeadbeef>')

    def test_bin(self):
        num = Bin('0b1101')
        assert(num.val == 0b1101)
        assert(num.test() == '\n<bin:0b1101>')

###################################################################### container

class Container(Object):
    pass
class Vector(Container):
    pass
class Dict(Container):
    pass
class Stack(Container):
    pass
class Queue(Container):
    pass
class Set(Container):
    pass

######################################################################### active

class Active(Object):
    pass
class Block(Active, Vector):
    pass

class Op(Active):
    def eval(self, ctx):
        if self.val == '`':
            return self.nest[0]
        lvalue = self.nest[0].eval(ctx)
        rvalue = self.nest[1].eval(ctx)
        if self.val == '=':
            ctx[lvalue.val] = rvalue
            return rvalue
        elif self.val == '//':
            return lvalue // rvalue
        elif self.val == '<<':
            return lvalue << rvalue
        elif self.val == '>>':
            return lvalue >> rvalue
        elif self.val == ':':
            return lvalue.apply(rvalue, ctx)
        else:
            raise SyntaxError(self)

class Command(Active):
    def __init__(self, F):
        Active.__init__(self, F.__name__)
        self.fn = F

    def eval(self, ctx):
        return self.fn(ctx)

    def apply(self, that, ctx):
        return self.fn(that, ctx)

class VM(Active):
    pass


vm = VM('metaL')
vm << vm

########################################################################### meta

class Meta(Object):
    pass

class Class(Meta):
    def __init__(self, C):
        Meta.__init__(self, C.__name__.lower())
        self.cls = C

    def apply(self, that, ctx):
        return self.cls(that.val)

############################################################################# io

class IO(Object):
    pass
class File(IO):
    pass


vm >> Class(File)

############################################################################ net

class Net(IO):
    pass
class IP(Net, Primitive):
    pass

class Port(Net, Primitive):
    pass


vm >> Class(Port)

class URL(Net, Primitive):
    pass
class Email(Net, Primitive):
    pass

################################################################## web interface


import flask, flask_wtf, wtforms

class Web(Net):
    def eval(self, ctx):

        app = flask.Flask(self.val)
        app.config['SECRET_KEY'] = os.urandom(32)

        class CLI(flask_wtf.FlaskForm):
            pad = wtforms.TextAreaField('pad',
                                        render_kw={'rows': 5, 'autofocus': 'true'},)
            go = wtforms.SubmitField('GO: Ctrl+Enter')

        @app.route('/')
        def index():
            form = CLI()
            return flask.render_template('index.html', web=self, ctx=ctx, form=form)

        @app.route('/css.css')
        def css():
            return flask.Response(
                flask.render_template('css.css', web=self, ctx=ctx),
                mimetype='text/css')

        @app.route('/static/<path:path>')
        def statics(path):
            return app.send_static_file(path)

        app.run(
            host=ctx['IP'].val, port=ctx['PORT'].val,
            debug=True, extra_files=['kb.ini'])

def WEB(that, ctx):
    web = ctx['WEB'] = Web(that.val)
    web << ctx['IP'] << ctx['PORT'] << ctx['LOGO']
    return web.eval(ctx)


vm >> Command(WEB)

####################################################################### document

class Doc(Object):
    pass
class Font(Doc):
    pass
class Size(Doc):
    pass
class Color(Doc):
    pass

####################################################################### database


########################################################################## lexer

import ply.lex as lex

tokens = ['nl', 'lq', 'rq', 'lc', 'rc',
          'eq', 'tick', 'push', 'lshift', 'rshift', 'colon',
          'symbol', 'string',
          'number', 'integer', 'hex', 'bin',
          'url', 'email', 'ip',
          'end']

t_ignore = ' \t\r'
t_ignore_comment = r'\#.*'

states = (('str', 'exclusive'),)

t_str_ignore = ''

def t_str(t):
    r'\''
    t.lexer.push_state('str')
    t.lexer.string = ''
def t_str_string(t):
    r'\''
    t.lexer.pop_state()
    t.value = String(t.lexer.string)
    return t
def t_str_char(t):
    r'.'
    t.lexer.string += t.value

def t_nl(t):
    r'\n'
    t.lexer.lineno += 1
    return t


t_lq = r'\['
t_rq = r'\]'
t_lc = r'\{'
t_rc = r'\}'

def t_hex(t):
    r'0x[0-9a-fA-F]+'
    t.value = Hex(t.value)
    return t
def t_bin(t):
    r'0b[01]+'
    t.value = Bin(t.value)
    return t

def t_tick(t):
    r'`'
    t.value = Op(t.value)
    return t
def t_colon(t):
    r':'
    t.value = Op(t.value)
    return t
def t_eq(t):
    r'='
    t.value = Op(t.value)
    return t
def t_push(t):
    r'//'
    t.value = Op(t.value)
    return t
def t_lshift(t):
    r'<<'
    t.value = Op(t.value)
    return t
def t_rshift(t):
    r'>>'
    t.value = Op(t.value)
    return t

def t_end(t):
    r'\.end'
    return t

def t_url(t):
    r'https?://[^ \t\r\n]+'
    t.value = URL(t.value)
    return t
def t_email(t):
    r'[a-z]+@[^ \t\r\n]+'
    t.value = Email(t.value)
    return t
def t_ip(t):
    r'([0-9]{1,3}\.){3}[0-9]{1,3}'
    t.value = IP(t.value)
    return t

def t_symbol(t):
    r'[^ \t\r\n\#\{\}\[\]:]+'
    t.value = Symbol(t.value)
    return t

def t_ANY_error(t): raise SyntaxError(t)


lexer = lex.lex()

######################################################################### parser

import ply.yacc as yacc

precedence = (
    ('right', 'eq'),
    ('left', 'push'),
    ('left', 'lshift', 'rshift'),
    ('nonassoc', 'tick', 'colon'),
)


def p_REPL_none(p):
    ' REPL : '
    pass
def p_REPL_nl(p):
    ' REPL : REPL nl '
    pass
def p_REPL_recursuve(p):
    ' REPL : REPL ex '
    print(p[2])
    print(p[2].eval(vm))
    # print(vm)
    print('-' * 80)
def p_REPL_end(p):
    r' REPL : REPL end '
    sys.exit(0)

def p_ex_symbol(p):
    ' ex : symbol '
    p[0] = p[1]
def p_ex_string(p):
    ' ex : string '
    p[0] = p[1]
# def p_ex_number(p):
#     ' ex : number '
#     p[0] = p[1]
# def p_ex_integer(p):
#     ' ex : integer '
#     p[0] = p[1]
# def p_ex_hex(p):
#     ' ex : hex '
#     p[0] = p[1]
# def p_ex_bin(p):
#     ' ex : bin '
#     p[0] = p[1]
def p_ex_url(p):
    ' ex : url '
    p[0] = p[1]
def p_ex_email(p):
    ' ex : email '
    p[0] = p[1]
def p_ex_ip(p):
    ' ex : ip '
    p[0] = p[1]

def p_ex_tick(p):
    ' ex : tick ex '
    p[0] = p[1] // p[2]
def p_ex_colon_sym(p):
    ' ex : symbol colon symbol '
    p[0] = p[2] // p[1] // (Op('`') // p[3])
def p_ex_eq(p):
    ' ex : symbol eq ex '
    p[0] = p[2] // (Op('`') // p[1]) // p[3]
def p_ex_push(p):
    ' ex : ex push ex '
    p[0] = p[2] // p[1] // p[3]
def p_ex_lshift(p):
    ' ex : ex lshift ex '
    p[0] = p[2] // p[1] // p[3]
def p_ex_rshift(p):
    ' ex : ex rshift ex '
    p[0] = p[2] // p[1] // p[3]

# def p_vector_named(p):
#     ' ex : symbol lq vector rq '
#     p[0] = p[3]
#     p[0].val = p[1].val
# def p_vector(p):
#     ' ex : lq vector rq '
#     p[0] = p[2]
# def p_vector_none(p):
#     ' vector : '
#     p[0] = Vector('')
# def p_vector_ex(p):
#     ' vector : vector ex '
#     p[0] = p[1] // p[2]

# def p_block_named(p):
#     ' ex : symbol lc block rc '
#     p[0] = p[3]
#     p[0].val = p[1].val
# def p_block(p):
#     ' ex : lc block rc '
#     p[0] = p[2]
# def p_block_none(p):
#     ' block : '
#     p[0] = Block('')
# def p_block_ex(p):
#     ' block : block ex '
#     p[0] = p[1] // p[2]

def p_error(p): raise SyntaxError(p)


parser = yacc.yacc(debug=False, write_tables=False)

#################################################################### system init

if __name__ == '__main__':
    for srcfile in sys.argv[1:]:
        with open(srcfile) as src:
            parser.parse(src.read())
