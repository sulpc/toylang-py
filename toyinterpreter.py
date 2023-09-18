# -*- coding: utf-8 -*-
"""
toylang interpreter
"""
from toyconfig import *
from toyerror import *
from toylexer import *
from toyparser import *
from toyast import *
from toydisplayer import *
from toyanalyzer import *
from toyvalue import *

import argparse

class ARType(Enum):
    PROGRAM   = 'PROGRAM'
    FUNC      = 'FUNC'
    BLOCK     = 'BLOCK'
    FOR       = 'FOR'


class ActivationRecord:
    def __init__(self, name):
        self.name = name
        self.members = {}
        self.outer = None
        self.nesting_level = 0

    def __str__(self) -> str:
        lines = [f'{self.nesting_level}: {self.name}']
        for name, val in self.members.items():
            lines.append(f'    {name:<20}: {val.type():<7}: {val}')
        return '==========================================\n' + 'ACTIVATION RECORD:\n' + '\n'.join(lines) + '\n=========================================='

    def __repr__(self):
        return self.__str__()

    def __setitem__(self, key, value):
        self.members[key] = value

    def __getitem__(self, key):
        return self.members[key]

    def get(self, key):
        return self.members.get(key)

    def has(self, key):
        return key in self.members

    def init_builtins(self):
        builtin_typevalues_init(self.members)


class CallStack:
    def __init__(self):
        self.stack = []
        self.current_ar = None
        self.current_level = 0

    def push(self, ar: ActivationRecord):
        ar.outer = self.current_ar
        ar.nesting_level = self.current_level + 1
        self.stack.append(ar)
        self.current_ar = ar
        self.current_level += 1

    def pop(self) -> ActivationRecord:
        self.current_level -= 1
        self.current_ar = self.current_ar.outer
        return self.stack.pop()

    def __str__(self):
        s = '\n'.join(repr(ar) for ar in reversed(self.stack))
        return f'CALL STACK:\n{s}\n'


