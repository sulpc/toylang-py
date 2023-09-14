# -*- coding: utf-8 -*-
"""
toylang token define
"""

from enum import Enum


class TokenType(Enum):
    # misc
    IDENTIFIER          = 'IDENTIFIER'
    INT_LITERAL         = 'INT_LITERAL'
    FLOAT_LITERAL       = 'FLOAT_LITERAL'
    STRING_LITERAL      = 'STRING_LITERAL'
    EOF                 = 'EOF'

    # sep
    LPAREN              = '('
    RPAREN              = ')'
    LBRACK              = '['
    RBRACK              = ']'
    LBRACE              = '{'
    RBRACE              = '}'
    COMMA               = ','
    DOT                 = '.'
    COLON               = ':'
    SEMI                = ';'
    QUERY               = '?'
    VARARG              = '...'
    # compare
    EQ                  = '=='
    NE                  = '!='
    LT                  = '<'
    LE                  = '<='
    GT                  = '>'
    GE                  = '>='
    # cal
    ADD                 = '+'
    SUB                 = '-'
    MUL                 = '*'
    DIV                 = '/'
    POW                 = '**'
    MOD                 = '%'
    BSHL                = '<<'
    BSHR                = '>>'
    BAND                = '&'
    BXOR                = '^'
    BOR                 = '|'
    BNOT                = '~'
    LEN                 = '#'
    # assign
    ASSIGN              = '='
    # compoundassign
    SELF_ADD            = '+='
    SELF_SUB            = '-='
    SELF_MUL            = '*='
    SELF_DIV            = '/='
    SELF_POW            = '**='
    SELF_MOD            = '%='
    SELF_BSHL           = '<<='
    SELF_BSHR           = '>>='
    SELF_BAND           = '&='
    SELF_BXOR           = '^='
    SELF_BOR            = '|='
    # keyword
    KW_START            = '__kw_start'
    AND                 = 'and'
    NOT                 = 'not'
    OR                  = 'or'
    IF                  = 'if'
    ELIF                = 'elif'
    ELSE                = 'else'
    SWITCH              = 'switch'
    CASE                = 'case'
    DEFAULT             = 'default'
    LABEL               = 'label'
    GOTO                = 'goto'
    BREAK               = 'break'
    CONTINUE            = 'continue'
    REPEAT              = 'repeat'
    UNTIL               = 'until'
    WHILE               = 'while'
    FOR                 = 'for'
    IS                  = 'is'
    IN                  = 'in'
    FUNC                = 'func'
    RETURN              = 'return'
    LOCAL               = 'local'       # -
    GLOBAL              = 'global'      # -
    VAR                 = 'var'
    PRINT               = 'print'       # NOTE
    TRUE                = 'true'
    FALSE               = 'false'
    NULL                = 'null'
    KW_END              = '__kw_end'


class OperatorTokenCfg:
    def __init__(self, start_char, content, token_type, token_len):
        self.start = start_char
        self.content = content
        self.type = token_type
        self.len = token_len


