# -*- coding: utf-8 -*-
"""
toylang ast displayer
"""

from pyecharts import options as opts
from pyecharts.charts import Tree
import os
from toyast import *


LOCAL_ECHARTS = False


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

        vars = {'name': 'vars', 'children': []}
        for var in node.vars:
            vars['children'].append(self.visit(var))
        data['children'].append(vars)

        if node.exprs is not None:
            values = {'name': 'values', 'children': []}
            for expr in node.exprs:
                values['children'].append(self.visit(expr))
            data['children'].append(values)
        return data

    def visit_IfStat(self, node: IfStat):
        data = {'name': 'if', 'children': []}
        for cond, stat in zip(node.conds, node.stats):
            data['children'].append({'name': 'cond', 'children': [self.visit(cond), self.visit(stat)]})
        return data

    def visit_SwitchStat(self, node: SwitchStat):
        data = {'name': 'switch', 'children': []}
        data['children'].append({'name': 'expr', 'children': [self.visit(node.expr)]})
        for case, stat in zip(node.cases, node.stats):
            data['children'].append({'name': 'case', 'children': [self.visit(case), self.visit(stat)]})
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
        data['children'].append({'name': 'var', 'children': [self.visit(node.var_name)]})

        rg = {'name': 'range', 'children': []}
        rg['children'].append({'name': 'start', 'children': [self.visit(node.start_expr)]})
        rg['children'].append({'name': 'end', 'children': [self.visit(node.end_expr)]})
        if node.step_expr is not None:
            rg['children'].append({'name': 'step', 'children': [self.visit(node.step_expr)]})
        data['children'].append(rg)

        data['children'].append({'name': 'do', 'children': [self.visit(node.stat)]})
        return data

    def visit_ForeachStat(self, node: ForeachStat):
        data = {'name': 'foreach', 'children': []}

        vars = {'name': 'vars', 'children': []}
        vars['children'].append(self.visit(node.key_name))
        if node.val_name is not None:
            vars['children'].append(self.visit(node.val_name))
        data['children'].append(vars)

        data['children'].append({'name': 'in', 'children': [self.visit(node.expr)]})
        data['children'].append({'name': 'do', 'children': [self.visit(node.stat)]})
        return data

    def visit_BreakStat(self, node: BreakStat):
        data = {'name': 'break'}
        return data

    def visit_ContinueStat(self, node: ContinueStat):
        data = {'name': 'continue'}
        return data

    def visit_PrintStat(self, node: PrintStat):
        data = {'name': 'print', 'children': []}
        for expr in node.exprs:
            data['children'].append(self.visit(expr))
        return data

    def visit_AssignStat(self, node: AssignStat):
        data = {'name': '=', 'children': []}
        left = {'name': 'left', 'children': []}
        right = {'name': 'right', 'children': []}
        for expr in node.left_exprs:
            left['children'].append(self.visit(expr))
        for expr in node.right_exprs:
            right['children'].append(self.visit(expr))
        data['children'].append(left)
        data['children'].append(right)
        return data

    def visit_CompoundAssignStat(self, node: CompoundAssignStat):
        data = {'name': f'{node.operator.value}', 'children': []}
        data['children'].append(self.visit(node.left_expr))
        data['children'].append(self.visit(node.right_expr))
        return data

    def visit_SelectExpr(self, node: SelectExpr):
        data = {'name': '?:', 'children': []}
        data['children'].append(self.visit(node.cond))
        data['children'].append(self.visit(node.expr1))
        data['children'].append(self.visit(node.expr2))
        return data

    def visit_BinOpExpr(self, node: BinOpExpr):
        data = {'name': f'{node.operator.value}', 'children': []}
        data['children'].append(self.visit(node.left))
        data['children'].append(self.visit(node.right))
        return data

    def visit_UniOpExpr(self, node: UniOpExpr):
        data = {'name': f'{node.operator.value}', 'children': []}
        data['children'].append(self.visit(node.expr))
        return data

    def visit_Name(self, node: Name):
        data = {'name': f'{node.name}'}
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
            if LOCAL_ECHARTS:
                content[5] = '    <script type="text/javascript" src="../../echarts.min.js"></script>\n'
        with open(f'{self.filename}', 'w') as fout:
            fout.writelines(content)
        os.remove('html')
