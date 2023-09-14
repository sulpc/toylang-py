# -*- coding: utf-8 -*-
"""
toylang parser
"""

from toytoken import *
from toyast import *
from toylexer import *
from toyerror import *
from toydisplayer import *


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

        # while self.current_token.type == TokenType.SEMI:
        #     self.eat(TokenType.SEMI)
        #     result.append(self.stat())
        while self.current_token.type not in (TokenType.RBRACE, TokenType.EOF):
            stat = self.stat()
            if type(stat) is not EmptyStat:
                result.append(stat)

        return result

    def stat(self):
        """parse stat

        stat : assign_stat
             | compoundassign_stat
             | block_stat
             | if_stat
             | switch_stat
             | repeat_stat
             | while_stat
             | forloop_stat
             | foreach_stat
             | break_stat
             | continue_stat
             | print_stat
             | empty_stat
        """
        if self.current_token.type == TokenType.IDENTIFIER:     # assign_stat | compoundassign_stat NOTE
            return self.identifier_prefix_stat()
        elif self.current_token.type == TokenType.LBRACE:       # { block_stat
            return self.block_stat()
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
        elif self.current_token.type == TokenType.PRINT:
            return self.print_stat()
        elif self.current_token.type == TokenType.SEMI:
            return self.empty_stat()
        else:
            self.error(self.current_token, ErrorInfo.invalid_statement(self.current_token.value))

    def identifier_prefix_stat(self):
        """parse identifier_prefix_stat: assign_stat | compoundassign_stat

        assign_stat         : var_list ASSIGN expr_list
        compoundassign_stat : var compoundassign expr
        """
        vars = self.var_list()
        assert(len(vars) != 0)

        if len(vars) == 1:
            # compoundassign_stat
            if self.current_token.type in (TokenType.SELF_ADD, TokenType.SELF_ADD,
                                           TokenType.SELF_SUB, TokenType.SELF_MUL,
                                           TokenType.SELF_DIV, TokenType.SELF_POW,
                                           TokenType.SELF_MOD, TokenType.SELF_BSHL,
                                           TokenType.SELF_BSHR, TokenType.SELF_BAND,
                                           TokenType.SELF_BXOR, TokenType.SELF_BOR):
                stat = CompoundAssignStat(op_type=self.current_token.type,
                                          var=vars[0],
                                          expr=None,
                                          position=self.current_token.position)
                self.eat(self.current_token.type)
                stat.expr = self.expr()
                return stat

        if self.current_token.type == TokenType.ASSIGN:
            stat = AssignStat(vars=vars,
                              exprs=None,
                              position=self.current_token.position)
            self.eat(TokenType.ASSIGN)
            stat.exprs = self.expr_list()
            return stat

        self.error(self.current_token, ErrorInfo.unexpected_token(self.current_token.value, 'assign or compoundassign'))

    def block_stat(self):
        """parse block_stat

        block_stat : LBRACE stat_list RBRACE
        """
        stat = BlockStat(stats=None, position=self.current_token.position)
        self.eat(TokenType.LBRACE)
        stat.stats = self.stat_list()
        self.eat(TokenType.RBRACE)
        return stat

    def if_stat(self):
        """parse if_stat

        if_stat : IF expr (COLON)? stat (ELIF expr (COLON)? stat)* (ELSE (COLON)? stat)?
        """
        stat = IfStat(conds=None, stats=None, position=self.current_token.position)

        self.eat(TokenType.IF)
        stat.conds = [self.expr()]
        if self.current_token.type == TokenType.COLON:
            self.eat(TokenType.COLON)
        stat.stats = [self.stat()]

        while self.current_token.type == TokenType.ELIF:
            self.eat(TokenType.ELIF)
            stat.conds.append(self.expr())
            if self.current_token.type == TokenType.COLON:
                self.eat(TokenType.COLON)
            stat.stats.append(self.stat())

        if self.current_token.type == TokenType.ELSE:
            stat.conds.append(Bool('true', self.current_token.position))    # make `else:` to `elif True`
            self.eat(TokenType.ELSE)
            if self.current_token.type == TokenType.COLON:
                self.eat(TokenType.COLON)
            stat.stats.append(self.stat())

        return stat

    def switch_stat(self):
        """parse switch_stat

        switch_stat : SWITCH expr (COLON)? (CASE expr (COLON)? stat)+ (DEFAULT (COLON)? stat)?
        """
        stat = SwitchStat(expr=None, cases=None, stats=None,
                          position=self.current_token.position)
        self.eat(TokenType.SWITCH)
        stat.expr = self.expr()
        if self.current_token.type == TokenType.COLON:
            self.eat(TokenType.COLON)
        stat.cases = []
        stat.stats = []

        if self.current_token.type != TokenType.CASE:
            self.error(self.current_token, ErrorInfo.unexpected_token(self.current_token.value, "case"))

        while self.current_token.type == TokenType.CASE:
            self.eat(TokenType.CASE)
            stat.cases.append(self.expr())
            if self.current_token.type == TokenType.COLON:
                self.eat(TokenType.COLON)
            stat.stats.append(self.stat())

        if self.current_token.type == TokenType.DEFAULT:
            self.eat(TokenType.DEFAULT)
            stat.cases.append(Bool('true', self.current_token.position))    # make `default:` to `case True`
            if self.current_token.type == TokenType.COLON:
                self.eat(TokenType.COLON)
            stat.stats.append(self.stat())

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
        stat = WhileStat(expr=None, stat=None, position=self.current_token.position)
        self.eat(TokenType.WHILE)
        stat.expr = self.expr()
        if self.current_token.type == TokenType.COLON:
            self.eat(TokenType.COLON)
        stat.stat = self.stat()
        return stat

    def for_prefix_stat(self):
        """parse forloop_stat | foreach_stat

        forloop_stat : FOR IDENTIFIER IS expr COMMA expr (COMMA expr)? (COLON)? stat
        foreach_stat : FOR IDENTIFIER (COMMA IDENTIFIER)? IN expr (COLON)? stat
        """
        position = self.current_token.position
        self.eat(TokenType.FOR)
        identifier = Identifier(self.current_token.value, self.current_token.position)
        self.eat(TokenType.IDENTIFIER)

        if self.current_token.type == TokenType.IS:
            return self.complete_forloop_stat(identifier, position)
        else:
            return self.complete_foreach_stat(identifier, position)

    def complete_forloop_stat(self, identifier, position):
        """complete forloop_stat

        forloop_stat : FOR IDENTIFIER IS expr COMMA expr (COMMA expr)? (COLON)? stat
        """
        stat = ForloopStat(identifier=identifier, start_expr=None, stop_expr=None, step_expr=None, stat=None,
                           position=position)

        self.eat(TokenType.IS)
        stat.start_expr = self.expr()
        self.eat(TokenType.COMMA)
        stat.stop_expr = self.expr()
        if self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            stat.step_expr = self.expr()
        if self.current_token.type == TokenType.COLON:
            self.eat(TokenType.COLON)
        stat.stat = self.stat()
        return stat

    def complete_foreach_stat(self, identifier, position):
        """parse foreach_stat

        foreach_stat : FOR IDENTIFIER (COMMA IDENTIFIER)? IN expr (COLON)? stat
        """
        stat = ForeachStat(key_id=identifier, value_id=None, expr=None, stat=None, position=position)

        if self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            stat.value_id = Identifier(self.current_token.value, self.current_token.position)
            self.eat(TokenType.IDENTIFIER)
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
        self.eat(TokenType.BREAK)
        return stat

    def print_stat(self):
        """parse print_stat

        print_stat : PRINT expr_list
        """
        stat = PrintStat(exprs=None,
                         position=self.current_token.position)
        self.eat(TokenType.PRINT)
        stat.exprs = self.expr_list()
        return stat

    def empty_stat(self):
        """parse empty_stat

        empty_stat : SEMI
        """
        self.eat(TokenType.SEMI)
        return EmptyStat()

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
            expr = BinOpExpr(op_type=TokenType.OR, left=expr, right=None,
                             position=self.current_token.position)
            self.eat(TokenType.OR)
            expr.right = self.logic_and_expr()
        return expr

    def logic_and_expr(self):
        """parse logic_and_expr

        logic_and_expr : check_in_expr (AND check_in_expr)*
        """
        expr = self.check_in_expr()
        while self.current_token.type == TokenType.AND:
            expr = BinOpExpr(op_type=TokenType.AND, left=expr, right=None,
                             position=self.current_token.position)
            self.eat(TokenType.AND)
            expr.right = self.check_in_expr()
        return expr

    def check_in_expr(self):
        """parse check_in_expr

        check_in_expr : relation_expr (IN relation_expr)*
        """
        expr = self.relation_expr()
        while self.current_token.type == TokenType.IN:
            expr = BinOpExpr(op_type=TokenType.IN, left=expr, right=None,
                             position=self.current_token.position)
            self.eat(TokenType.IN)
            expr.right = self.relation_expr()
        return expr

    def relation_expr(self):
        """parse relation_expr

        relation_expr : bit_or_expr ((EQ | NE | LT | LE | GT | GE) bit_or_expr)?
        """
        expr = self.bit_or_expr()
        if self.current_token.type in (TokenType.EQ, TokenType.NE,
                                       TokenType.LT, TokenType.LE,
                                       TokenType.GT, TokenType.GE):
            expr = BinOpExpr(op_type=self.current_token.type, left=expr, right=None,
                             position=self.current_token.position)
            self.eat(self.current_token.type)
            expr.right = self.bit_or_expr()
        return expr

    def bit_or_expr(self):
        """parse bit_or_expr

        bit_or_expr : bit_xor_expr (BOR bit_xor_expr)*
        """
        expr = self.bit_xor_expr()
        while self.current_token.type == TokenType.BOR:
            expr = BinOpExpr(op_type=TokenType.BOR, left=expr, right=None,
                             position=self.current_token.position)
            self.eat(TokenType.BOR)
            expr.right = self.bit_xor_expr()
        return expr

    def bit_xor_expr(self):
        """parse bit_xor_expr

        bit_xor_expr : bit_and_expr (BXOR bit_and_expr)*
        """
        expr = self.bit_and_expr()
        while self.current_token.type == TokenType.BXOR:
            expr = BinOpExpr(op_type=TokenType.BXOR, left=expr, right=None,
                             position=self.current_token.position)
            self.eat(TokenType.BXOR)
            expr.right = self.bit_and_expr()
        return expr

    def bit_and_expr(self):
        """parse bit_and_expr

        bit_and_expr : bit_shift_expr (BAND bit_shift_expr)*
        """
        expr = self.bit_shift_expr()
        while self.current_token.type == TokenType.BAND:
            expr = BinOpExpr(op_type=TokenType.BAND, left=expr, right=None,
                             position=self.current_token.position)
            self.eat(TokenType.BAND)
            expr.right = self.bit_shift_expr()
        return expr

    def bit_shift_expr(self):
        """parse bit_shift_expr

        bit_shift_expr : addition_expr ((BSHL | BSHR) addition_expr)*
        """
        expr = self.addition_expr()
        while self.current_token.type in (TokenType.BSHL, TokenType.BSHR):
            expr = BinOpExpr(op_type=self.current_token.type, left=expr, right=None,
                             position=self.current_token.position)
            self.eat(self.current_token.type)
            expr.right = self.addition_expr()
        return expr

    def addition_expr(self):
        """parse addition_expr

        addition_expr : multiple_expr ((ADD | SUB) multiple_expr)*
        """
        expr = self.multiple_expr()
        while self.current_token.type in (TokenType.ADD, TokenType.SUB):
            expr = BinOpExpr(op_type=self.current_token.type, left=expr, right=None,
                             position=self.current_token.position)
            self.eat(self.current_token.type)
            expr.right = self.multiple_expr()
        return expr

    def multiple_expr(self):
        """parse multiple_expr

        multiple_expr : unary_expr ((MUL | DIV | MOD) unary_expr)*
        """
        expr = self.unary_expr()
        while self.current_token.type in (TokenType.MUL, TokenType.DIV, TokenType.MOD):
            expr = BinOpExpr(op_type=self.current_token.type, left=expr, right=None,
                             position=self.current_token.position)
            self.eat(self.current_token.type)
            expr.right = self.unary_expr()
        return expr

    def unary_expr(self):
        """parse unary_expr

        unary_expr : (unop)* pow_expr
        """
        if self.current_token.type in (TokenType.ADD, TokenType.SUB, TokenType.NOT,
                                       TokenType.LEN, TokenType.BNOT):
            expr = UniOpExpr(op_type=self.current_token.type, expr=None,
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
            expr = BinOpExpr(op_type=self.current_token.type, left=expr, right=None,
                             position=self.current_token.position)
            self.eat(self.current_token.type)
            expr.right = self.primary_expr()
        return expr

    def primary_expr(self):
        """parse primary_expr

        primary_expr : INT_LITERAL | REAL_LITERAL | STRING_LITERAL | TRUE | FALSE | NULL | LPAREN expr RPAREN | var
        """
        if self.current_token.type in (TokenType.INT_LITERAL, TokenType.REAL_LITERAL):
            expr = Num(self.current_token.value, self.current_token.position)
            self.eat(self.current_token.type)
            return expr
        elif self.current_token.type == TokenType.STRING_LITERAL:
            expr = String(self.current_token.value, self.current_token.position)
            self.eat(self.current_token.type)
            return expr
        elif self.current_token.type in (TokenType.TRUE, TokenType.FALSE):
            expr = Bool(self.current_token.value, self.current_token.position)
            self.eat(self.current_token.type)
            return expr
        elif self.current_token.type == TokenType.NULL:
            expr = Null(self.current_token.position)
            self.eat(self.current_token.type)
            return expr
        elif self.current_token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            expr = self.expr()
            self.eat(TokenType.RPAREN)
            return expr
        else:
            return self.var()

    def var_list(self):
        """parse var_list

        var_list : var (COMMA var)*
        """
        vars = [self.var()]
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            vars.append(self.var())
        return vars

    def var(self):
        """parse var

        var : IDENTIFIER
        """
        var = Identifier(self.current_token.value, self.current_token.position)
        self.eat(TokenType.IDENTIFIER)
        return var

    def expr_list(self):
        """parse expr_list

        expr_list : expr (COMMA expr)*
        """
        exprs = [self.expr()]
        while self.current_token.type == TokenType.COMMA:
            self.eat(TokenType.COMMA)
            exprs.append(self.expr())
        return exprs

    def parse(self):
        result = self.program()
        if self.current_token.type != TokenType.EOF:
            self.error(self.current_token, ErrorInfo.unexpected_token(self.current_token, 'EOF'))
        return result


if __name__ == '__main__':
    code = '''
    x,y,z,t = 1,true,'hello, world', null
    // x = y + ------1
    print x,y

    if x < 0:   ;
    elif x < 5:    print "x > 0"
    elif x < 10 {
        print "x < 10"
        x = 10
    }
    else {print "x >=10"; x=20;}


    for i is 1,10,1:
        print i*2

    i = 0;
    while i < 10 {
        print i*2
        i += 1
    }

    i = 0;
    repeat {
        print i*2;
        i += 1;
    } until i >= 10;
    

    for k,v in map {
        print k,v
    }

    ;
    '''
    try:
        lexer = Lexer(code)
        parser = Parser(lexer)
        tree = parser.parse()

        displayer = Displayer(tree)
        displayer.display()
    except (LexerError, ParserError) as e:
        print(e)
