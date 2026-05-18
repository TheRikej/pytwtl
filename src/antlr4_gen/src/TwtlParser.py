# Generated from src/Twtl.g4 by ANTLR 4.13.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,18,99,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,1,0,1,0,1,0,1,1,1,1,1,2,1,2,1,2,5,2,25,8,2,10,2,12,2,28,
        9,2,1,3,1,3,1,3,5,3,33,8,3,10,3,12,3,36,9,3,1,4,1,4,1,4,5,4,41,8,
        4,10,4,12,4,44,9,4,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,
        5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,5,1,
        5,1,5,1,5,3,5,76,8,5,1,5,1,5,1,5,3,5,81,8,5,1,6,3,6,84,8,6,1,6,1,
        6,1,6,1,6,3,6,90,8,6,1,6,3,6,93,8,6,1,7,1,7,1,7,1,7,1,7,0,0,8,0,
        2,4,6,8,10,12,14,0,0,105,0,16,1,0,0,0,2,19,1,0,0,0,4,21,1,0,0,0,
        6,29,1,0,0,0,8,37,1,0,0,0,10,80,1,0,0,0,12,92,1,0,0,0,14,94,1,0,
        0,0,16,17,3,2,1,0,17,18,5,0,0,1,18,1,1,0,0,0,19,20,3,4,2,0,20,3,
        1,0,0,0,21,26,3,6,3,0,22,23,5,2,0,0,23,25,3,6,3,0,24,22,1,0,0,0,
        25,28,1,0,0,0,26,24,1,0,0,0,26,27,1,0,0,0,27,5,1,0,0,0,28,26,1,0,
        0,0,29,34,3,8,4,0,30,31,5,1,0,0,31,33,3,8,4,0,32,30,1,0,0,0,33,36,
        1,0,0,0,34,32,1,0,0,0,34,35,1,0,0,0,35,7,1,0,0,0,36,34,1,0,0,0,37,
        42,3,10,5,0,38,39,5,6,0,0,39,41,3,10,5,0,40,38,1,0,0,0,41,44,1,0,
        0,0,42,40,1,0,0,0,42,43,1,0,0,0,43,9,1,0,0,0,44,42,1,0,0,0,45,46,
        5,4,0,0,46,47,5,7,0,0,47,48,5,15,0,0,48,81,5,16,0,0,49,50,5,4,0,
        0,50,51,5,7,0,0,51,52,5,15,0,0,52,81,5,13,0,0,53,54,5,4,0,0,54,55,
        5,7,0,0,55,56,5,15,0,0,56,81,5,14,0,0,57,58,5,4,0,0,58,59,5,7,0,
        0,59,60,5,15,0,0,60,61,5,3,0,0,61,81,5,16,0,0,62,63,5,5,0,0,63,64,
        5,10,0,0,64,65,3,2,1,0,65,66,5,11,0,0,66,81,1,0,0,0,67,68,5,8,0,
        0,68,69,3,2,1,0,69,70,5,9,0,0,70,71,5,7,0,0,71,72,5,8,0,0,72,75,
        5,15,0,0,73,74,5,12,0,0,74,76,5,15,0,0,75,73,1,0,0,0,75,76,1,0,0,
        0,76,77,1,0,0,0,77,78,5,9,0,0,78,81,1,0,0,0,79,81,3,12,6,0,80,45,
        1,0,0,0,80,49,1,0,0,0,80,53,1,0,0,0,80,57,1,0,0,0,80,62,1,0,0,0,
        80,67,1,0,0,0,80,79,1,0,0,0,81,11,1,0,0,0,82,84,5,3,0,0,83,82,1,
        0,0,0,83,84,1,0,0,0,84,85,1,0,0,0,85,93,5,16,0,0,86,93,5,13,0,0,
        87,93,5,14,0,0,88,90,5,3,0,0,89,88,1,0,0,0,89,90,1,0,0,0,90,91,1,
        0,0,0,91,93,3,14,7,0,92,83,1,0,0,0,92,86,1,0,0,0,92,87,1,0,0,0,92,
        89,1,0,0,0,93,13,1,0,0,0,94,95,5,10,0,0,95,96,3,2,1,0,96,97,5,11,
        0,0,97,15,1,0,0,0,8,26,34,42,75,80,83,89,92
    ]

