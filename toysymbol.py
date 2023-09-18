# -*- coding: utf-8 -*-
"""
toylang symbol define
"""
from toyconfig import *
from collections import OrderedDict


class Symbol:
    def __init__(self, identifier):
        self.identifier = identifier
        self.scope_level = 0
        # self.value = None

    def __str__(self) -> str:
        return self.identifier

    def __repr__(self) -> str:
        # return f'{self.__class__.__name__}("{self.identifier}")'
        return "{class_name}('{identifier}')".format(
            class_name=self.__class__.__name__,
            identifier=self.identifier,
        )


class BuiltinTypeSymbol(Symbol):
    def __init__(self, identifier):
        super().__init__(identifier)


class VarSymbol(Symbol):
    def __init__(self, identifier):
        super().__init__(identifier)


class NameSymbol(Symbol):
    def __init__(self, identifier):
        super().__init__(identifier)


class ScopeSymbolTable:
    def __init__(self, identifier, level, parent=None):
        self.symbols = OrderedDict()
        self.identifier = identifier
        self.level = level
        self.parent = parent
        self.in_loop = False
        self.in_function = False

    def __str__(self) -> str:
        h1 = f'SCOPE SYMBOL TABLE <{self.identifier},{self.level},{self.parent.identifier if self.parent else None}>'
        lines = [h1, '=' * len(h1)]
        lines.extend(
            ['%-10s: %r' % (key, value) for key, value in self.symbols.items()]
        )
        lines.append('=' * len(h1))
        s = '\n'.join(lines)
        return s

    __repr__ = __str__

    def log(self, msg):
        if CONFIG_USE_SCOPE_LOG:
            print(msg)

    def insert(self, symbol: Symbol):
        self.log(f'insert: {symbol.identifier}. (scope: {self.identifier})')
        symbol.scope_level = self.level
        self.symbols[symbol.identifier] = symbol

    def lookup(self, identifier, current_scope_only=False) -> Symbol:
        self.log(f'lookup: {identifier}. (scope identifier: {self.identifier})')
        symbol = self.symbols.get(identifier)

        if current_scope_only or symbol is not None:
            return symbol

        # recursively lookup symbol in the outer scope
        if self.parent is not None:
            return self.parent.lookup(identifier)
        else:
            return None


if __name__ == '__main__':
    table = ScopeSymbolTable('_g', 0)

    v1 = VarSymbol('idx')
    n1 = NameSymbol('i')
    t1 = BuiltinTypeSymbol('int')

    table.insert(t1)
    table.insert(n1)
    table.insert(v1)

    print(table)
