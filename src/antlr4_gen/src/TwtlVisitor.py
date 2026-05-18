# Generated from src/Twtl.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .TwtlParser import TwtlParser
else:
    from TwtlParser import TwtlParser

# This class defines a complete generic visitor for a parse tree produced by TwtlParser.

class TwtlVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by TwtlParser#prog.
    def visitProg(self, ctx:TwtlParser.ProgContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TwtlParser#formula.
    def visitFormula(self, ctx:TwtlParser.FormulaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TwtlParser#disjunction.
    def visitDisjunction(self, ctx:TwtlParser.DisjunctionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TwtlParser#conjunction.
    def visitConjunction(self, ctx:TwtlParser.ConjunctionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TwtlParser#concatenation.
    def visitConcatenation(self, ctx:TwtlParser.ConcatenationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TwtlParser#holdProp.
    def visitHoldProp(self, ctx:TwtlParser.HoldPropContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TwtlParser#holdTrue.
    def visitHoldTrue(self, ctx:TwtlParser.HoldTrueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TwtlParser#holdFalse.
    def visitHoldFalse(self, ctx:TwtlParser.HoldFalseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TwtlParser#holdNegProp.
    def visitHoldNegProp(self, ctx:TwtlParser.HoldNegPropContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TwtlParser#eventuallyExpr.
    def visitEventuallyExpr(self, ctx:TwtlParser.EventuallyExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TwtlParser#withinExpr.
    def visitWithinExpr(self, ctx:TwtlParser.WithinExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TwtlParser#temporalNegation.
    def visitTemporalNegation(self, ctx:TwtlParser.TemporalNegationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TwtlParser#negation.
    def visitNegation(self, ctx:TwtlParser.NegationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by TwtlParser#atom.
    def visitAtom(self, ctx:TwtlParser.AtomContext):
        return self.visitChildren(ctx)



del TwtlParser