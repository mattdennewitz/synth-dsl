"""
Defines a grammar for expression module i/o routing and configuration.

Grammar:

Module := Name '{' [newline] Config-line | Routing-line [newline] '}'
Config-line := Key ':' Value
Routing-line := Source '>' Destination ['|' Destination]+
Name := alphas+
Source := alphas+
Destination := alphas+
Key := alphas+
Value := alphas+
alphas+ := [A-z-_.&]
"""

from pyparsing import *


__all__ = ("grammar",)

alphas_punc = alphanums + "-_.&"

ConfigLine = Word(alphas_punc) + ":" + (Word(alphas_punc) | QuotedString('"'))
RoutingLine = (
    Word(alphas_punc) + ">" + Group(delimitedList(Word(alphas_punc), delim="&"))
)


Module = (
    Group(
        Word(alphas_punc)
        + Literal("{").suppress()
        + Group(
            ZeroOrMore(Group((ConfigLine | RoutingLine) & Optional(QuotedString('"'))))
        )
        + Literal("}").suppress()
    )
).ignore("#" + restOfLine)

grammar = OneOrMore(Module)