class Interpreter(AstNodeVistor):
    def __init__(self):
        self.call_stack = CallStack()

        ar = ActivationRecord('__global')
        ar.init_builtins()
        self.enter_ar(ar)

    def error(self, position, message):
        raise InterpreterError(position, message)

    def log(self, msg):
        if CONFIG_USE_INTERPRETER_LOG:
            print(msg)

    def enter_ar(self, ar: ActivationRecord):
        self.call_stack.push(ar)
        self.log(f'enter ar: {ar.name}')
        self.log(self.call_stack)

    def exit_ar(self):
        self.log(f'leave: {self.call_stack.current_ar.name}')
        self.log(self.call_stack)
        self.call_stack.pop()

    def visit_Program(self, node: Program):
        # ar = ActivationRecord('program')
        # ar.init_builtins()
        # self.enter_ar(ar)
        for stat in node.stats:
            self.visit(stat)
        # self.exit_ar()

    def visit_EmptyStat(self, node: EmptyStat):
        pass

    def visit_BlockStat(self, node: BlockStat):
        ar = ActivationRecord('block')
        self.enter_ar(ar)
        for stat in node.stats:
            self.visit(stat)
        self.exit_ar()

    def visit_VarDeclStat(self, node: VarDeclStat):
        for i in range(len(node.names)):
            name = node.names[i]
            right_expr = node.exprs[i] if node.exprs and i < len(node.exprs) else None
            self.call_stack.current_ar[name.identifier] = self.visit(right_expr) if right_expr else NullValue()

    def visit_IfStat(self, node: IfStat):
        for cond_expr, stat in zip(node.cond_exprs, node.stats):
            cond_value = OpImpl.value_to_bool(self.visit(cond_expr))
            if cond_value._val:
                self.visit(stat)
                return

    def visit_SwitchStat(self, node: SwitchStat):
        switch_val = self.visit(node.expr)
        for case_expr, case_stat in zip(node.case_exprs, node.case_stats):
            case_val = self.visit(case_expr)

            if OpImpl.eq(switch_val, case_val)._val:
                self.visit(case_stat)
                return

        if node.default_stat:
            self.visit(node.default_stat)

    def visit_RepeatStat(self, node: RepeatStat):
        pass

    def visit_WhileStat(self, node: WhileStat):
        pass

    def visit_ForloopStat(self, node: ForloopStat):
        pass

    def visit_ForeachStat(self, node: ForeachStat):
        pass

    def visit_BreakStat(self, node: BreakStat):
        pass

    def visit_ContinueStat(self, node: ContinueStat):
        pass

    def visit_PrintStat(self, node: PrintStat):
        for stat in node.exprs:
            print(self.visit(stat), end=' ')
        print()

    def visit_AssignStat(self, node: AssignStat):
        for i in range(len(node.left_exprs)):
            left_expr = node.left_exprs[i]
            right_expr = node.right_exprs[i] if i < len(node.right_exprs) else None

            if type(left_expr) == Name:      # NAME = .*
                self.call_stack.current_ar[left_expr.identifier] = self.visit(right_expr) if right_expr else NullValue()
            else:                            # NAME.NAME | NAME[expr]
                # TODO
                self.error(node.position, 'TODO: access')

    def visit_CompoundAssignStat(self, node: CompoundAssignStat):
        left_expr = node.left_expr
        right_expr = node.right_expr
        if type(left_expr) == Name:      # NAME += .*
            if node.operator in BINOP_IMPL_TABLE:
                try:
                    self.call_stack.current_ar[left_expr.identifier] = BINOP_IMPL_TABLE[node.operator](self.visit(left_expr), self.visit(right_expr))
                except TypeError:
                    self.error(node.position, ErrorInfo.op_used_on_wrong_type(node.operator.value))
            else:
                self.error(node.position, ErrorInfo.op_not_supported(node.operator.value))
        else:
            # TODO
            self.error(node.position, 'TODO: access')

    def visit_SelectExpr(self, node: SelectExpr):
        cond_val = OpImpl.value_to_bool(self.visit(node.cond))
        if cond_val._val:
            return self.visit(node.expr1)
        else:
            return self.visit(node.expr2)

    def visit_BinOpExpr(self, node: BinOpExpr):
        left_val = self.visit(node.left_expr)
        right_val = self.visit(node.right_expr)
        operator = node.operator

        reverse = False
        if operator == TokenType.NE:
            reverse = True
            operator = TokenType.EQ
        elif operator == TokenType.GE:
            reverse = True
            operator = TokenType.LT
        elif operator == TokenType.GT:
            reverse = True
            operator = TokenType.LE

        if operator in BINOP_IMPL_TABLE:
            try:
                result = BINOP_IMPL_TABLE[operator](left_val, right_val)
                if reverse:    # must be a bool
                    result._val = not result._val
            except TypeError:
                self.error(node.position, ErrorInfo.op_used_on_wrong_type(operator.value))
            return result
        else:
            self.error(node.position, ErrorInfo.op_not_supported(operator.value))

    def visit_UniOpExpr(self, node: UniOpExpr):
        expr = node.expr
        expr_value = self.visit(expr)

        if node.operator in UNIOP_IMPL_TABLE:
            try:
                result = UNIOP_IMPL_TABLE[node.operator](expr_value)
            except TypeError:
                self.error(node.position, ErrorInfo.op_used_on_wrong_type(node.operator.value))
            return result
        else:
            self.error(node.position, ErrorInfo.op_not_supported(node.operator.value))

    def visit_Name(self, node: Name):
        identifier = node.identifier
        ar = self.call_stack.current_ar
        while ar is not None:
            value = ar.get(identifier)
            if value is not None:
                return value
            else:
                ar = ar.outer
        self.error(node.position, ErrorInfo.name_not_valid(identifier))

    def visit_Num(self, node: Num):
        if node.is_int:
            return NumValue(int(node.value), is_int=True)
        else:
            return NumValue(float(node.value), is_int=False)

    def visit_String(self, node: String):
        return StringValue(node.value)

    def visit_Bool(self, node: Bool):
        return BoolValue(True if node.value == 'true' else False)

    def visit_Null(self, node: Null):
        return NullValue()

    def interpret(self, tree):
        self.visit(tree)


if __name__ == '__main__':
    code = '''
    var i = 1
    print('i =', i)
    if i > 1
        print('i>1')
    else
        print('i<1')

    i += 1
    print('i =', i)
    switch i
    case 1:
        print('in case 1')
    case 2 {
        print('in case 2')
    }
    default
        print('default')
    '''

    parser = argparse.ArgumentParser(description='toylang interpreter')
    # parser.add_argument('inputfile', help='source file')
    parser.add_argument('--repl', action='store_true', help='run in repl mode')
    args = parser.parse_args()

    interpreter = Interpreter()

    if args.repl:
        while True:
            try:
                text = input('>>> ')
                text = text.strip(' \n')
                if len(text) == 0:
                    continue
                elif text == 'exit':
                    break
                elif text == 'info':
                    print(interpreter.call_stack)
                    continue

                lexer = Lexer(text)
                parser = Parser(lexer)
                tree = parser.parse()

                displayer = Displayer(tree, 'ast.html')
                displayer.display()

                # analyzer = SemanticAnalyzer(tree)
                # analyzer.analysis()

                # stat or expr?
                interpreter.interpret(tree)
            except (LexerError, ParserError, SemanticError, InterpreterError) as e:
                print(e)
    else:
        try:
            lexer = Lexer(code)
            parser = Parser(lexer)
            tree = parser.parse()

            displayer = Displayer(tree, 'ast.html')
            displayer.display()

            analyzer = SemanticAnalyzer(tree)
            analyzer.analysis()

            # interpreter = Interpreter()
            interpreter.interpret(tree)
        except (LexerError, ParserError, SemanticError, InterpreterError) as e:
            print(e)
