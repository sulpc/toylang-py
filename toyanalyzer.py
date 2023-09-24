# -*- coding: utf-8 -*-
"""
toylang symbol define & semantic analyzer

role:
- insure var used after declared
- insure temp var in for stat not be assigned
- insure var not be duplicate declared

note:
- deprecated
"""
from toyerror import *
from toylexer import *
from toyast import *
from toydisplayer import *
from toyparser import *

import sys
from collections import OrderedDict


CONFIG_USE_SCOPE_LOG    = False
CONFIG_USE_ANALYZER_LOG = False


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


class SemanticAnalyzer(AstNodeVistor):
    def __init__(self, tree):
        self.tree = tree
        self.current_scope = None
        self.in_loop = False
        self.in_function = False

    def error(self, position, message):
        raise SemanticError(position, message)

    def log(self, msg):
        if CONFIG_USE_ANALYZER_LOG:
            print(msg)

    def enter_scope(self, identifier, inherit=True):
        self.log(f'enter scope: {identifier}')
        new_scope = ScopeSymbolTable(
            identifier=identifier,
            level=self.current_scope.level + 1 if self.current_scope is not None else 0,
            parent=self.current_scope)
        if inherit:                 # inherit properties of parent scope, like in_loop, in_function
            new_scope.in_loop = self.current_scope.in_loop
            new_scope.in_function = self.current_scope.in_function
        self.current_scope = new_scope

    def exit_scope(self):
        self.log(self.current_scope)
        self.log('leave scope: %s' % self.current_scope.identifier)
        self.log('')
        self.current_scope = self.current_scope.parent

    def visit_Program(self, node: Program):
        self.enter_scope('program', inherit=False)
        for stat in node.stats:
            self.visit(stat)
        self.exit_scope()

    def visit_EmptyStat(self, node: EmptyStat):
        pass

    def visit_BlockStat(self, node: BlockStat):
        self.enter_scope('block')
        for stat in node.stats:
            self.visit(stat)
        self.exit_scope()

    def visit_VarDeclStat(self, node: VarDeclStat):
        for name in node.names:
            if self.current_scope.lookup(name.identifier, current_scope_only=True) is not None:
                self.error(node.position, ErrorInfo.name_duplicate_declared(name.identifier))
            var_symbol = VarSymbol(identifier=name.identifier)
            self.current_scope.insert(var_symbol)
        if node.exprs is not None:
            for expr in node.exprs:
                self.visit(expr)

    def visit_IfStat(self, node: IfStat):
        for cond, stat in zip(node.cond_exprs, node.stats):
            self.visit(cond)
            self.visit(stat)

    def visit_SwitchStat(self, node: SwitchStat):
        self.visit(node.expr)
        for case, stat in zip(node.case_exprs, node.case_stats):
            self.visit(case)
            self.visit(stat)
        self.visit(node.default_stat)

    def visit_RepeatStat(self, node: RepeatStat):
        self.in_loop = True
        self.visit(node.expr)
        self.visit(node.stat)

    def visit_WhileStat(self, node: WhileStat):
        self.visit(node.expr)
        self.visit(node.stat)

    def visit_ForloopStat(self, node: ForloopStat):
        self.enter_scope('for')
        self.current_scope.insert(NameSymbol(node.var_name.identifier))
        self.visit(node.start_expr)
        self.visit(node.end_expr)
        if node.step_expr is not None:
            self.visit(node.step_expr)
        self.visit(node.stat)
        self.exit_scope()

    def visit_ForeachStat(self, node: ForeachStat):
        self.enter_scope('for')
        self.current_scope.insert(NameSymbol(node.key_name.identifier))
        if node.val_name is not None:
            self.current_scope.insert(NameSymbol(node.val_name.identifier))
        self.visit(node.expr)
        self.visit(node.stat)
        self.exit_scope()

    def visit_BreakStat(self, node: BreakStat):
        if not self.current_scope.in_loop:
            self.error(node.position, ErrorInfo.invalid_syntax('break'))

    def visit_ContinueStat(self, node: ContinueStat):
        if not self.current_scope.in_loop:
            self.error(node.position, ErrorInfo.invalid_syntax('continue'))

    def visit_ReturnStat(self, node: ReturnStat):
        raise Exception('TODO: not implement!')

    def visit_AssignStat(self, node: AssignStat):
        for expr in node.left_exprs:
            if type(expr) is Name:
                name_symbol = self.current_scope.lookup(expr.identifier)
                if name_symbol is None:
                    self.error(expr.position, ErrorInfo.name_not_declared(expr.identifier))
                elif type(name_symbol) is not VarSymbol:
                    self.error(expr.position, ErrorInfo.name_not_assignable(expr.identifier))
            else:
                self.visit(expr)
        for expr in node.right_exprs:
            self.visit(expr)

    def visit_CompoundAssignStat(self, node: CompoundAssignStat):
        expr = node.left_expr
        if type(expr) is Name:
            name_symbol = self.current_scope.lookup(expr.identifier)
            if name_symbol is None:
                self.error(expr.position, ErrorInfo.name_not_declared(expr.identifier))
            elif type(name_symbol) is not VarSymbol:
                self.error(expr.position, ErrorInfo.name_not_assignable(expr.identifier))
        else:
            self.visit(expr)

        self.visit(node.right_expr)

    def visit_FuncDef(self, node: FuncDef):
        raise Exception('TODO: not implement!')

    def visit_FuncCall(self, node: FuncCall):
        # self.visit(node.func_expr)
        for expr in node.arg_exprs:
            self.visit(expr)

    def visit_SelectExpr(self, node: SelectExpr):
        self.visit(node.cond)
        self.visit(node.expr1)
        self.visit(node.expr2)

    def visit_BinOpExpr(self, node: BinOpExpr):
        self.visit(node.left_expr)
        self.visit(node.right_expr)

    def visit_UniOpExpr(self, node: UniOpExpr):
        self.visit(node.expr)

    def visit_ListCtorExpr(self, node: ListCtorExpr):
        raise Exception('TODO: not implement!')

    def visit_MapCtorExpr(self, node: MapCtorExpr):
        raise Exception('TODO: not implement!')

    def visit_AccessExpr(self, node: AccessExpr):
        raise Exception('TODO: not implement!')

    def visit_Name(self, node: Name):
        if self.current_scope.lookup(node.identifier) is None:
            self.error(node.position, ErrorInfo.name_not_declared(node.identifier))

    def visit_Num(self, node: Num):
        pass

    def visit_String(self, node: String):
        pass

    def visit_Bool(self, node: Bool):
        pass

    def visit_Null(self, node: Null):
        pass

    def analysis(self):
        self.enter_scope('__scope_0', False)
        self.visit(self.tree)
        self.exit_scope()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: python toy.py <src.toy>')
        sys.exit(0)

    with open(sys.argv[1], 'r') as f:
        code = f.read()

    try:
        lexer = Lexer(code)
        parser = Parser(lexer)
        tree = parser.parse()

        displayer = Displayer(tree, 'ast.html')
        displayer.display()

        analyzer = SemanticAnalyzer(tree)
        analyzer.analysis()
    except (LexerError, ParserError, SemanticError) as e:
        print(e)
