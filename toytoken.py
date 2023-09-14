from enum import Enum


class ValueType(Enum):
    STRING              = 'string'
    INT                 = 'int'
    REAL                = 'real'
    LIST                = 'list'
    OBJECT              = 'object'
    TABLE               = 'table'


class TokenType(Enum):
    # misc
    NAME                = 'NAME'
    INT_LITERAL         = 'INT_LITERAL'
    REAL_LITERAL        = 'REAL_LITERAL'
    STRING_LITERAL      = 'STRING_LITERAL'
    BOOL_LITERAL        = 'BOOL_LITERAL'
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
    ### keyword
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
    TRUE                = 'true'
    FALSE               = 'false'
    NULL                = 'null'
    FUNC                = 'func'
    RETURN              = 'return'
    LOCAL               = 'local'
    GLOBAL              = 'global'
    PRINT               = 'print'
    KW_END              = '__kw_end'


def _build_reserved_keywords():
    token_list = list(TokenType)
    start_idx = token_list.index(TokenType.KW_START) + 1
    end_idx = token_list.index(TokenType.KW_END) - 1
    return {
        token_type.value: token_type
        for token_type in token_list[start_idx: end_idx + 1]
    }


RESERVED_KEYWORDS = _build_reserved_keywords()
