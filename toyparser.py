# -*- coding: utf-8 -*-
"""
toylang parser
"""
from toytoken import *
from toyerror import *
from toylexer import *
from toyast import *
from toydisplayer import *
import sys

class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.current_token = self.lexer.next_token()

    def error(self, token: Token, message):
        raise ParserError(token.position, message)

    def eat(self, token_type):
        """verify the token type
        """
        if self.current_token.type == token_type:
            self.current_token = self.lexer.next_token()
        else:
            self.error(self.current_token, f'expect {token_type}')

    def program(self):
        """parse program

        program : stat_list
        """
        return Program(stats=self.stat_list())

    def stat_list(self):
        """parse stat_list

        stat_list : (stat)+
        """
        result = []
        while self.current_token.type not in (TokenType.RBRACE, TokenType.EOF):
            stat = self.stat()
            if type(stat) is not EmptyStat:
                result.append(stat)
        return result

    def stat(self):
        """parse stat

        stat : empty_stat
             | block_stat
             | var_decl_stat
             | if_stat
             | switch_stat
             | repeat_stat
             | while_stat
             | forloop_stat
             | foreach_stat
             | break_stat
             | continue_stat
             | func_decl_stat
             | return_stat
             | assign_stat
             | compoundassign_stat
             | func_call_stat
        """
        if self.current_token.type == TokenType.SEMI:
            return self.empty_stat()
        elif self.current_token.type == TokenType.LBRACE:       # { block_stat
            return self.block_stat()
        elif self.current_token.type in (TokenType.VAR, TokenType.CONST):
            return self.var_decl_stat()
        elif self.current_token.type == TokenType.IF:
            return self.if_stat()
        elif self.current_token.type == TokenType.SWITCH:
            return self.switch_stat()
        elif self.current_token.type == TokenType.REPEAT:
            return self.repeat_stat()
        elif self.current_token.type == TokenType.WHILE:
            return self.while_stat()
        elif self.current_token.type == TokenType.FOR:          # forloop_stat | foreach_stat
            return self.for_prefix_stat()
        elif self.current_token.type == TokenType.BREAK:
            return self.break_stat()
        elif self.current_token.type == TokenType.CONTINUE:
            return self.continue_stat()
        elif self.current_token.type == TokenType.FUNC:
            return self.func_prefix_stat()
        elif self.current_token.type == TokenType.RETURN:
            return self.return_stat()
        else:                                                   # IDENTIFIER
            return self.identifier_prefix_stat()

    def empty_stat(self):
        """parse empty_stat

        empty_stat : SEMI
        """
        self.eat(TokenType.SEMI)
        return EmptyStat()

    def block_stat(self):
        """parse block_stat

        block_stat : LBRACE stat_list RBRACE
        """
        stat = BlockStat(stats=None,
                         position=self.current_token.position)
        self.eat(TokenType.LBRACE)
        stat.stats = self.stat_list()
        self.eat(TokenType.RBRACE)
        return stat

    def var_decl_stat(self):
        """parse var_decl_stat

        var_decl_stat : (VAR | CONST) name_list (ASSIGN expr_list)?
        """
        const = True if self.current_token.type == TokenType.CONST else False
        stat = VarDeclStat(names=None, exprs=None, const=const,
                           position=self.current_token.position)
        self.eat(self.current_token.type)               # VAR or CONST
        stat.names = self.name_list()
        if self.current_token.type == TokenType.ASSIGN:
            self.eat(TokenType.ASSIGN)
            stat.exprs = self.expr_list()
        return stat

    def if_stat(self):
        """parse if_stat

        if_stat : IF expr (COLON)? stat (ELIF expr (COLON)? stat)* (ELSE (COLON)? stat)?
        """
        stat = IfStat(cond_exprs=[], stats=[],
                      position=self.current_token.position)

        self.eat(TokenType.IF)
        stat.cond_exprs.append(self.expr())
        if self.current_token.type == TokenType.COLON:
            self.eat(TokenType.COLON)
        stat.stats.append(self.stat())

        while self.current_token.type == TokenType.ELIF:
            self.eat(TokenType.ELIF)
            stat.cond_exprs.append(self.expr())
            if self.current_token.type == TokenType.COLON:
                self.eat(TokenType.COLON)
            stat.stats.append(self.stat())

        if self.current_token.type == TokenType.ELSE:
            stat.cond_exprs.append(BoolLiteral('true', self.current_token.position))    # make `else:` to `elif True`
            self.eat(TokenType.ELSE)
            if self.current_token.type == TokenType.COLON:
                self.eat(TokenType.COLON)
            stat.stats.append(self.stat())

        return stat

    def switch_stat(self):
        """parse switch_stat

        switch_stat : SWITCH expr (COLON)? (CASE expr (COLON)? stat)+ (DEFAULT (COLON)? stat)?
        """
        stat = SwitchStat(expr=None, case_exprs=[], case_stats=[], default_stat=None,
                          position=self.current_token.position)
        self.eat(TokenType.SWITCH)
        stat.expr = self.expr()
        if self.current_token.type == TokenType.COLON:
            self.eat(TokenType.COLON)

        if self.current_token.type != TokenType.CASE:
            self.error(self.current_token, ErrorInfo.unexpected_token(self.current_token.value, "case"))

        while self.current_token.type == TokenType.CASE:
            self.eat(TokenType.CASE)
            stat.case_exprs.append(self.expr())
            if self.current_token.type == TokenType.COLON:
                self.eat(TokenType.COLON)
            stat.case_stats.append(self.stat())

        if self.current_token.type == TokenType.DEFAULT:
            self.eat(TokenType.DEFAULT)
            if self.current_token.type == TokenType.COLON:
                self.eat(TokenType.COLON)
            stat.default_stat = self.stat()
        return stat

    def repeat_stat(self):
        """parse repeat_stat

        repeat_stat : REPEAT (COLON)? stat UNTIL expr
        """
        stat = RepeatStat(stat=None, expr=None,
                          position=self.current_token.position)
        self.eat(TokenType.REPEAT)
        if self.current_token.type == TokenType.COLON:
            self.eat(TokenType.COLON)
        stat.stat = self.stat()

        self.eat(TokenType.UNTIL)
        stat.expr = self.expr()
        return stat

    def while_stat(self):
        """parse while_stat

        while_stat : WHILE expr (COLON)? stat
        """
        stat = WhileStat(expr=None, stat=None,
                         position=self.current_token.position)
        self.eat(TokenType.WHILE)
        stat.expr = self.expr()
        if self.current_token.type == TokenType.COLON:
            self.eat(TokenType.COLON)
        stat.stat = self.stat()
        return stat

    def for_prefix_stat(self):
        """parse forloop_stat | foreach_stat

        forloop_stat : FOR name IS expr COMMA expr (COMMA expr)? (COLON)? stat
        foreach_stat : FOR name (COMMA name)? IN expr (COLON)? stat
        """
        position = self.current_token.position
        self.eat(TokenType.FOR)
        name = self.name()

        if self.current_token.type == TokenType.IS:
            return self.complete_forloop_stat(name, position)
        else:
            return self.complete_foreach_stat(name, position)

    def complete_forloop_stat(self, name, position):
        """complete forloop_stat

        forloop_stat : FOR name IS expr COMMA expr (COMMA expr)? (COLON)? stat
        """
        stat = ForloopStat(var_name=name, start_expr=None, end_expr=None, step_expr=None, stat=None,
                           position=position)

        self.eat(TokenType.IS)
        stat.start_expr = self.expr()
        self.eat(TokenType.COMMA)
        stat.end_expr = self.expr()
        if self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            stat.step_expr = self.expr()
        if self.current_token.type == TokenType.COLON:
            self.eat(TokenType.COLON)
        stat.stat = self.stat()
        return stat

    def complete_foreach_stat(self, name, position):
        """parse foreach_stat

        foreach_stat : FOR name (COMMA name)? IN expr (COLON)? stat
        """
        stat = ForeachStat(key_name=name, val_name=None, expr=None, stat=None,
                           position=position)

        if self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            stat.val_name = self.name()
        self.eat(TokenType.IN)

        stat.expr = self.expr()
        if self.current_token.type == TokenType.COLON:
            self.eat(TokenType.COLON)
        stat.stat = self.stat()
        return stat

    def break_stat(self):
        """parse break_stat

        break_stat : BREAK
        """
        stat = BreakStat(position=self.current_token.position)
        self.eat(TokenType.BREAK)
        return stat

    def continue_stat(self):
        """parse continue_stat

        continue_stat : CONTINUE
        """
        stat = ContinueStat(position=self.current_token.position)
        self.eat(TokenType.CONTINUE)
        return stat

    def func_prefix_stat(self):
        """parse func_prefix_stat:

        func_decl_stat: FUNC name func_def  => CONST name = FUNC func_def
        func_call_stat: func_call
        func_call     : func_def_expr LPAREN (expr_list)? RPAREN
        func_def_expr : FUNC func_def
        """
        self.eat(TokenType.FUNC)
        if self.current_token.type == TokenType.IDENTIFIER:
            # func decl is convert to const var decl
            name = self.name()
            func_def = self.func_def()
            stat = VarDeclStat(names=[name], exprs=[func_def], const=True,
                               position=self.current_token.position)
        else:
            func = self.func_def()
            stat = self.complete_func_call(func)
        return stat

    def return_stat(self):
        """parse return_stat

        return_stat : RETURN (expr | SEMI)
        """
        stat = ReturnStat(expr=None, position=self.current_token.position)
        self.eat(TokenType.RETURN)
        if self.current_token.type == TokenType.SEMI:
            self.eat(TokenType.SEMI)
        else:
            stat.expr = self.expr()
        return stat

    def identifier_prefix_stat(self):
        """parse identifier_prefix_stat

        assign_stat         : lvalue_expr (COMMA lvalue_expr)* ASSIGN expr_list
        compoundassign_stat : lvalue_expr compoundassign expr
        func_call_stat      : func_call
        func_call           : lvalue_expr LPAREN (expr_list)? RPAREN
        """
        lve = self.lvalue_expr()
        if self.current_token.type in (TokenType.COMMA, TokenType.ASSIGN):
            return self.complete_assign_stat(lve)
        elif self.current_token.type == TokenType.LPAREN:
            return self.complete_func_call(lve)
        else:
            return self.complete_compoundassign_stat(lve)

    def complete_assign_stat(self, lvalue_expr):
        """complete assign_stat

        assign_stat : lvalue_expr (COMMA lvalue_expr)* ASSIGN expr_list
        """
        lexprs = [lvalue_expr]
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            lexprs.append(self.lvalue_expr())

        stat = AssignStat(left_exprs=lexprs, right_exprs=None,
                          position=self.current_token.position)
        self.eat(TokenType.ASSIGN)

        stat.right_exprs = self.expr_list()
        return stat

    def complete_compoundassign_stat(self, lvalue_expr):
        """complete compoundassign_stat

        compoundassign_stat : lvalue_expr compoundassign expr
        """
        if self.current_token.type in (TokenType.SELF_ADD, TokenType.SELF_ADD,
                                       TokenType.SELF_SUB, TokenType.SELF_MUL,
                                       TokenType.SELF_DIV, TokenType.SELF_POW,
                                       TokenType.SELF_MOD, TokenType.SELF_BSHL,
                                       TokenType.SELF_BSHR, TokenType.SELF_BAND,
                                       TokenType.SELF_BXOR, TokenType.SELF_BOR):
            stat = CompoundAssignStat(operator=self.current_token.type,
                                      left_expr=lvalue_expr,
                                      right_expr=None,
                                      position=self.current_token.position)
            self.eat(self.current_token.type)
            stat.right_expr = self.expr()
            return stat
        else:
            self.error(self.current_token, ErrorInfo.unexpected_token(self.current_token.value, 'compoundassign'))

    def complete_func_call(self, func):
        """complete func_call

        func_call : lvalue_expr   LPAREN (expr_list)? RPAREN
                  | func_def_expr LPAREN (expr_list)? RPAREN
        """
        call = FuncCall(func_expr=func, arg_exprs=None, position=self.current_token.position)
        self.eat(TokenType.LPAREN)
        if self.current_token.type != TokenType.RPAREN:
            call.arg_exprs = self.expr_list()
        self.eat(TokenType.RPAREN)
        return call

    def expr(self):
        """parse expr

        expr : select_expr
        """
        return self.select_expr()

    def select_expr(self):
        """parse select_expr

        select_expr : logic_or_expr (QUERY expr COLON expr)?
        """

        lor_expr = self.logic_or_expr()
        if self.current_token.type != TokenType.QUERY:
            return lor_expr

        s_expr = SelectExpr(cond=lor_expr, expr1=None, expr2=None,
                            position=self.current_token.position)
        self.eat(TokenType.QUERY)
        s_expr.expr1 = self.expr()
        self.eat(TokenType.COLON)
        s_expr.expr2 = self.expr()
        return s_expr

    def logic_or_expr(self):
        """parse logic_or_expr

        logic_or_expr : logic_and_expr (OR logic_and_expr)*
        """
        expr = self.logic_and_expr()
        while self.current_token.type == TokenType.OR:
            expr = BinOpExpr(operator=TokenType.OR, left_expr=expr, right_expr=None,
                             position=self.current_token.position)
            self.eat(TokenType.OR)
            expr.right_expr = self.logic_and_expr()
        return expr

    def logic_and_expr(self):
        """parse logic_and_expr

        logic_and_expr : check_expr (AND check_expr)*
        """
        expr = self.check_expr()
        while self.current_token.type == TokenType.AND:
            expr = BinOpExpr(operator=TokenType.AND, left_expr=expr, right_expr=None,
                             position=self.current_token.position)
            self.eat(TokenType.AND)
            expr.right_expr = self.check_expr()
        return expr

    def check_expr(self):
        """parse check_expr

        check_expr : relation_expr ((IN | IS) relation_expr)*
        """
        expr = self.relation_expr()
        while self.current_token.type in (TokenType.IN, TokenType.IS):
            expr = BinOpExpr(operator=self.current_token.type, left_expr=expr, right_expr=None,
                             position=self.current_token.position)
            self.eat(self.current_token.type)
            expr.right_expr = self.relation_expr()
        return expr

    def relation_expr(self):
        """parse relation_expr

        relation_expr : bit_or_expr ((EQ | NE | LT | LE | GT | GE) bit_or_expr)?
        """
        expr = self.bit_or_expr()
        if self.current_token.type in (TokenType.EQ, TokenType.NE,
                                       TokenType.LT, TokenType.LE,
                                       TokenType.GT, TokenType.GE):
            expr = BinOpExpr(operator=self.current_token.type, left_expr=expr, right_expr=None,
                             position=self.current_token.position)
            self.eat(self.current_token.type)
            expr.right_expr = self.bit_or_expr()
        return expr

    def bit_or_expr(self):
        """parse bit_or_expr

        bit_or_expr : bit_xor_expr (BOR bit_xor_expr)*
        """
        expr = self.bit_xor_expr()
        while self.current_token.type == TokenType.BOR:
            expr = BinOpExpr(operator=TokenType.BOR, left_expr=expr, right_expr=None,
                             position=self.current_token.position)
            self.eat(TokenType.BOR)
            expr.right_expr = self.bit_xor_expr()
        return expr

    def bit_xor_expr(self):
        """parse bit_xor_expr

        bit_xor_expr : bit_and_expr (BXOR bit_and_expr)*
        """
        expr = self.bit_and_expr()
        while self.current_token.type == TokenType.BXOR:
            expr = BinOpExpr(operator=TokenType.BXOR, left_expr=expr, right_expr=None,
                             position=self.current_token.position)
            self.eat(TokenType.BXOR)
            expr.right_expr = self.bit_and_expr()
        return expr

    def bit_and_expr(self):
        """parse bit_and_expr

        bit_and_expr : bit_shift_expr (BAND bit_shift_expr)*
        """
        expr = self.bit_shift_expr()
        while self.current_token.type == TokenType.BAND:
            expr = BinOpExpr(operator=TokenType.BAND, left_expr=expr, right_expr=None,
                             position=self.current_token.position)
            self.eat(TokenType.BAND)
            expr.right_expr = self.bit_shift_expr()
        return expr

    def bit_shift_expr(self):
        """parse bit_shift_expr

        bit_shift_expr : addition_expr ((BSHL | BSHR) addition_expr)*
        """
        expr = self.addition_expr()
        while self.current_token.type in (TokenType.BSHL, TokenType.BSHR):
            expr = BinOpExpr(operator=self.current_token.type, left_expr=expr, right_expr=None,
                             position=self.current_token.position)
            self.eat(self.current_token.type)
            expr.right_expr = self.addition_expr()
        return expr

    def addition_expr(self):
        """parse addition_expr

        addition_expr : multiple_expr ((ADD | SUB) multiple_expr)*
        """
        expr = self.multiple_expr()
        while self.current_token.type in (TokenType.ADD, TokenType.SUB):
            expr = BinOpExpr(operator=self.current_token.type, left_expr=expr, right_expr=None,
                             position=self.current_token.position)
            self.eat(self.current_token.type)
            expr.right_expr = self.multiple_expr()
        return expr

    def multiple_expr(self):
        """parse multiple_expr

        multiple_expr : unary_expr ((MUL | DIV | MOD) unary_expr)*
        """
        expr = self.unary_expr()
        while self.current_token.type in (TokenType.MUL, TokenType.DIV, TokenType.MOD):
            expr = BinOpExpr(operator=self.current_token.type, left_expr=expr, right_expr=None,
                             position=self.current_token.position)
            self.eat(self.current_token.type)
            expr.right_expr = self.unary_expr()
        return expr

    def unary_expr(self):
        """parse unary_expr

        unary_expr : (unop)* pow_expr
        """
        if self.current_token.type in (TokenType.ADD, TokenType.SUB, TokenType.NOT,
                                       TokenType.LEN, TokenType.BNOT):
            expr = UniOpExpr(operator=self.current_token.type, expr=None,
                             position=self.current_token.position)
            self.eat(self.current_token.type)
            expr.expr = self.unary_expr()
            return expr

        return self.pow_expr()

    def pow_expr(self):
        """parse pow_expr

        pow_expr : primary_expr (POW primary_expr)*
        """
        expr = self.primary_expr()
        while self.current_token.type == TokenType.POW:
            expr = BinOpExpr(operator=self.current_token.type, left_expr=expr, right_expr=None,
                             position=self.current_token.position)
            self.eat(self.current_token.type)
            expr.right_expr = self.primary_expr()
        return expr

    def primary_expr(self):
        """parse primary_expr

        primary_expr  : INT_LITERAL | FLOAT_LITERAL | STRING_LITERAL | TRUE | FALSE | NULL | LPAREN expr RPAREN
                      | list_ctor_expr | map_ctor_expr | set_ctor_expr | func_def_expr |
                      | lvalue_expr | func_call_expr
        func_def_expr : FUNC func_def
        """
        if self.current_token.type == TokenType.INT_LITERAL:
            expr = NumLiteral(self.current_token.value, is_int=True,
                              position=self.current_token.position)
            self.eat(self.current_token.type)
            return expr
        elif self.current_token.type == TokenType.FLOAT_LITERAL:
            expr = NumLiteral(self.current_token.value, is_int=False,
                              position=self.current_token.position)
            self.eat(self.current_token.type)
            return expr
        elif self.current_token.type == TokenType.STRING_LITERAL:
            expr = StringLiteral(self.current_token.value, self.current_token.position)
            self.eat(self.current_token.type)
            return expr
        elif self.current_token.type in (TokenType.TRUE, TokenType.FALSE):
            expr = BoolLiteral(self.current_token.value, self.current_token.position)
            self.eat(self.current_token.type)
            return expr
        elif self.current_token.type == TokenType.NULL:
            expr = NullLiteral(self.current_token.position)
            self.eat(self.current_token.type)
            return expr
        elif self.current_token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            expr = self.expr()
            self.eat(TokenType.RPAREN)
            return expr
        elif self.current_token.type == TokenType.LBRACK:
            expr = self.list_ctor_expr()
            return expr
        elif self.current_token.type == TokenType.LBRACE:       # map set
            expr = self.map_set_ctor_expr()
            return expr
        elif self.current_token.type == TokenType.FUNC:
            self.eat(TokenType.FUNC)
            expr = self.func_def()
            if self.current_token.type == TokenType.LPAREN:
                expr = self.complete_func_call(expr)
            return expr
        else:               # identifier
            if self.current_token.type != TokenType.IDENTIFIER:
                self.error(self.current_token, ErrorInfo.unexpected_token(self.current_token.value, 'IDENTIFIER'))
            expr = self.lvalue_expr()
            if self.current_token.type == TokenType.LPAREN:     # expr()
                return self.complete_func_call(expr)
            return expr

    def list_ctor_expr(self):
        """parse list_ctor_expr

        list_ctor_expr : LBRACK (expr_list)? RBRACK
        """
        expr = ListCtorExpr(exprs=None, position=self.current_token.position)
        self.eat(TokenType.LBRACK)
        if self.current_token.type != TokenType.RBRACK:
            expr.exprs = self.expr_list()
        self.eat(TokenType.RBRACK)
        return expr

    def map_set_ctor_expr(self):
        """parse map_ctor_expr | set_ctor_expr

        map_ctor_expr : LBRACE (expr COLON expr (COMMA expr COLON expr)*)? RBRACE
        set_ctor_expr : LBRACE expr (COMMA expr)* RBRACE
        """
        position = self.current_token.position
        self.eat(TokenType.LBRACE)
        key_exprs=[]
        value_exprs=[]
        is_set = False          # default `{}` trait as map
        if self.current_token.type != TokenType.RBRACE:
            # determine map or set based on the first pair
            key_exprs.append(self.expr())
            if self.current_token.type == TokenType.COLON:
                is_set = False
                self.eat(TokenType.COLON)
                value_exprs.append(self.expr())
            else:
                is_set = True
            # parse remaining content
            while self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                key_exprs.append(self.expr())
                if is_set:              # set
                    # do nothing
                    pass
                else:                   # map
                    self.eat(TokenType.COLON)
                    value_exprs.append(self.expr())
        self.eat(TokenType.RBRACE)
        if is_set:
            expr = SetCtorExpr(key_exprs, position)
        else:
            expr = MapCtorExpr(key_exprs, value_exprs, position)
        return expr

    def lvalue_expr(self):
        """parse lvalue_expr

        lvalue_expr : name | lvalue_expr LBRACK expr RBRACK | lvalue_expr DOT name
        """
        lve = self.name()
        while self.current_token.type in (TokenType.LBRACK, TokenType.DOT):
            lve = AccessExpr(expr=lve, field_expr=None, dot=False if self.current_token.type == TokenType.DOT else False,
                             position=self.current_token.position)
            if self.current_token.type == TokenType.LBRACK:
                self.eat(TokenType.LBRACK)
                lve.dot = False
                lve.field_expr = self.expr()
                self.eat(TokenType.RBRACK)
            else:
                self.eat(TokenType.DOT)
                lve.dot = True
                lve.field_expr = StringLiteral(self.current_token.value, self.current_token.position)
                self.eat(TokenType.IDENTIFIER)
        return lve

    def name_list(self):
        """parse name_list

        name_list : name (COMMA name)*
        """
        names = [self.name()]
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            names.append(self.name())
        return names

    def expr_list(self):
        """parse expr_list

        expr_list : expr (COMMA expr)*
        """
        exprs = [self.expr()]
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            exprs.append(self.expr())
        return exprs

    def func_def(self):
        """parse func_def

        func_def   : LPAREN (param_list)? RPAREN LBRACE stat_list RBRACE
        param_list : name_list (COMMA VARARG)? | VARARG
        """
        func = FuncDef(param_names=None, vararg=False, body=None,
                       position=self.current_token.position)
        # func
        self.eat(TokenType.LPAREN)
        if self.current_token.type != TokenType.RPAREN:
            if self.current_token.type != TokenType.VARARG:
                func.param_names = self.name_list()

            # NOTE: bug, conflict to parse `, ...` and `, name`
            # if self.current_token.type == TokenType.COMMA:   
            #     self.eat(TokenType.COMMA)
            # if self.current_token.type == TokenType.VARARG:
            #     self.eat(TokenType.VARARG)
            #     func.vararg = True
        self.eat(TokenType.RPAREN)
        # func body
        self.eat(TokenType.LBRACE)
        func.body = self.stat_list()
        self.eat(TokenType.RBRACE)
        return func

    def name(self):
        """parse name

        name : IDENTIFIER
        """
        name = Name(self.current_token.value, self.current_token.position)
        self.eat(TokenType.IDENTIFIER)
        return name

    def parse(self):
        result = self.program()
        if self.current_token.type != TokenType.EOF:
            self.error(self.current_token, ErrorInfo.unexpected_token(self.current_token, 'EOF'))
        return result


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
    except (LexerError, ParserError) as e:
        print(e)
