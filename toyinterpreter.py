# -*- coding: utf-8 -*-
"""
toylang interpreter
"""
from toyerror import *
from toylexer import *
from toyparser import *
from toyast import *
from toydisplayer import *
from toyvalue import *
from toylib import *
import toylog

import argparse
from enum import Enum


class ARType(Enum):
    PROGRAM   = 'PROGRAM'
    BLOCK     = 'BLOCK'
    LOOP      = 'LOOP'
    FUNCTION  = 'FUNCTION'


class ARState(Enum):
    NORMAL    = 'NORMAL'
    BREAKED   = 'BREAKED'
    CONTINUED = 'CONTINUED'
    RETURNED  = 'RETURNED'


class ActivationRecord:
    def __init__(self, name, type):
        self.name = name
        self.members = {}       # identifier -> [value, const]
        self.outer = None
        self.nesting_level = 0
        # below used for function and loop
        self.type = type
        self.state = ARState.NORMAL

    def __str__(self) -> str:
        lines = [f'{self.nesting_level}: {self.name} {self.type.value} {self.state.value}']
        for name, vv in self.members.items():
            lines.append(f'    {name:<20}: {vv[0].type():<12}: {vv[0]} {"const" if vv[1] else ""}')
        return 'ACTIVATION RECORD:\n' + '\n'.join(lines)

    def __repr__(self):
        return self.__str__()

    # def __setitem__(self, key, value):
    #     self.members[key] = value

    # def __getitem__(self, key):
    #     return self.members[key]

    def set(self, key, value, const):
        self.members[key] = [value, const]

    def get(self, key):
        vv = self.members.get(key)
        if vv is None:
            return None, None
        else:
            return vv[0], vv[1]

    def has(self, key):
        return key in self.members

    def set_values(self, keys, values, const):
        if len(keys) != len(values):
            raise Exception(f'keys and values must have same length: {len(keys)} != {len(values)}')
        for k, v in zip(keys, values):
            self.members[k] = [v, const]

    def init_builtins(self):
        init_builtin_typevalues(self.set_values)
        ToyLib.register(self.set_values)


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

    def pop(self):
        self.current_level -= 1
        self.current_ar = self.current_ar.outer
        return self.stack.pop()

    def __str__(self):
        s = '\n----------------------------------------\n'.join(repr(ar) for ar in reversed(self.stack))
        return f'CALL STACK:\n========================================\n{s}\n========================================\n'


