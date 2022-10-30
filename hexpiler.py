"""
hexpiler

A parser and transpiler for a Lisp-based DSL that compiles to Hex 
Casting patterns. Performs naive transpilation without any checks.

Check hex.grammar for grammar.

## Example ##

(break_block 
    (- (pos self) <0,-1,0>)

(teleport
    (raycast/entity
        (get_entity_look self) 
        (get_entity_pos self)) 
    <0, 100, 0>)

Named variables (aka memoized values) are accomplished using a list in
the ravenmind.
"""

from collections import ChainMap
from pprint import pprint

from lark.lark import Lark
from lark.lexer import Token
from lark.tree import ParseTree

from builtin_patterns import builtin_patterns

l = Lark(open("hex.lark"))

# Test spell to teleport a raycast entity very high
t = l.parse(
    """
    (teleport
        (raycast/entity
            (get_entity_look self) 
            (get_entity_pos self)) 
        <0, 100, 0>)
    """
)

print(t.pretty())
print(t)

symbols = ChainMap(builtin_patterns)

out = []


def eval(node: ParseTree | Token):
    """
    Evaluates expressions.
    """
    if isinstance(node, Token):
        if node == "self":
            out.append(builtin_patterns["get_caster"])
        else:
            match node.type:
                case _:
                    out.append(str(node))
        return

    match node.data:
        case "literal":
            eval(node.children[0])
        case "invocation":
            eval_invocation(node)
        case "list":
            eval_list(node)
        case "vector":
            eval_vector(node)
        case _:
            assert False


def eval_invocation(node: ParseTree):
    """
    Evaluate an invocation. Expects a symbol representing a function
    at index 0, with argument expressions after.
    """
    fn, *args = node.children
    for arg in args:
        eval(arg)

    out.append(builtin_patterns[fn])


def eval_list(node: ParseTree):
    """
    Evaluate a list. Expects a list of expressions.
    """
    for el in node.children:
        eval(el)

    out.append(len(node.children))
    out.append(builtin_patterns["last_n_list"])


def eval_vector(node: ParseTree):
    """
    Evaluates a vector. Expects 3 expressions.
    """
    assert len(node.children) == 3
    for el in node.children:
        eval(el)

    out.append(3)
    out.append("MAKE_VECTOR")


eval(t)
pprint(out)
