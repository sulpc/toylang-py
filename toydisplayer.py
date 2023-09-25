# -*- coding: utf-8 -*-
"""
toylang ast displayer
"""
from toyast import *

from pyecharts import options as opts
from pyecharts.charts import Tree
import os


CONFIG_USE_LOCAL_ECHARTS = True


class Displayer(AstNodeVistor):
    def __init__(self, tree, filename):
        self.tree = tree
        self.filename = filename

    def visit_Program(self, node: Program):
        data = {'name': 'Program', 'children': []}
        for stat in node.stats:
            data['children'].append(self.visit(stat))
        return data

    def visit_EmptyStat(self, node: EmptyStat):
        data = {'name': 'empty'}
        return data

    def visit_BlockStat(self, node: BlockStat):
        data = {'name': 'block', 'children': []}
        for stat in node.stats:
            data['children'].append(self.visit(stat))
        return data

    def visit_VarDeclStat(self, node: VarDeclStat):
        data = {'name': 'decl', 'children': []}
        # names
        names = {'name': 'names', 'children': []}
        for name in node.names:
            names['children'].append(self.visit(name))
        data['children'].append(names)
        # values
        if node.exprs is not None:
            values = {'name': 'values', 'children': []}
            for expr in node.exprs:
                values['children'].append(self.visit(expr))
            data['children'].append(values)
        return data

    def visit_IfStat(self, node: IfStat):
        data = {'name': 'if', 'children': []}
        for cond, stat in zip(node.cond_exprs, node.stats):
            data['children'].append({'name': 'cond', 'children': [self.visit(cond), self.visit(stat)]})
        return data

    def visit_SwitchStat(self, node: SwitchStat):
        data = {'name': 'switch', 'children': []}
        data['children'].append({'name': 'expr', 'children': [self.visit(node.expr)]})
        # cases
        for case, stat in zip(node.case_exprs, node.case_stats):
            data['children'].append({'name': 'case', 'children': [self.visit(case), self.visit(stat)]})
        # default
        data['children'].append({'name': 'default', 'children': [self.visit(node.default_stat)]})
        return data

    def visit_RepeatStat(self, node: RepeatStat):
        data = {'name': 'repeat', 'children': []}
        data['children'].append({'name': 'do', 'children': [self.visit(node.stat)]})
        data['children'].append({'name': 'until', 'children': [self.visit(node.expr)]})
        return data

    def visit_WhileStat(self, node: WhileStat):
        data = {'name': 'while', 'children': []}
        data['children'].append({'name': 'do', 'children': [self.visit(node.stat)]})
        data['children'].append({'name': 'while', 'children': [self.visit(node.expr)]})
        return data

    def visit_ForloopStat(self, node: ForloopStat):
        data = {'name': 'forloop', 'children': []}
        data['children'].append({'name': 'idx', 'children': [self.visit(node.var_name)]})
        # loop range
        rg = {'name': 'range', 'children': []}
        rg['children'].append({'name': 'start', 'children': [self.visit(node.start_expr)]})
        rg['children'].append({'name': 'end', 'children': [self.visit(node.end_expr)]})
        if node.step_expr is not None:
            rg['children'].append({'name': 'step', 'children': [self.visit(node.step_expr)]})
        data['children'].append(rg)
        # stat
        data['children'].append({'name': 'do', 'children': [self.visit(node.stat)]})
        return data

    def visit_ForeachStat(self, node: ForeachStat):
        data = {'name': 'foreach', 'children': []}
        # k/v var name
        kv = {'name': 'k/v', 'children': []}
        kv['children'].append(self.visit(node.key_name))
        if node.val_name is not None:
            kv['children'].append(self.visit(node.val_name))
        data['children'].append(kv)
        # in & do
        data['children'].append({'name': 'in', 'children': [self.visit(node.expr)]})
        data['children'].append({'name': 'do', 'children': [self.visit(node.stat)]})
        return data

    def visit_BreakStat(self, node: BreakStat):
        data = {'name': 'break'}
        return data

    def visit_ContinueStat(self, node: ContinueStat):
        data = {'name': 'continue'}
        return data

    def visit_ReturnStat(self, node: ReturnStat):
        data = {'name': 'return', 'children': []}
        if node.expr:
            data['children'].append(self.visit(node.expr))
        else:
            data['children'].append({'name': ';'})
        return data

    def visit_AssignStat(self, node: AssignStat):
        data = {'name': '=', 'children': []}
        lexprs = {'name': 'lexprs', 'children': []}
        rexprs = {'name': 'rexprs', 'children': []}
        for expr in node.left_exprs:
            lexprs['children'].append(self.visit(expr))
        for expr in node.right_exprs:
            rexprs['children'].append(self.visit(expr))
        data['children'].append(lexprs)
        data['children'].append(rexprs)
        return data

    def visit_CompoundAssignStat(self, node: CompoundAssignStat):
        data = {'name': f'{node.operator.value}', 'children': []}
        data['children'].append(self.visit(node.left_expr))
        data['children'].append(self.visit(node.right_expr))
        return data

    def visit_FuncDef(self, node: FuncDef):
        data = {'name': f'func', 'children': []}
        # params
        params = {'name': f'params', 'children': []}
        if node.param_names:
            for name in node.param_names:
                params['children'].append(self.visit(name))
        if node.vararg:
            params['children'].append({'name': '...'})
        # stats
        body = {'name': f'body', 'children': []}
        for stat in node.body:
            body['children'].append(self.visit(stat))
        data['children'].append(params)
        data['children'].append(body)
        return data

    def visit_FuncCall(self, node: FuncCall):
        data = {'name': 'call', 'children': []}
        data['children'].append({'name': 'func', 'children': [self.visit(node.func_expr)]})
        if node.arg_exprs:
            args = {'name': 'args', 'children': []}
            for expr in node.arg_exprs:
                args['children'].append(self.visit(expr))
            data['children'].append(args)
        return data

    def visit_SelectExpr(self, node: SelectExpr):
        data = {'name': '?:', 'children': []}
        data['children'].append(self.visit(node.cond))
        data['children'].append(self.visit(node.expr1))
        data['children'].append(self.visit(node.expr2))
        return data

    def visit_BinOpExpr(self, node: BinOpExpr):
        data = {'name': f'{node.operator.value}', 'children': []}
        data['children'].append(self.visit(node.left_expr))
        data['children'].append(self.visit(node.right_expr))
        return data

    def visit_UniOpExpr(self, node: UniOpExpr):
        data = {'name': f'{node.operator.value}', 'children': []}
        data['children'].append(self.visit(node.expr))
        return data

    def visit_ListCtorExpr(self, node: ListCtorExpr):
        data = {'name': f'list', 'children': []}
        if node.exprs:
            for expr in node.exprs:
                data['children'].append(self.visit(expr))
        return data

    def visit_MapCtorExpr(self, node: MapCtorExpr):
        data = {'name': f'map', 'children': []}
        for key, value in zip(node.key_exprs, node.value_exprs):
            pair = {'name': f'pair', 'children': []}
            pair['children'].append(self.visit(key))
            if value is not None:
                pair['children'].append(self.visit(value))
            data['children'].append(pair)
        return data

    def visit_SetCtorExpr(self, node: SetCtorExpr):
        data = {'name': f'set', 'children': []}
        if node.exprs:
            for expr in node.exprs:
                data['children'].append(self.visit(expr))
        return data

    def visit_AccessExpr(self, node: AccessExpr):
        data = {'name': f'{"." if node.dot else "[]"}', 'children': []}
        data['children'].append(self.visit(node.expr))
        data['children'].append(self.visit(node.field_expr))
        return data

    def visit_Name(self, node: Name):
        data = {'name': f'{node.identifier}'}
        return data

    def visit_Num(self, node: Num):
        data = {'name': f'<{node.value}>'}
        return data

    def visit_String(self, node: String):
        data = {'name': f'`{node.value}`'}
        return data

    def visit_Bool(self, node: Bool):
        data = {'name': f'{node.value}'}
        return data

    def visit_Null(self, node: Null):
        data = {'name': f'null'}
        return data

    def display(self):
        data = self.visit(self.tree)
        c = (
            Tree()
            .add(
                series_name="",         # name
                data=[data],            # data
                initial_tree_depth=-1,  # all expand
                orient="TB",            # top-to-bottom
                label_opts=opts.LabelOpts(
                    position="top",
                    vertical_align="middle",
                ),
            )
            .set_global_opts(title_opts=opts.TitleOpts(title="Tree"))
            .render('html')
        )
        # modify js reference to local
        with open('html', 'r') as fin:
            content = fin.readlines()
            content[4] = '    <title>Tree</title>\n'
            if CONFIG_USE_LOCAL_ECHARTS:
                content[5] = '    <script type="text/javascript" src="../../echarts.min.js"></script>\n'
        with open(f'{self.filename}', 'w') as fout:
            fout.writelines(content)
        os.remove('html')
