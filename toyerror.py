# -*- coding: utf-8 -*-
"""
toylang error information
"""

class ErrorInfo:
    #
    # lexer error
    #

    @staticmethod
    def unrecognized_char(item):
        return f'unrecognized char `{item}`'

    @staticmethod
    def unsupport_escape(item):
        return f'unsupport escape char `{item}`'

    @staticmethod
    def literal_string_not_end():
        return f'literal string is not end'

    #
    # parser error
    #

    @staticmethod
    def unexpected_token(item, want):
        return f'token `{item}` is not expected, want `{want}`'

    @staticmethod
    def type_not_implemented(item):
        return f'type `{item}` is not implemented'

    #
    # semantic & intepreter error
    #

    @staticmethod
    def name_not_declared(item):
        return f'name `{item}` not declared'

    @staticmethod
    def name_duplicate_declared(item):
        return f'name `{item}` duplicate declared'

    @staticmethod
    def name_not_assignable(item):
        return f'name `{item}` not assignable'

    @staticmethod
    def name_not_callable(item):
        return f'name `{item}` not callable'

    @staticmethod
    def invalid_syntax(item):
        return f'invalid syntax `{item}`'

    @staticmethod
    def expr_type_error(want):
        return f'expr type error, want `{want}`'

    @staticmethod
    def expr_value_error(msg):
        return f'expr value error: {msg}'

    @staticmethod
    def op_not_implemented(item):
        return f'op `{item}` is not implemented'

    @staticmethod
    def general(info):
        return info


class Error(Exception):
    def __init__(self, message=''):
        self.message = message

    def __str__(self):
        return self.message


class GrammarError(Error):
    def __init__(self, position, message):
        self.position = position
        super().__init__(message)

    def __str__(self):
        return f'{self.__class__.__name__}: <{self.position[0]}:{self.position[1]}>: {self.message}'


class LexerError(GrammarError):
    pass


class ParserError(GrammarError):
    pass


class SemanticError(GrammarError):
    pass


class InterpreterError(GrammarError):
    pass


class ValueTypeError(Error):
    pass

class MemberAccessError(Error):
    pass
