# -*- coding: utf-8 -*-
"""
toylang ast define

name style:
- `.*stat`: a Stat ast
- `.*expr`: a Expr ast
- `.*stats`: a list of Stat ast
- `.*exprs`: a list of Expr ast
- `.*name`: a Name ast
- `value`: a value
- `identifier`: a string identifier
"""
from toytoken import *

class AST:
    pass


class EmptyStat(AST):
    pass


class Program(AST):
    def __init__(self, stats):
        self.stats = stats


class BlockStat(AST):
    def __init__(self, stats, position):
        self.stats = stats
        self.position = position


class VarDeclStat(AST):
    def __init__(self, names, exprs, const, position):
        self.names = names
        self.exprs = exprs
        self.const = const
        self.position = position


class IfStat(AST):
    def __init__(self, cond_exprs, stats, position):
        self.cond_exprs = cond_exprs
        self.stats = stats
        self.position = position


class SwitchStat(AST):
    def __init__(self, expr, case_exprs, case_stats, default_stat, position):
        self.expr = expr
        self.case_exprs = case_exprs
        self.case_stats = case_stats
        self.default_stat = default_stat
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
    def __init__(self, var_name, start_expr, end_expr, step_expr, stat, position):
        self.var_name = var_name
        self.start_expr = start_expr
        self.end_expr = end_expr
        self.step_expr = step_expr
        self.stat = stat
        self.position = position


class ForeachStat(AST):
    def __init__(self, key_name, val_name, expr, stat, position):
        self.key_name = key_name
        self.val_name = val_name
        self.expr = expr
        self.stat = stat
        self.position = position


class BreakStat(AST):
    def __init__(self, position):
        self.position = position


class ContinueStat(AST):
    def __init__(self, position):
        self.position = position


class ReturnStat(AST):
    def __init__(self, expr, position):
        self.expr = expr
        self.position = position


class AssignStat(AST):
    def __init__(self, left_exprs, right_exprs, position):
        self.left_exprs = left_exprs
        self.right_exprs = right_exprs
        self.position = position


class CompoundAssignStat(AST):
    def __init__(self, operator, left_expr, right_expr, position):
        self.operator = operator
        self.left_expr = left_expr
        self.right_expr = right_expr
        self.position = position


class FuncDef(AST):
    def __init__(self, param_names, vararg, body, position):
        self.param_names = param_names
        self.vararg = vararg
        self.body = body
        self.position = position


class FuncCall(AST):
    def __init__(self, func_expr, arg_exprs, position):
        self.func_expr = func_expr
        self.arg_exprs = arg_exprs
        self.position = position


class SelectExpr(AST):
    def __init__(self, cond, expr1, expr2, position):
        self.cond = cond
        self.expr1 = expr1
        self.expr2 = expr2
        self.position = position


class BinOpExpr(AST):
    def __init__(self, operator, left_expr, right_expr, position):
        """BinOpExpr

        operator is like TokenType.EQ, ...
        """
        self.operator = operator
        self.left_expr = left_expr
        self.right_expr = right_expr
        self.position = position


class UniOpExpr(AST):
    def __init__(self, operator, expr, position):
        self.operator = operator
        self.expr = expr
        self.position = position


class ListCtorExpr(AST):
    def __init__(self, exprs, position):
        self.exprs = exprs
        self.position = position


class MapCtorExpr(AST):
    def __init__(self, key_exprs, value_exprs, position):
        self.key_exprs = key_exprs
        self.value_exprs = value_exprs
        self.position = position


class AccessExpr(AST):
    def __init__(self, expr, key_expr, dot: bool, position):
        self.expr = expr
        self.key_expr = key_expr
        self.dot = dot
        self.position = position


class Name(AST):
    def __init__(self, identifier, position):
        self.identifier = identifier
        self.position = position


class Num(AST):
    def __init__(self, value, is_int, position):
        self.value = value
        self.is_int = is_int
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


class AstNodeVistor():
    def visit(self, node):
        """dispatches
        """
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visitor)
        return visitor(node)

    def generic_visitor(self, node):
        raise Exception(f'No visit_{type(node).__name__} method')
