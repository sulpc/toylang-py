# -*- coding: utf-8 -*-
"""
toylang formator
"""
from toyast import *
from toyerror import *
from toylexer import *
from toyparser import *
from toyast import *
from toydisplayer import *
from toyvalue import *
from toylib import *
import toylog
import argparse


class Formator(AstNodeVistor):
    def __init__(self, tree, tight=False):
        self.tree = tree
        self.level = 0
        self.tight = tight

    def output(self, content):
        print(content, end='')

    def newline(self):
        if not self.tight:
            print()
        else:
            self.output(' ')

    def indent(self):
        if not self.tight:
            self.output('    ' * self.level)

    def branch(self, stat):
        if type(stat) == BlockStat:
            self.output(f' ')
            self.visit(stat)
        else:
            self.output(f':')
            self.newline()
            self.level += 1
            self.statement(stat, newline=False)
            self.level -= 1

    def statement(self, stat, newline=True):
        self.indent()
        self.visit(stat)
        if self.tight:
            self.output(';')
        if newline:
            self.newline()

    def visit_Program(self, node: Program):
        for stat in node.stats:
            self.statement(stat)

    def visit_EmptyStat(self, node: EmptyStat):
        self.output(';')

    def visit_BlockStat(self, node: BlockStat):
        self.output('{')
        self.newline()
        self.level += 1
        for stat in node.stats:
            self.statement(stat)
        self.level -= 1
        self.indent()
        self.output('}')

    def visit_VarDeclStat(self, node: VarDeclStat):
        self.output('const ' if node.const else 'var ')
        for i in range(0, len(node.names) - 1):
            self.output(node.names[i].identifier)
            self.output(', ')
        self.output(node.names[-1].identifier)
        if node.exprs:
            self.output(' = ')
            for i in range(0, len(node.exprs) - 1):
                self.visit(node.exprs[i])
                self.output(', ')
            self.visit(node.exprs[-1])

    def visit_IfStat(self, node: IfStat):
        self.output('if ')
        self.visit(node.cond_exprs[0])
        self.branch(node.stats[0])

        i = 1
        while i < len(node.cond_exprs) - 1:
            self.newline()
            self.indent()
            self.output('elif ')
            self.visit(node.cond_exprs[i])
            self.branch(node.stats[i])
            i += 1

        if i < len(node.cond_exprs):
            expr = node.cond_exprs[i]
            if type(expr) == Bool and expr.value == 'true':
                self.newline()
                self.indent()
                self.output('else')
                self.branch(node.stats[-1])

    def visit_SwitchStat(self, node: SwitchStat):
        raise Exception('TODO: not implement!')

    def visit_RepeatStat(self, node: RepeatStat):
        raise Exception('TODO: not implement!')

    def visit_WhileStat(self, node: WhileStat):
        self.output(f'while ')
        self.visit(node.expr)
        self.branch(node.stat)

    def visit_ForloopStat(self, node: ForloopStat):
        self.output(f'for ')
        self.visit(node.var_name)
        self.output(f' is ')
        self.visit(node.start_expr)
        self.output(f', ')
        self.visit(node.end_expr)
        if node.step_expr:
            self.output(f', ')
            self.visit(node.step_expr)
        self.branch(node.stat)

    def visit_ForeachStat(self, node: ForeachStat):
        raise Exception('TODO: not implement!')

    def visit_BreakStat(self, node: BreakStat):
        self.output(f'break')

    def visit_ContinueStat(self, node: ContinueStat):
        self.output(f'continue')

    def visit_ReturnStat(self, node: ReturnStat):
        raise Exception('TODO: not implement!')

    def visit_AssignStat(self, node: AssignStat):
        for i in range(len(node.left_exprs) - 1):
            self.visit(node.left_exprs[i])
            self.output(f', ')
        self.visit(node.left_exprs[-1])

        if node.right_exprs:
            self.output(f' = ')
            for i in range(len(node.right_exprs) - 1):
                self.visit(node.right_exprs[i])
                self.output(f', ')
            self.visit(node.right_exprs[-1])

    def visit_CompoundAssignStat(self, node: CompoundAssignStat):
        self.visit(node.left_expr)
        self.output(f' {node.operator.value} ')
        self.visit(node.right_expr)

    def visit_FuncDef(self, node: FuncDef):
        raise Exception('TODO: not implement!')

    def visit_FuncCall(self, node: FuncCall):
        self.visit(node.func_expr)
        self.output(f'(')
        if node.arg_exprs:
            for i in range(len(node.arg_exprs) - 1):
                self.visit(node.arg_exprs[i])
                self.output(f', ')
            self.visit(node.arg_exprs[-1])
        self.output(f')')

    def visit_SelectExpr(self, node: SelectExpr):
        self.visit(node.cond)
        self.output(f' ? ')
        self.visit(node.expr1)
        self.output(f' : ')
        self.visit(node.expr2)

    def visit_BinOpExpr(self, node: BinOpExpr):
        self.visit(node.left_expr)
        self.output(f' {node.operator.value} ')
        self.visit(node.right_expr)

    def visit_UniOpExpr(self, node: UniOpExpr):
        self.output(node.operator.value)
        self.visit(node.expr)

    def visit_ListCtorExpr(self, node: ListCtorExpr):
        raise Exception('TODO: not implement!')

    def visit_MapCtorExpr(self, node: MapCtorExpr):
        raise Exception('TODO: not implement!')

    def visit_SetCtorExpr(self, node: SetCtorExpr):
        raise Exception('TODO: not implement!')

    def visit_AccessExpr(self, node: AccessExpr):
        raise Exception('TODO: not implement!')

    def visit_Name(self, node: Name):
        self.output(node.identifier)

    def visit_Num(self, node: Num):
        self.output(node.value)

    def visit_String(self, node: String):
        self.output(f"'{node.value}'")

    def visit_Bool(self, node: Bool):
        self.output(node.value)

    def visit_Null(self, node: Null):
        self.output('null')

    def format(self):
        self.visit(self.tree)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='toylang formator')
    parser.add_argument('file', help='source file')
    parser.add_argument('--tight', action='store_true', help='tight mode')
    args = parser.parse_args()

    with open(args.file, 'r', encoding='utf-8') as f:
        code = f.read()

    lexer = Lexer(code)
    parser = Parser(lexer)
    tree = parser.parse()

    formator = Formator(tree, tight=args.tight)
    formator.format()
