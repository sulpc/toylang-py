# -*- coding: utf-8 -*-
"""
toylang lexer
"""
from toytoken import *
from toyerror import *
import sys

class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.residual = len(text)
        self.current_char = self.text[0]
        # self.pos  = 0
        self.line = 1
        self.col  = 1

    def error(self, message):
        raise LexerError(self.position(), message)

    def position(self):
        return self.line, self.col

    def advance(self, n=1):
        """advance n char, refresh current_char
        """
        assert(n <= self.residual)

        for i in range(n):
            self.col += 1
            if self.text[i] == '\n':
                self.line += 1
                self.col = 1

        self.residual -= n
        self.text = self.text[n:]
        if self.residual == 0:
            self.current_char = None
        else:
            self.current_char = self.text[0]

    def start_with(self, s):
        return self.text.startswith(s)

    def next_token(self):
        """get next token
        """
        self.skip_writespaces()

        if self.current_char is None:
            return Token(TokenType.EOF, None, self.position())

        # digit -> number_literal
        if self.current_char.isdigit():
            return self.number_literal()

        # '"` -> string_literal
        if self.current_char in ('"', "'", '`'):
            return self.string_literal()

        # alpha -> identifier/keyword
        if self.current_char.isalpha() or self.current_char == '_':
            return self.identifier_keyword()

        # operators
        for op in OPERATOR_TOKEN_LIST:
            if self.current_char == op.start:
                if self.start_with(op.content):
                    token = Token(op.type, op.content, self.position())
                    self.advance(op.len)
                    return token

        # other
        self.error(ErrorInfo.unrecognized_char(self.current_char))

    def skip_writespaces(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.advance()
            elif self.start_with('//'):     # // comment
                self.skip_comment(oneline=True)
            elif self.start_with('/*'):     # /* comment
                self.skip_comment(oneline=False)
            else:
                break

    def skip_comment(self, oneline: bool):
        if oneline:
            self.advance(2)         # eat `//`
            while self.current_char is not None:
                if self.current_char == '\n':
                    break
                self.advance(1)
            if self.current_char is not None:
                self.advance(1)     # eat `\n`
        else:
            self.advance(2)         # eat `/*`
            while self.current_char is not None:
                if self.current_char == '*' and self.start_with('*/'):
                    break
                self.advance(1)
            if self.current_char is not None:
                self.advance(2)     # eat `*/`

    def number_literal(self):
        """parse a literal number

        number:
        """
        token = Token(None, None, self.position())

        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()

        if self.current_char != '.':
            token.type = TokenType.INT_LITERAL
        else:
            result += '.'
            self.advance()

            while self.current_char is not None and self.current_char.isdigit():
                result += self.current_char
                self.advance()

            token.type = TokenType.FLOAT_LITERAL

        token.value = result
        return token

    def string_literal(self):
        """parse a literal string
        """
        token = Token(TokenType.STRING_LITERAL, None, self.position())
        result = ''
        start = self.current_char
        self.advance(1)     # eat ' " `

        while self.current_char != start:
            if self.current_char is None:
                self.error(ErrorInfo.literal_string_not_end())
            if self.current_char == '\n' and start != '`':
                self.error(ErrorInfo.literal_string_not_end())

            if self.current_char == '\r':
                self.advance()              # '\r' is ignored
                continue
            if self.current_char == '\\':   # escape
                result += self.escape()
            else:
                result += self.current_char
                self.advance()

        self.advance(1)     # eat ' " `
        token.value = result
        return token

    def escape(self):
        """parse escape char
        """
        self.advance(1)         # eat '\'
        if self.current_char in ('"', "'", "`"):
            self.advance(1)
            return self.current_char

        if self.current_char == 'n':
            self.advance(1)
            return '\n'

        self.error(ErrorInfo.unsupport_escape(self.current_char))

    def identifier_keyword(self):
        """parse a identifier/keyword
        """
        token = Token(None, None, self.position())
        result = ''
        while self.current_char is not None:
            if self.current_char.isalnum() or self.current_char == '_':
                result += self.current_char
                self.advance()
            else:
                break
        token.value = result

        # keyword or idetifier
        token.type = RESERVED_KEYWORDS.get(result, TokenType.IDENTIFIER)
        token.value = result
        return token


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: python toy.py <src.toy>')
        sys.exit(0)

    with open(sys.argv[1], 'r') as f:
        code = f.read()

    try:
        lexer = Lexer(code)

        while True:
            token = lexer.next_token()
            print(token)
            if token.type == TokenType.EOF:
                break
    except LexerError as e:
        print(e)