class TwtlParser ( Parser ):

    grammarFileName = "Twtl.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'&'", "'|'", "'!'", "'H'", "'F'", "'*'", 
                     "'^'", "'['", "']'", "'('", "')'", "','" ]

    symbolicNames = [ "<INVALID>", "AND", "OR", "NOT", "HOLD", "EVENTUALLY", 
                      "CONCAT", "CARET", "LBRACK", "RBRACK", "LPAREN", "RPAREN", 
                      "COMMA", "TRUE", "FALSE", "INT", "PROP", "LINECMT", 
                      "WS" ]

    RULE_prog = 0
    RULE_formula = 1
    RULE_disjunction = 2
    RULE_conjunction = 3
    RULE_concatenation = 4
    RULE_temporal = 5
    RULE_negation = 6
    RULE_atom = 7

    ruleNames =  [ "prog", "formula", "disjunction", "conjunction", "concatenation", 
                   "temporal", "negation", "atom" ]

    EOF = Token.EOF
    AND=1
    OR=2
    NOT=3
    HOLD=4
    EVENTUALLY=5
    CONCAT=6
    CARET=7
    LBRACK=8
    RBRACK=9
    LPAREN=10
    RPAREN=11
    COMMA=12
    TRUE=13
    FALSE=14
    INT=15
    PROP=16
    LINECMT=17
    WS=18

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class ProgContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def formula(self):
            return self.getTypedRuleContext(TwtlParser.FormulaContext,0)


        def EOF(self):
            return self.getToken(TwtlParser.EOF, 0)

        def getRuleIndex(self):
            return TwtlParser.RULE_prog

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitProg" ):
                return visitor.visitProg(self)
            else:
                return visitor.visitChildren(self)




    def prog(self):

        localctx = TwtlParser.ProgContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_prog)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 16
            self.formula()
            self.state = 17
            self.match(TwtlParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FormulaContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def disjunction(self):
            return self.getTypedRuleContext(TwtlParser.DisjunctionContext,0)


        def getRuleIndex(self):
            return TwtlParser.RULE_formula

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFormula" ):
                return visitor.visitFormula(self)
            else:
                return visitor.visitChildren(self)




    def formula(self):

        localctx = TwtlParser.FormulaContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_formula)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 19
            self.disjunction()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DisjunctionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def conjunction(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(TwtlParser.ConjunctionContext)
            else:
                return self.getTypedRuleContext(TwtlParser.ConjunctionContext,i)


        def OR(self, i:int=None):
            if i is None:
                return self.getTokens(TwtlParser.OR)
            else:
                return self.getToken(TwtlParser.OR, i)

        def getRuleIndex(self):
            return TwtlParser.RULE_disjunction

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitDisjunction" ):
                return visitor.visitDisjunction(self)
            else:
                return visitor.visitChildren(self)




    def disjunction(self):

        localctx = TwtlParser.DisjunctionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_disjunction)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 21
            self.conjunction()
            self.state = 26
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==2:
                self.state = 22
                self.match(TwtlParser.OR)
                self.state = 23
                self.conjunction()
                self.state = 28
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ConjunctionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def concatenation(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(TwtlParser.ConcatenationContext)
            else:
                return self.getTypedRuleContext(TwtlParser.ConcatenationContext,i)


        def AND(self, i:int=None):
            if i is None:
                return self.getTokens(TwtlParser.AND)
            else:
                return self.getToken(TwtlParser.AND, i)

        def getRuleIndex(self):
            return TwtlParser.RULE_conjunction

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitConjunction" ):
                return visitor.visitConjunction(self)
            else:
                return visitor.visitChildren(self)




    def conjunction(self):

        localctx = TwtlParser.ConjunctionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_conjunction)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 29
            self.concatenation()
            self.state = 34
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==1:
                self.state = 30
                self.match(TwtlParser.AND)
                self.state = 31
                self.concatenation()
                self.state = 36
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ConcatenationContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def temporal(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(TwtlParser.TemporalContext)
            else:
                return self.getTypedRuleContext(TwtlParser.TemporalContext,i)


        def CONCAT(self, i:int=None):
            if i is None:
                return self.getTokens(TwtlParser.CONCAT)
            else:
                return self.getToken(TwtlParser.CONCAT, i)

        def getRuleIndex(self):
            return TwtlParser.RULE_concatenation

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitConcatenation" ):
                return visitor.visitConcatenation(self)
            else:
                return visitor.visitChildren(self)




    def concatenation(self):

        localctx = TwtlParser.ConcatenationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_concatenation)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 37
            self.temporal()
            self.state = 42
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==6:
                self.state = 38
                self.match(TwtlParser.CONCAT)
                self.state = 39
                self.temporal()
                self.state = 44
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TemporalContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return TwtlParser.RULE_temporal

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)



    class WithinExprContext(TemporalContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a TwtlParser.TemporalContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def LBRACK(self, i:int=None):
            if i is None:
                return self.getTokens(TwtlParser.LBRACK)
            else:
                return self.getToken(TwtlParser.LBRACK, i)
        def formula(self):
            return self.getTypedRuleContext(TwtlParser.FormulaContext,0)

        def RBRACK(self, i:int=None):
            if i is None:
                return self.getTokens(TwtlParser.RBRACK)
            else:
                return self.getToken(TwtlParser.RBRACK, i)
        def CARET(self):
            return self.getToken(TwtlParser.CARET, 0)
        def INT(self, i:int=None):
            if i is None:
                return self.getTokens(TwtlParser.INT)
            else:
                return self.getToken(TwtlParser.INT, i)
        def COMMA(self):
            return self.getToken(TwtlParser.COMMA, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitWithinExpr" ):
                return visitor.visitWithinExpr(self)
            else:
                return visitor.visitChildren(self)


    class HoldPropContext(TemporalContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a TwtlParser.TemporalContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def HOLD(self):
            return self.getToken(TwtlParser.HOLD, 0)
        def CARET(self):
            return self.getToken(TwtlParser.CARET, 0)
        def INT(self):
            return self.getToken(TwtlParser.INT, 0)
        def PROP(self):
            return self.getToken(TwtlParser.PROP, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitHoldProp" ):
                return visitor.visitHoldProp(self)
            else:
                return visitor.visitChildren(self)


    class HoldNegPropContext(TemporalContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a TwtlParser.TemporalContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def HOLD(self):
            return self.getToken(TwtlParser.HOLD, 0)
        def CARET(self):
            return self.getToken(TwtlParser.CARET, 0)
        def INT(self):
            return self.getToken(TwtlParser.INT, 0)
        def NOT(self):
            return self.getToken(TwtlParser.NOT, 0)
        def PROP(self):
            return self.getToken(TwtlParser.PROP, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitHoldNegProp" ):
                return visitor.visitHoldNegProp(self)
            else:
                return visitor.visitChildren(self)


    class HoldFalseContext(TemporalContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a TwtlParser.TemporalContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def HOLD(self):
            return self.getToken(TwtlParser.HOLD, 0)
        def CARET(self):
            return self.getToken(TwtlParser.CARET, 0)
        def INT(self):
            return self.getToken(TwtlParser.INT, 0)
        def FALSE(self):
            return self.getToken(TwtlParser.FALSE, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitHoldFalse" ):
                return visitor.visitHoldFalse(self)
            else:
                return visitor.visitChildren(self)


    class TemporalNegationContext(TemporalContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a TwtlParser.TemporalContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def negation(self):
            return self.getTypedRuleContext(TwtlParser.NegationContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTemporalNegation" ):
                return visitor.visitTemporalNegation(self)
            else:
                return visitor.visitChildren(self)


    class HoldTrueContext(TemporalContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a TwtlParser.TemporalContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def HOLD(self):
            return self.getToken(TwtlParser.HOLD, 0)
        def CARET(self):
            return self.getToken(TwtlParser.CARET, 0)
        def INT(self):
            return self.getToken(TwtlParser.INT, 0)
        def TRUE(self):
            return self.getToken(TwtlParser.TRUE, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitHoldTrue" ):
                return visitor.visitHoldTrue(self)
            else:
                return visitor.visitChildren(self)


    class EventuallyExprContext(TemporalContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a TwtlParser.TemporalContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def EVENTUALLY(self):
            return self.getToken(TwtlParser.EVENTUALLY, 0)
        def LPAREN(self):
            return self.getToken(TwtlParser.LPAREN, 0)
        def formula(self):
            return self.getTypedRuleContext(TwtlParser.FormulaContext,0)

        def RPAREN(self):
            return self.getToken(TwtlParser.RPAREN, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEventuallyExpr" ):
                return visitor.visitEventuallyExpr(self)
            else:
                return visitor.visitChildren(self)



    def temporal(self):

        localctx = TwtlParser.TemporalContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_temporal)
        self._la = 0 # Token type
        try:
            self.state = 80
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,4,self._ctx)
            if la_ == 1:
                localctx = TwtlParser.HoldPropContext(self, localctx)
                self.enterOuterAlt(localctx, 1)
                self.state = 45
                self.match(TwtlParser.HOLD)
                self.state = 46
                self.match(TwtlParser.CARET)
                self.state = 47
                self.match(TwtlParser.INT)
                self.state = 48
                self.match(TwtlParser.PROP)
                pass

            elif la_ == 2:
                localctx = TwtlParser.HoldTrueContext(self, localctx)
                self.enterOuterAlt(localctx, 2)
                self.state = 49
                self.match(TwtlParser.HOLD)
                self.state = 50
                self.match(TwtlParser.CARET)
                self.state = 51
                self.match(TwtlParser.INT)
                self.state = 52
                self.match(TwtlParser.TRUE)
                pass

            elif la_ == 3:
                localctx = TwtlParser.HoldFalseContext(self, localctx)
                self.enterOuterAlt(localctx, 3)
                self.state = 53
                self.match(TwtlParser.HOLD)
                self.state = 54
                self.match(TwtlParser.CARET)
                self.state = 55
                self.match(TwtlParser.INT)
                self.state = 56
                self.match(TwtlParser.FALSE)
                pass

            elif la_ == 4:
                localctx = TwtlParser.HoldNegPropContext(self, localctx)
                self.enterOuterAlt(localctx, 4)
                self.state = 57
                self.match(TwtlParser.HOLD)
                self.state = 58
                self.match(TwtlParser.CARET)
                self.state = 59
                self.match(TwtlParser.INT)
                self.state = 60
                self.match(TwtlParser.NOT)
                self.state = 61
                self.match(TwtlParser.PROP)
                pass

            elif la_ == 5:
                localctx = TwtlParser.EventuallyExprContext(self, localctx)
                self.enterOuterAlt(localctx, 5)
                self.state = 62
                self.match(TwtlParser.EVENTUALLY)
                self.state = 63
                self.match(TwtlParser.LPAREN)
                self.state = 64
                self.formula()
                self.state = 65
                self.match(TwtlParser.RPAREN)
                pass

            elif la_ == 6:
                localctx = TwtlParser.WithinExprContext(self, localctx)
                self.enterOuterAlt(localctx, 6)
                self.state = 67
                self.match(TwtlParser.LBRACK)
                self.state = 68
                self.formula()
                self.state = 69
                self.match(TwtlParser.RBRACK)
                self.state = 70
                self.match(TwtlParser.CARET)
                self.state = 71
                self.match(TwtlParser.LBRACK)
                self.state = 72
                self.match(TwtlParser.INT)
                self.state = 75
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==12:
                    self.state = 73
                    self.match(TwtlParser.COMMA)
                    self.state = 74
                    self.match(TwtlParser.INT)


                self.state = 77
                self.match(TwtlParser.RBRACK)
                pass

            elif la_ == 7:
                localctx = TwtlParser.TemporalNegationContext(self, localctx)
                self.enterOuterAlt(localctx, 7)
                self.state = 79
                self.negation()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NegationContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def PROP(self):
            return self.getToken(TwtlParser.PROP, 0)

        def NOT(self):
            return self.getToken(TwtlParser.NOT, 0)

        def TRUE(self):
            return self.getToken(TwtlParser.TRUE, 0)

        def FALSE(self):
            return self.getToken(TwtlParser.FALSE, 0)

        def atom(self):
            return self.getTypedRuleContext(TwtlParser.AtomContext,0)


        def getRuleIndex(self):
            return TwtlParser.RULE_negation

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNegation" ):
                return visitor.visitNegation(self)
            else:
                return visitor.visitChildren(self)




    def negation(self):

        localctx = TwtlParser.NegationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_negation)
        self._la = 0 # Token type
        try:
            self.state = 92
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,7,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 83
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==3:
                    self.state = 82
                    self.match(TwtlParser.NOT)


                self.state = 85
                self.match(TwtlParser.PROP)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 86
                self.match(TwtlParser.TRUE)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 87
                self.match(TwtlParser.FALSE)
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 89
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==3:
                    self.state = 88
                    self.match(TwtlParser.NOT)


                self.state = 91
                self.atom()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AtomContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LPAREN(self):
            return self.getToken(TwtlParser.LPAREN, 0)

        def formula(self):
            return self.getTypedRuleContext(TwtlParser.FormulaContext,0)


        def RPAREN(self):
            return self.getToken(TwtlParser.RPAREN, 0)

        def getRuleIndex(self):
            return TwtlParser.RULE_atom

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAtom" ):
                return visitor.visitAtom(self)
            else:
                return visitor.visitChildren(self)




    def atom(self):

        localctx = TwtlParser.AtomContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_atom)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 94
            self.match(TwtlParser.LPAREN)
            self.state = 95
            self.formula()
            self.state = 96
            self.match(TwtlParser.RPAREN)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





