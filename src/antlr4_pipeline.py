"""ANTLR4-based parsing and evaluation pipeline for TWTL."""

from __future__ import annotations

from dataclasses import dataclass

from antlr4 import CommonTokenStream, InputStream
from antlr4.error.ErrorListener import ErrorListener

from antlr4_gen.src.TwtlLexer import TwtlLexer
from antlr4_gen.src.TwtlParser import TwtlParser
from antlr4_gen.src.TwtlVisitor import TwtlVisitor
from dfa import accept_prop, complement, concatenation, hold, intersection, union, within


class _RaisingErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise ValueError(f"Invalid TWTL formula at {line}:{column}: {msg}")


@dataclass(frozen=True)
class ParsedFormula:
    tree: TwtlParser.FormulaContext
    alphabet: set[str]


class _NormVisitor(TwtlVisitor):
    def visitFormula(self, ctx):
        return self.visit(ctx.disjunction())

    def visitDisjunction(self, ctx):
        values = [self.visit(node) for node in ctx.conjunction()]
        acc = values[0]
        for value in values[1:]:
            acc = (min(acc[0], value[0]), max(acc[1], value[1]))
        return acc

    def visitConjunction(self, ctx):
        values = [self.visit(node) for node in ctx.concatenation()]
        acc = values[0]
        for value in values[1:]:
            acc = (max(acc[0], value[0]), max(acc[1], value[1]))
        return acc

    def visitConcatenation(self, ctx):
        values = [self.visit(node) for node in ctx.temporal()]
        acc = values[0]
        for value in values[1:]:
            acc = (acc[0] + value[0] + 1, acc[1] + value[1] + 1)
        return acc

    def visitHoldProp(self, ctx):
        duration = int(ctx.INT().getText())
        return (duration, duration)

    def visitHoldNegProp(self, ctx):
        duration = int(ctx.INT().getText())
        return (duration, duration)

    def visitWithinExpr(self, ctx):
        phi = self.visit(ctx.formula())
        low = int(ctx.INT(0).getText())
        high = int(ctx.INT(1).getText()) if len(ctx.INT()) > 1 else None
        if high is not None and phi[1] > high - low:
            raise ValueError("Within operator deadline is invalid!")
        return (low + phi[0], high)

    def visitTemporalNegation(self, ctx):
        return self.visit(ctx.negation())

    def visitNegation(self, ctx):
        return self.visit(ctx.atom())

    def visitAtom(self, ctx):
        if ctx.formula() is not None:
            return self.visit(ctx.formula())
        return (0, 0)


class _DfaVisitor(TwtlVisitor):
    def __init__(self, alphabet: set[str]):
        super().__init__()
        self.props = alphabet

    def visitFormula(self, ctx):
        return self.visit(ctx.disjunction())

    def visitDisjunction(self, ctx):
        values = [self.visit(node) for node in ctx.conjunction()]
        acc = values[0]
        for value in values[1:]:
            acc = union(acc, value)
        return acc

    def visitConjunction(self, ctx):
        values = [self.visit(node) for node in ctx.concatenation()]
        acc = values[0]
        for value in values[1:]:
            acc = intersection(acc, value)
        return acc

    def visitConcatenation(self, ctx):
        values = [self.visit(node) for node in ctx.temporal()]
        acc = values[0]
        for value in values[1:]:
            acc = concatenation(acc, value)
        return acc

    def visitHoldProp(self, ctx):
        return hold(self.props, ctx.PROP().getText(), int(ctx.INT().getText()), negation=False)

    def visitHoldNegProp(self, ctx):
        return hold(self.props, ctx.PROP().getText(), int(ctx.INT().getText()), negation=True)

    def visitWithinExpr(self, ctx):
        return within(self.visit(ctx.formula()), int(ctx.INT(0).getText()), int(ctx.INT(1).getText()) if len(ctx.INT()) > 1 else None)

    def visitTemporalNegation(self, ctx):
        return self.visit(ctx.negation())

    def visitNegation(self, ctx):
        dfa = self.visit(ctx.atom())
        return complement(dfa) if ctx.NOT() is not None else dfa

    def visitAtom(self, ctx):
        if ctx.PROP() is not None:
            return accept_prop(self.props, prop=ctx.PROP().getText())
        if ctx.TRUE() is not None:
            return accept_prop(self.props, boolean=True)
        if ctx.FALSE() is not None:
            return accept_prop(self.props, boolean=False)
        return self.visit(ctx.formula())


def parse_formula(formula: str) -> ParsedFormula:
    lexer = TwtlLexer(InputStream(formula))
    lexer.removeErrorListeners()
    lexer.addErrorListener(_RaisingErrorListener())

    tokens = CommonTokenStream(lexer)
    tokens.fill()
    alphabet = {tok.text for tok in tokens.tokens if tok.type == TwtlLexer.PROP}

    parser = TwtlParser(tokens)
    parser.removeErrorListeners()
    parser.addErrorListener(_RaisingErrorListener())

    prog = parser.prog()
    return ParsedFormula(tree=prog.formula(), alphabet=alphabet)


def evaluate_norm(tree: TwtlParser.FormulaContext) -> tuple[int, int]:
    return _NormVisitor().visit(tree)


def evaluate_dfa(tree: TwtlParser.FormulaContext, alphabet: set[str]):
    return _DfaVisitor(alphabet).visit(tree)
