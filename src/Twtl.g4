grammar Twtl;

prog
    : formula EOF
    ;

formula
    : disjunction
    ;

disjunction
    : conjunction (OR conjunction)*
    ;

conjunction
    : concatenation (AND concatenation)*
    ;

concatenation
    : temporal (CONCAT temporal)*
    ;

temporal
    : HOLD CARET INT PROP                          # holdProp
    | HOLD CARET INT TRUE                          # holdTrue
    | HOLD CARET INT FALSE                         # holdFalse
    | HOLD CARET INT NOT PROP                      # holdNegProp
    | EVENTUALLY LPAREN formula RPAREN             # eventuallyExpr
    | LBRACK formula RBRACK CARET LBRACK INT (COMMA INT)? RBRACK # withinExpr
    | negation                                     # temporalNegation
    ;

negation
    : NOT? PROP
    | TRUE
    | FALSE
    | NOT? atom
    ;

atom
    : LPAREN formula RPAREN
    ;

AND: '&';
OR: '|';
NOT: '!';
HOLD: 'H';
EVENTUALLY: 'F';
CONCAT: '*';
CARET: '^';
LBRACK: '[';
RBRACK: ']';
LPAREN: '(';
RPAREN: ')';
COMMA: ',';

TRUE: 'True' | 'true';
FALSE: 'False' | 'false';
INT: '0' | [1-9] [0-9]*;
PROP: ([a-zA-GI-VX-Z]) ('_' | [a-zA-Z0-9])*;

LINECMT: '//' ~[\n\r]* -> skip;
WS: [\n\r\f\t ]+ -> skip;
