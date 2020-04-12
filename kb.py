############################################ kb: Knowledge Base engine in Python
########################### (c) Dmitry Ponyatov <<dponyatov@gmail.com>> 2020 MIT
######################################### github: https://github.com/ponyatov/kb

def comment(text, width=80):
    print('#' * (width - len(text) - 1) + ' ' + text)
# comment('document')


######################################################################## modules


import os, sys
import pytest

############################################################# object graph types

## base object graph node class
class Object:

    def __init__(self, V):
        ## type/class tag
        self.type = self.__class__.__name__.lower()
        ## scalar value
        self.val = V
        ## attributes = associative array
        self.slot = {}
        ## nested elements = vector = stack
        self.nest = []

    ## @name dump

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
            return header + ' @%x' % id(self)

    ## tab padding
    def pad(self, depth):
        return '\n' + '\t' * depth

    ## .val formatting for dumps
    def _val(self):
        return '%s' % self.val

    ## @name operators

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

    ## @name evaluate graph

    def eval(self, ctx): return self


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


###################################################################### primitive


class Primitive(Object):
    pass
class Symbol(Primitive):
    pass
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
        if self.val == '=':
            ctx[self.nest[0].val] = self.nest[1]
            return self.nest[1]
        return Active.eval(self, ctx)

class Command(Active):
    pass
class VM(Active):
    pass


vm = VM('metaL')
vm << vm

########################################################################### meta


############################################################################# io

class IO(Object):
    pass

############################################################################ net

class Net(IO):
    pass
class IP(Net):
    pass
class Port(Net):
    pass

################################################################## web interface


import flask

class Web(Net):
    pass

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
          'eq',
          'symbol', 'string',
          'number', 'integer', 'hex', 'bin',
          'end']

t_ignore = ' \t\r'
t_ignore_comment = r'\#.*'

states = (('str', 'exclusive'),)

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

def t_eq(t):
    r'\='
    t.value = Op(t.value)
    return t

def t_end(t):
    r'\.end'
    return t

def t_symbol(t):
    r'[^ \t\r\n\#\{\}\[\]]+'
    t.value = Symbol(t.value)
    return t

def t_ANY_error(t): raise SyntaxError(t)


lexer = lex.lex()

######################################################################### parser

import ply.yacc as yacc

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
    print(vm)
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
def p_ex_number(p):
    ' ex : number '
    p[0] = p[1]
def p_ex_integer(p):
    ' ex : integer '
    p[0] = p[1]
def p_ex_hex(p):
    ' ex : hex '
    p[0] = p[1]
def p_ex_bin(p):
    ' ex : bin '
    p[0] = p[1]

def p_ex_eq(p):
    r' ex : symbol eq ex '
    p[0] = p[2] // p[1] // p[3]

def p_vector_named(p):
    ' ex : symbol lq vector rq '
    p[0] = p[3]
    p[0].val = p[1].val
def p_vector(p):
    ' ex : lq vector rq '
    p[0] = p[2]
def p_vector_none(p):
    ' vector : '
    p[0] = Vector('')
def p_vector_ex(p):
    ' vector : vector ex '
    p[0] = p[1] // p[2]

def p_block_named(p):
    ' ex : symbol lc block rc '
    p[0] = p[3]
    p[0].val = p[1].val
def p_block(p):
    ' ex : lc block rc '
    p[0] = p[2]
def p_block_none(p):
    ' block : '
    p[0] = Block('')
def p_block_ex(p):
    ' block : block ex '
    p[0] = p[1] // p[2]

def p_error(p): raise SyntaxError(p)


parser = yacc.yacc(debug=False, write_tables=False)

#################################################################### system init

if __name__ == '__main__':
    print(vm)
    for srcfile in sys.argv[1:]:
        print('%s:' % srcfile)
        with open(srcfile) as src:
            parser.parse(src.read())
