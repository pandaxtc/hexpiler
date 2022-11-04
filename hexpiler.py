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

import argparse
import logging
from collections import ChainMap
from pprint import pformat


from lark.lark import Lark
from lark.lexer import Token
from lark.tree import ParseTree
from pygments import highlight
from pygments.lexers.mcfunction import MCFunctionLexer
from pygments.formatters import TerminalTrueColorFormatter

from builtin_patterns import builtin_patterns
from util import number_to_pattern, patterns_to_give_command

GRAMMAR = open("hexlisp.grammar").read()

# Defined variables. Mutates over the course of an evaluation.
symbols = ChainMap(builtin_patterns)


def eval_expression(node: ParseTree | Token):
    """
    Evaluates expressions.
    """
    out = []

    if isinstance(node, Token):
        match node.type:
            case "SIGNED_NUMBER":
                out.append(number_to_pattern(float(node)))
            case "SYMBOL":
                if node == "self":
                    out.append(builtin_patterns["get_caster"])
                else:
                    pass
    else:
        match node.data:
            case "literal":
                out.extend(eval_expression(node.children[0]))
            case "invocation":
                out.extend(eval_invocation(node))
            case "list":
                out.extend(eval_list(node))
            case "vector":
                out.extend(eval_vector(node))
            case _:
                assert False

    return out


def eval_invocation(node: ParseTree):
    """
    Evaluate an invocation. Expects a symbol representing a function
    at index 0, with argument expressions after.

    Special cases are defined for constructs like if/else, for, etc.
    """
    fn, *args = node.children

    match fn:
        case "if":
            """
            (if cond then-expr else-expr)

            Conditionals are constructed according to:

                <condition>
                identity
                {
                    patterns if true (1)
                }
                conjunction
                {
                    patterns if false (0), aka else
                }
                disjunction
                hermes

            In the absence of an else-expr, an empty list will be evaluated
            by hermes.
            """
            cond = eval_expression(args[0])

            then_expr = [
                builtin_patterns["open_paren"],
                *eval_expression(args[1]),
                builtin_patterns["close_paren"],
            ]

            else_expr = (
                [
                    builtin_patterns["open_paren"],
                    *eval_expression(args[2]),
                    builtin_patterns["close_paren"],
                ]
                if len(args) > 2
                else [builtin_patterns["empty_list"]]
            )

            return [
                *cond,
                builtin_patterns["identity"],
                *then_expr,
                builtin_patterns["and"],
                *else_expr,
                builtin_patterns["or"],
                builtin_patterns["eval"],
            ]

        case _:
            """
            Standard function invocation.
            """
            out = []

            for arg in args:
                out.extend(eval_expression(arg))

            out.append(builtin_patterns[fn])

            return out


def eval_list(node: ParseTree):
    """
    Evaluate a list. Expects a list of expressions.
    """
    out = []

    for el in node.children:
        out.extend(eval_expression(el))

    out.append(len(node.children))
    out.append(builtin_patterns["last_n_list"])

    return out


def eval_vector(node: ParseTree):
    """
    Evaluates a vector. Expects 3 expressions.
    """
    assert len(node.children) == 3

    out = []

    for el in node.children:
        out.extend(eval_expression(el))

    out.append(builtin_patterns["construct_vec"])

    return out


def main():
    parser = argparse.ArgumentParser(
        prog="hexpiler",
        description="A hexlisp transpiler for the Hex Casting mod. Heavy WIP.",
    )
    parser.add_argument("file", help="Input file.")
    parser.add_argument("-d", "--debug", action="store_true", help="Print debug info.")
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    l = Lark(GRAMMAR)

    t = l.parse(open(args.file).read())

    logging.debug(f"Parse tree: \n{t.pretty()}")

    out = eval_expression(t)
    logging.debug(f"Final pattern list: \n{pformat(out)}")

    print(
        highlight(
            patterns_to_give_command(out),
            MCFunctionLexer(),
            TerminalTrueColorFormatter(),
        )
    )


if __name__ == "__main__":
    main()