OPERATOR_TOKEN_LIST = [
    #                start  content    type             len     顺序应该会影响解析效率
    OperatorTokenCfg('=',   '==',  TokenType.EQ,        len('==')  ),
    OperatorTokenCfg('=',   '=',   TokenType.ASSIGN,    len('=')   ),
    OperatorTokenCfg('.',   '...', TokenType.VARARG,    len('...') ),
    OperatorTokenCfg('.',   '.',   TokenType.DOT,       len('.')   ),
    OperatorTokenCfg('+',   '+=',  TokenType.SELF_ADD,  len('+=')  ),
    OperatorTokenCfg('+',   '+',   TokenType.ADD,       len('+')   ),
    OperatorTokenCfg('-',   '-=',  TokenType.SELF_SUB,  len('-=')  ),
    OperatorTokenCfg('-',   '-',   TokenType.SUB,       len('-')   ),
    OperatorTokenCfg('*',   '*=',  TokenType.SELF_MUL,  len('*=')  ),
    OperatorTokenCfg('*',   '*',   TokenType.MUL,       len('*')   ),
    OperatorTokenCfg('/',   '/=',  TokenType.SELF_DIV,  len('/=')  ),
    OperatorTokenCfg('/',   '/',   TokenType.DIV,       len('/')   ),
    OperatorTokenCfg('*',   '**=', TokenType.SELF_POW,  len('**=') ),
    OperatorTokenCfg('*',   '**',  TokenType.POW,       len('**')  ),
    OperatorTokenCfg('%',   '%=',  TokenType.SELF_MOD,  len('%=')  ),
    OperatorTokenCfg('%',   '%',   TokenType.MOD,       len('%')   ),
    OperatorTokenCfg('<',   '<<=', TokenType.SELF_BSHL, len('<<=') ),
    OperatorTokenCfg('<',   '<=',  TokenType.LE,        len('<=')  ),
    OperatorTokenCfg('<',   '<<',  TokenType.BSHL,      len('<<')  ),
    OperatorTokenCfg('<',   '<',   TokenType.LT,        len('<')   ),
    OperatorTokenCfg('>',   '>>=', TokenType.SELF_BSHR, len('>>=') ),
    OperatorTokenCfg('>',   '>=',  TokenType.GE,        len('>=')  ),
    OperatorTokenCfg('>',   '>>',  TokenType.BSHR,      len('>>')  ),
    OperatorTokenCfg('>',   '>',   TokenType.GT,        len('>')   ),
    OperatorTokenCfg('&',   '&=',  TokenType.SELF_BAND, len('&=')  ),
    OperatorTokenCfg('&',   '&',   TokenType.BAND,      len('&')   ),
    OperatorTokenCfg('^',   '^=',  TokenType.SELF_BXOR, len('^=')  ),
    OperatorTokenCfg('^',   '^',   TokenType.BXOR,      len('^')   ),
    OperatorTokenCfg('|',   '|=',  TokenType.SELF_BOR,  len('|=')  ),
    OperatorTokenCfg('|',   '|',   TokenType.BOR,       len('|')   ),
    OperatorTokenCfg('(',   '(',   TokenType.LPAREN,    len('(')   ),
    OperatorTokenCfg(')',   ')',   TokenType.RPAREN,    len(')')   ),
    OperatorTokenCfg('[',   '[',   TokenType.LBRACK,    len('[')   ),
    OperatorTokenCfg(']',   ']',   TokenType.RBRACK,    len(']')   ),
    OperatorTokenCfg('{',   '{',   TokenType.LBRACE,    len('{')   ),
    OperatorTokenCfg('}',   '}',   TokenType.RBRACE,    len('}')   ),
    OperatorTokenCfg(',',   ',',   TokenType.COMMA,     len(',')   ),
    OperatorTokenCfg(':',   ':',   TokenType.COLON,     len(':')   ),
    OperatorTokenCfg(';',   ';',   TokenType.SEMI,      len(';')   ),
    OperatorTokenCfg('?',   '?',   TokenType.QUERY,     len('?')   ),
    OperatorTokenCfg('!',   '!=',  TokenType.NE,        len('!=')  ),
    OperatorTokenCfg('~',   '~',   TokenType.BNOT,      len('~')   ),
    OperatorTokenCfg('#',   '#',   TokenType.LEN,       len('#')   ),
]


class Token:
    def __init__(self, type: TokenType, value: str, position: tuple[int, int]):
        self.type  = type
        self.value = value
        self.position = position

    def __str__(self):
        return f'Token({self.type}, {repr(self.value)}, pos={self.position[0]}:{self.position[1]})'

    def __repr__(self):
        return self.__str__()


def _build_reserved_keywords():
    token_list = list(TokenType)
    start_idx = token_list.index(TokenType.KW_START) + 1
    end_idx = token_list.index(TokenType.KW_END) - 1
    return {
        token_type.value: token_type
        for token_type in token_list[start_idx: end_idx + 1]
    }


RESERVED_KEYWORDS = _build_reserved_keywords()
