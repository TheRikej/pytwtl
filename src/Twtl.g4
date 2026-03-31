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
    | HOLD CARET INT NOT PROP                      # holdNegProp
    | LBRACK formula RBRACK CARET LBRACK INT COMMA INT RBRACK # withinExpr
    | negation                                     # temporalNegation
    ;

negation
    : NOT? atom
    ;

atom
    : TRUE
    | FALSE
    | PROP
    | LPAREN formula RPAREN
    ;

AND: '&';
OR: '|';
NOT: '!';
HOLD: 'H';
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
