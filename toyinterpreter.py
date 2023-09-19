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
from toyvalue import *
from toylib import *

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
            lines.append(f'    {name:<20}: {val.type():<12}: {val}')
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
        ToyLib.register(self.members)


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
            try:
                cond_value = OpImpl.value_to_bool(self.visit(cond_expr))
            except ToyTypeError:
                self.error(cond_expr.position, ErrorInfo.expr_convert_bool_error())
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
        while True:
            self.visit(node.stat)
            try:
                expr_val = OpImpl.value_to_bool(self.visit(node.expr))
            except ToyTypeError:
                self.error(node.expr.position, ErrorInfo.expr_convert_bool_error())
            if expr_val._val:
                break

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

    def visit_AssignStat(self, node: AssignStat):
        for i in range(len(node.left_exprs)):
            left_expr = node.left_exprs[i]
            right_val = self.visit(node.right_exprs[i]) if i < len(node.right_exprs) else NullValue()

            if type(left_expr) == Name:      # NAME = .*
                self.set_Name(left_expr, right_val)
            else:                            # NAME.NAME | NAME[expr]
                # TODO
                self.error(node.position, 'TODO: access')

    def visit_CompoundAssignStat(self, node: CompoundAssignStat):
        left_expr = node.left_expr
        right_expr = node.right_expr
        if type(left_expr) == Name:      # NAME += .*
            if node.operator in BINOP_IMPL_TABLE:
                try:
                    new_val = BINOP_IMPL_TABLE[node.operator](self.visit(left_expr), self.visit(right_expr))
                except ToyTypeError:
                    self.error(node.position, ErrorInfo.op_used_on_wrong_type(node.operator.value))
                self.set_Name(left_expr, new_val)
            else:
                self.error(node.position, ErrorInfo.op_not_implemented(node.operator.value))
        else:
            # TODO
            self.error(node.position, 'TODO: access')

    def visit_FuncCall(self, node: FuncCall):
        func_val = self.visit(node.func_expr)
        if type(func_val) == HostFunctionValue:
            args = []
            if node.arg_exprs:
                for arg_expr in node.arg_exprs:
                    args.append(self.visit(arg_expr))
            result = func_val._func(args)
            if result:
                assert(type(result) == list)
                # TODO: when function return multi values
                return result[0]
            else:
                return NullValue()
        else:
            self.error(node.position, "TODO: func call")

    def visit_SelectExpr(self, node: SelectExpr):
        try:
            cond_val = OpImpl.value_to_bool(self.visit(node.cond))
        except ToyTypeError:
            self.error(cond_val.position, ErrorInfo.expr_convert_bool_error())
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
            except ToyTypeError:
                self.error(node.position, ErrorInfo.op_used_on_wrong_type(operator.value))
            return result
        else:
            self.error(node.position, ErrorInfo.op_not_implemented(operator.value))

    def visit_UniOpExpr(self, node: UniOpExpr):
        expr = node.expr
        expr_value = self.visit(expr)

        if node.operator in UNIOP_IMPL_TABLE:
            try:
                result = UNIOP_IMPL_TABLE[node.operator](expr_value)
            except ToyTypeError:
                self.error(node.position, ErrorInfo.op_used_on_wrong_type(node.operator.value))
            return result
        else:
            self.error(node.position, ErrorInfo.op_not_implemented(node.operator.value))

    def visit_Name(self, node: Name):
        identifier = node.identifier
        ar = self.call_stack.current_ar
        while ar is not None:
            value = ar.get(identifier)
            if value is not None:
                return value
            else:
                ar = ar.outer
        self.error(node.position, ErrorInfo.name_not_created(identifier))

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

    def set_Name(self, name: Name, value):
        ar = self.call_stack.current_ar
        while ar is not None:
            if ar.has(name.identifier):
                ar[name.identifier] = value
                return
            else:
                ar = ar.outer
        self.error(name.position, ErrorInfo.name_not_created(name.identifier))

    def set_Field(self, name: Name, field: Value, value: Value):
        pass

    def interpret(self, tree):
        self.visit(tree)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='toylang interpreter')
    parser.add_argument('--src', help='source file')
    parser.add_argument('--repl', action='store_true', help='repl mode')
    args = parser.parse_args()

    interpreter = Interpreter()

    if args.src:
        try:
            with open(args.src, 'r') as f:
                code = f.read()

            lexer = Lexer(code)
            parser = Parser(lexer)
            tree = parser.parse()

            displayer = Displayer(tree, 'ast.html')
            displayer.display()

            interpreter.interpret(tree)
        except (LexerError, ParserError, SemanticError, InterpreterError) as e:
            print(e)
            raise e
    # elif args.repl:
    else:
        text = ''
        while True:
            try:
                line = input('>>> ').strip()

                if len(line) == 0:
                    continue
                elif line == 'exit':
                        break
                elif line[0] == '%':               # exec interepter command
                    line = line[1:].strip()
                    if line == 'info':
                        print(interpreter.call_stack)
                        continue
                    else:
                        print('unknown command')
                        continue
                elif line[-1] == '\\':             # multi-line code
                    text += ' ' + line[:-1].strip()
                    continue
                else:
                    text += ' ' + line

                lexer = Lexer(text)
                text = ''
                parser = Parser(lexer)
                tree = parser.parse()

                displayer = Displayer(tree, 'ast.html')
                displayer.display()

                interpreter.interpret(tree)
            except (LexerError, ParserError, SemanticError, InterpreterError) as e:
                print(e)
                # raise e
