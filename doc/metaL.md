# [metaL]anguage

The system uses its own programming language `metaL` targetted especially for
handy graph transformations.

This expression in [metaL](metaL.md)
```
`Hello // `World << `left >> `right
```
will be parsed to this like AST (in form of object graph)
```
<operator://> @7f42dad60550
	0 = <operator:`> @7f42dad60390
		0 = <symbol:Hello> @7f42dad60470
	1 = <operator:>>> @7f42dad60940
		0 = <operator:<<> @7f42dad60780
			0 = <operator:`> @7f42dad605f8
				0 = <symbol:World> @7f42dad606a0
			1 = <operator:`> @7f42dad607b8
				0 = <symbol:left> @7f42dad60860
		1 = <operator:`> @7f42dad60400
			0 = <symbol:right> @7f42dad609e8
```
and then evaluated to
```
<symbol:Hello> @7f42dad60470
	0 = <symbol:World> @7f42dad606a0
		symbol = <symbol:left> @7f42dad60860
		right = <symbol:right> @7f42dad609e8
```

The `metaL` language was specially designed to work both with parsed and
evaluated data. It differs from many other programming languages, as you can
work with source code the same way as with any other data that exists in a
system. To do it in a uniform way, the data model was selected to be a good
representation form for program source code and any other structured data.

## Object Graph

Every element in a system is a unified object which can hold both scalar value,
attributes, and ordered subelements (subgraphs).

```
class Object:
    def __init__(self,V):
        # type/class tag
        self.type = self.__class__.__name__.lower()
        # scalar value
        self.val  = V
        # attributes = string-keyed array = environment
        self.slot = {}
        # nested elements = ordered vector = stack
        self.nest = []
        # unique object id for persistent storage
        self.sid  = id(self)
```

**Every object is universal** as it can be used as a single value, string-keyed
associative array, vector, and stack. As it has both environment and stack
storage facilities, any object can be used as a computation context for
expression (graph) evaluations. At a same time, any three objects can be used in
the evaluation & apply operations:

```
class Primitive(Object):
    # evaluate object `self` in the computation context `ctx`
    def eval(self,ctx): return self
class Active(Object):
    # apply `self' to object `that` as a function in context `ctx`
    def apply(self,that,ctx): return ...
```

So, **any object** not only an **universal data** container but also can act as
a **function or computation context**.

## Comments

```
# line comment
```

## Operators

### ` quote

Prefix any expression with ` to prevent from evaluation: leave parsed AST as is.

```
`symbol
`(expression)
```

### Structure (graph) definition

#### `//` push

```
`A // `B -> A.push(B)
```

#### `<<` store to type-named slot

```
A << B -> A[B.type] = B
```

#### `>>` store to val-named slot

```
A >> B -> A[B.val] = B
```

## Debug

To show a global virtual machine state you can just evaluate and print the `vm`
expression which maps to a global symbol in the VM to itself.

```
?> vm
--------------------------------------------------------------------------------

<symbol:vm> @7f8dd27ef898

<vm:metaL> @7f8dd3cb3940
	vm = <vm:metaL> @7f8dd3cb3940 _/
	MODULE = <symbol:kb> @7f8dd27ef630
	TITLE = <string:Knowledge Base engine /multilingual/> @7f8dd27ef550
	AUTHOR = <vector:> @7f8dd27ef710
		0 = <string:Dmitry Ponyatov> @7f8dd27ef7b8
		1 = <block:> @7f8dd340f9b0
			0 = <symbol:email:> @7f8dd27ef908
			1 = <email:dponyatov@gmail.com> @7f8dd27ef9e8
	LICENCE = <symbol:MIT> @7f8dd27efa58
	GOTHUB = <url:https://github.com/ponyatov/kb> @7f8dd27ef470
	LOGO = <symbol:static/logo.png> @7f8dd27ef860
```