class Interpreter(AstNodeVistor):
    def __init__(self):
        self.call_stack = CallStack()

        ar = ActivationRecord('__global', type=ARType.PROGRAM)
        ar.init_builtins()
        self.enter_ar(ar)

    def error(self, position, message):
        raise InterpreterError(position, message)

    def enter_ar(self, ar: ActivationRecord):
        self.call_stack.push(ar)
        toylog.debug(f'enter ar: {ar.name}')
        toylog.debug(self.call_stack)

    def exit_ar(self):
        toylog.debug(f'leave: {self.call_stack.current_ar.name}')
        toylog.debug(self.call_stack)
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
        ar = ActivationRecord(f'block<{node.position[0]}:{node.position[1]}>', ARType.BLOCK)
        self.enter_ar(ar)
        for stat in node.stats:
            self.visit(stat)
            if ar.state == ARState.BREAKED:
                ar.state = ARState.NORMAL
                toylog.info(f'[!] {ar.name:<12} pass break')
                break
            elif ar.state == ARState.CONTINUED:
                ar.state = ARState.NORMAL
                toylog.info(f'[!] {ar.name:<12} pass continue')
                break
        self.exit_ar()

    def visit_VarDeclStat(self, node: VarDeclStat):
        for i in range(len(node.names)):
            name = node.names[i]
            right_expr = node.exprs[i] if node.exprs and i < len(node.exprs) else None
            self.decl_Name(name, self.visit(right_expr) if right_expr else NullValue(),
                           const=node.const)

    def visit_IfStat(self, node: IfStat):
        for cond_expr, stat in zip(node.cond_exprs, node.stats):
            try:
                cond_value = OpImpl.value_to_bool(self.visit(cond_expr))
            except BaseError as e:
                self.error(cond_expr.position, ErrorInfo.expr_value_error(e.message))
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
        ar = ActivationRecord(f'repeat<{node.position[0]}:{node.position[1]}>', ARType.LOOP)
        self.enter_ar(ar)
        while True:
            self.visit(node.stat)
            if ar.state == ARState.BREAKED:
                ar.state = ARState.NORMAL
                toylog.info(f'[!] {ar.name:<12} handle break')
                break
            elif ar.state == ARState.CONTINUED:
                ar.state = ARState.NORMAL
                toylog.info(f'[!] {ar.name:<12} handle continue')
                # do nothing
            try:
                expr_val = OpImpl.value_to_bool(self.visit(node.expr))
            except BaseError as e:
                self.error(node.expr.position, ErrorInfo.expr_value_error(e.message))
            if expr_val._val:
                break
        self.exit_ar()

    def visit_WhileStat(self, node: WhileStat):
        ar = ActivationRecord(f'while<{node.position[0]}:{node.position[1]}>', ARType.LOOP)
        self.enter_ar(ar)
        while True:
            try:
                expr_val = OpImpl.value_to_bool(self.visit(node.expr))
            except BaseError as e:
                self.error(node.expr.position, ErrorInfo.expr_value_error(e.message))
            if expr_val._val:
                self.visit(node.stat)
                if ar.state == ARState.BREAKED:
                    ar.state = ARState.NORMAL
                    toylog.info(f'[!] {ar.name:<12} handle break')
                    break
                elif ar.state == ARState.CONTINUED:
                    ar.state = ARState.NORMAL
                    toylog.info(f'[!] {ar.name:<12} handle continue')
                    # do nothing
            else:
                break
        self.exit_ar()

    def visit_ForloopStat(self, node: ForloopStat):
        ar = ActivationRecord(f'for<{node.position[0]}:{node.position[1]}>', ARType.LOOP)
        self.enter_ar(ar)
        # cal start_val, end_val, step_val
        start_val = self.visit(node.start_expr)
        if not OpImpl.is_num(start_val):
            self.error(node.start_expr.position, ErrorInfo.expr_type_error('num'))
        end_val = self.visit(node.end_expr)
        if not OpImpl.is_num(end_val):
            self.error(node.end_expr.position, ErrorInfo.expr_type_error('num'))
        step_val = self.visit(node.step_expr) if node.step_expr else NumValue(1, is_int=True)
        # create index var
        self.decl_Name(node.var_name, start_val, const=True)

        while True:
            val = self.visit(node.var_name)
            if OpImpl.lt(val, end_val)._val:
                self.visit(node.stat)
                if ar.state == ARState.BREAKED:
                    ar.state = ARState.NORMAL
                    toylog.info(f'[!] {ar.name:<12} handle break')
                    break
                elif ar.state == ARState.CONTINUED:
                    ar.state = ARState.NORMAL
                    toylog.info(f'[!] {ar.name:<12} handle continue')
                    # do nothing
                self.set_Name(node.var_name, OpImpl.add(val, step_val), force=True)
            else:
                break

        self.exit_ar()

    def visit_ForeachStat(self, node: ForeachStat):
        ar = ActivationRecord(f'for<{node.position[0]}:{node.position[1]}>', ARType.LOOP)
        self.enter_ar(ar)
        # TODO
        self.exit_ar()

    def visit_BreakStat(self, node: BreakStat):
        ar = self.call_stack.current_ar
        while ar is not None:
            ar.state = ARState.BREAKED
            toylog.info(f'[!] {ar.name:<12} set break')
            if ar.type == ARType.LOOP:
                return
            elif ar.type == ARType.FUNCTION:
                break
            ar = ar.outer
        self.error(node.position, ErrorInfo.invalid_syntax('break'))

    def visit_ContinueStat(self, node: ContinueStat):
        ar = self.call_stack.current_ar
        while ar is not None:
            ar.state = ARState.CONTINUED
            toylog.info(f'[!] {ar.name:<12} set continue')
            if ar.type == ARType.LOOP:
                return
            elif ar.type == ARType.FUNCTION:
                break
            ar = ar.outer
        self.error(node.position, ErrorInfo.invalid_syntax('continue'))

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
                except BaseError as e:
                    self.error(node.position, ErrorInfo.expr_value_error(e.message))
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
            try:
                result = func_val._func(args)
            except BaseError as e:
                self.error(node.position, ErrorInfo.general(e.message))

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
        except BaseError as e:
            self.error(node.cond.position, ErrorInfo.expr_value_error(e.message))
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
            except BaseError as e:
                self.error(node.position, ErrorInfo.expr_value_error(e.message))
            return result
        else:
            self.error(node.position, ErrorInfo.op_not_implemented(operator.value))

    def visit_UniOpExpr(self, node: UniOpExpr):
        expr = node.expr
        expr_value = self.visit(expr)

        if node.operator in UNIOP_IMPL_TABLE:
            try:
                result = UNIOP_IMPL_TABLE[node.operator](expr_value)
            except BaseError as e:
                self.error(node.position, ErrorInfo.expr_value_error(e.message))
            return result
        else:
            self.error(node.position, ErrorInfo.op_not_implemented(node.operator.value))

    def visit_Name(self, node: Name):
        return self.get_Name(node)

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

    def decl_Name(self, name: Name, value: Value, const: bool):
        ar = self.call_stack.current_ar
        identifier = name.identifier
        if ar.has(identifier):
            self.error(name.position, ErrorInfo.name_duplicate_declared(identifier))
        ar.set(identifier, value, const)

    def set_Name(self, name: Name, value: Value, force=False):
        '''set value to a name

        Args:
          force: set value to a constant forcibly
        '''
        ar = self.call_stack.current_ar
        identifier = name.identifier
        while ar is not None:
            if ar.has(identifier):
                _, const = ar.get(identifier)
                if const and not force:    # it's a constant
                    self.error(name.position, ErrorInfo.name_not_assignable(identifier))
                ar.set(identifier, value, const)
                return
            else:
                ar = ar.outer
        self.error(name.position, ErrorInfo.name_not_declared(identifier))

    def get_Name(self, name: Name):
        ar = self.call_stack.current_ar
        identifier = name.identifier
        while ar is not None:
            value, const = ar.get(identifier)
            if value is not None:
                return value
            else:
                ar = ar.outer
        self.error(name.position, ErrorInfo.name_not_declared(identifier))

    def set_Field(self, name: Name, field: Value, value: Value):
        pass

    def interpret(self, tree):
        self.visit(tree)

    def finish(self):
        toylog.debug('program finish')
        toylog.debug(self.call_stack)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='toylang interpreter')
    parser.add_argument('--src', help='source file')
    parser.add_argument('--repl', action='store_true', help='repl mode')
    parser.add_argument('--level', type=int, help='log level')
    args = parser.parse_args()

    if args.level:
        toylog.set_log_level(args.level)

    interpreter = Interpreter()

    if args.src:
        try:
            with open(args.src, 'r', encoding='utf-8') as f:
                code = f.read()

            lexer = Lexer(code)
            parser = Parser(lexer)
            tree = parser.parse()

            displayer = Displayer(tree, 'ast.html')
            displayer.display()

            interpreter.interpret(tree)
            interpreter.finish()
        except (LexerError, ParserError, SemanticError, InterpreterError) as e:
            print(e)
            interpreter.finish()
    # elif args.repl:
    else:
        text = ''
        while True:
            try:
                line = input('toy> ').strip()

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
