# -*- coding: utf-8 -*-
"""
toylang error information
"""

class ErrorInfo:
    # lexer error

    @staticmethod
    def unrecognized_char(item):
        return f'unrecognized char `{item}`'

    @staticmethod
    def unsupport_escape(item):
        return f'unsupport escape char `{item}`'

    @staticmethod
    def literal_string_not_end():
        return f'literal string is not end'

    # parser error

    @staticmethod
    def invalid_statement(start):
        return f'invalid statement start with `{start}`'

    @staticmethod
    def unexpected_token(item, want):
        return f'token `{item}` is not expected, want `{want}`'

    @staticmethod
    def type_not_implemented(item):
        return f'type `{item}` is not implemented'

    # semantic error

    @staticmethod
    def name_duplicate_defined(item):
        return f'name `{item}` duplicate defined'

    @staticmethod
    def name_not_defined(item):
        return f'name `{item}` not defined'

    @staticmethod
    def name_not_callable(item):
        return f'name `{item}` not a procedure/function'

    @staticmethod
    def wrong_arguments_call(item):
        return f'wrong argument number in call `{item}`'

    @staticmethod
    def invalid_break():
        return 'break outside of loop'

    @staticmethod
    def invalid_continue():
        return 'continue outside of loop'

    @staticmethod
    def name_not_assignable(item):
        return f'name `{item}` is not assignable'

    # intepreter error

    @staticmethod
    def name_not_valid(item):
        return f'name `{item}` is invalid'

    @staticmethod
    def op_not_implemented(item):
        return f'op `{item}` is not implemented'

    @staticmethod
    def op_used_on_wrong_type(item):
        return f'op `{item}` used on wrong type'


class Error(Exception):
    def __init__(self, position, message):
        self.position = position
        self.message = message

    def __str__(self):
        return f'{self.__class__.__name__}: <{self.position[0]}:{self.position[1]}>: {self.message}'

    __repr__ = __str__


class LexerError(Error):
    pass


class ParserError(Error):
    pass


class SemanticError(Error):
    pass


class InterpreterError(Error):
    pass
