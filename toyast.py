# -*- coding: utf-8 -*-
"""
toylang ast define
"""

from toytoken import *


class AST:
    pass


class Program(AST):
    def __init__(self, stats):
        self.stats = stats


class AssignStat(AST):
    def __init__(self, vars, exprs, position):
        self.vars = vars
        self.exprs = exprs
        self.position = position


class CompoundAssignStat(AST):
    def __init__(self, op_type, var, expr, position):
        self.op_type = op_type
        self.var = var
        self.expr = expr
        self.position = position


class BlockStat(AST):
    def __init__(self, stats, position):
        self.stats = stats
        self.position = position


class IfStat(AST):
    def __init__(self, conds, stats, position):
        self.conds = conds
        self.stats = stats
        self.position = position


class SwitchStat(AST):
    def __init__(self, expr, cases, stats, position):
        self.expr = expr
        self.cases = cases
        self.stats = stats
        self.position = position


class RepeatStat(AST):
    def __init__(self, expr, stat, position):
        self.expr = expr
        self.stat = stat
        self.position = position


class WhileStat(AST):
    def __init__(self, expr, stat, position):
        self.expr = expr
        self.stat = stat
        self.position = position


class ForloopStat(AST):
    def __init__(self, identifier, start_expr, stop_expr, step_expr, stat, position):
        self.identifier = identifier
        self.start_expr = start_expr
        self.stop_expr = stop_expr
        self.step_expr = step_expr
        self.stat = stat
        self.position = position


class ForeachStat(AST):
    def __init__(self, key_id, value_id, expr, stat, position):
        self.key_id = key_id
        self.value_id = value_id
        self.expr = expr
        self.stat = stat
        self.position = position


class BreakStat(AST):
    def __init__(self, position):
        self.position = position


class ContinueStat(AST):
    def __init__(self, position):
        self.position = position


class PrintStat(AST):
    def __init__(self, exprs, position):
        self.exprs = exprs
        self.position = position


class EmptyStat(AST):
    pass


class SelectExpr(AST):
    def __init__(self, cond, expr1, expr2, position):
        self.cond = cond
        self.expr1 = expr1
        self.expr2 = expr2
        self.position = position


class UniOpExpr(AST):
    def __init__(self, op_type, expr, position):
        self.op_type = op_type
        self.expr = expr
        self.position = position


class BinOpExpr(AST):
    def __init__(self, op_type, left, right, position):
        self.op_type = op_type
        self.left = left
        self.right = right
        self.position = position


class Num(AST):
    def __init__(self, value, position):
        self.value = value
        self.position = position


class String(AST):
    def __init__(self, value, position):
        self.value = value
        self.position = position


class Bool(AST):
    def __init__(self, value, position):
        self.value = value
        self.position = position


class Null(AST):
    def __init__(self, position):
        self.position = position


class Identifier(AST):
    def __init__(self, value, position):
        self.value = value
        self.position = position


class AstNodeVistor():
    def visit(self, node):
        """dispatches
        """
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visitor)
        return visitor(node)

    def generic_visitor(self, node):
        raise Exception(f'No visit_{type(node).__name__} method')
